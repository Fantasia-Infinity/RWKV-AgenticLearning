"""Convert GSM8K solutions into multi-turn calc-tool SFT trajectories (CPU).

GSM8K answers contain inline arithmetic annotations::

    Natalia sold 48/2 = <<48/2=24>>24 clips in May.

Each `<<expr=result>>` marker is a natural anchor for one calculator tool call:

    assistant: <think>Natalia sold </think>
               **Tool Call:** ```json {"name":"calc","arguments":{"expression":"48/2"}}```
    tool:      {"result": 24}
    assistant: <think>24 clips in May. Natalia sold </think>
               **Tool Call:** ...
    ...
    assistant: <think>... </think>
               #### 72

Only markers whose expression is pure arithmetic AND whose evaluation matches
the claimed value are converted (measured: 23,716/23,716 on GSM8K train).
Everything else is left as prose.

Output: pretokenized parquet compatible with the SFT trainer
(uuid / question_id / input_ids / loss_mask) plus raw JSONL and stats.

Usage:
    python tools/convert_gsm8k_calc_sft.py --out-dir $SCRATCH/data/sft-gsm8k-calc
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent / "gen_sft_traj"))
from render import Renderer, parse_tool_calls  # noqa: E402

DEFAULT_INPUT = "/scratch-shared/szhang4/rwkv-agentic/data/gsm8k"
FINAL_RE = re.compile(r"####\s*([\-+]?[0-9][0-9.,]*(?:[eE][\-+]?[0-9]+)?)")
MARKER_RE = re.compile(r"<<([^<>]+?)=([^<>]+?)>>")
PURE_ARITH_RE = re.compile(r"[\d\s.+\-*/()]+")

SYSTEM = (
    "You are an RWKV agent. If the task requires an arithmetic calculation, "
    "call the calc tool. For non-arithmetic questions, answer directly without tools. "
    "When you call a tool, write exactly one fenced JSON tool call. Do not invent tool outputs."
)
USER_SUFFIX = (
    "\nUse the calc tool for arithmetic calculations. "
    "Put the final numeric answer after '####'."
)
TOOL_CALC = {
    "type": "function",
    "function": {
        "name": "calc",
        "description": "Evaluate an arithmetic expression.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
}


def safe_eval(expr: str) -> float:
    allowed = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)
    tree = ast.parse(expr, mode="eval")

    def walk(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            v = walk(node.operand)
            return v if isinstance(node.op, ast.UAdd) else -v
        if isinstance(node, ast.BinOp) and isinstance(node.op, allowed):
            l, r = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(r) > 100:
                raise ValueError("exponent too large")
            return {
                ast.Add: lambda: l + r, ast.Sub: lambda: l - r,
                ast.Mult: lambda: l * r, ast.Div: lambda: l / r,
                ast.FloorDiv: lambda: l // r, ast.Mod: lambda: l % r,
                ast.Pow: lambda: l**r,
            }[type(node.op)]()
        raise ValueError(f"unsupported node {type(node).__name__}")

    return walk(tree.body)


def norm_number(text: str):
    s = text.strip().strip("$").replace(",", "").replace(" ", "")
    try:
        f = float(s)
    except ValueError:
        return s
    return int(f) if f.is_integer() else f


def split_answer(answer: str):
    """Yield ('text', s) / ('marker', lhs, rhs) tokens in order."""
    pos = 0
    for m in MARKER_RE.finditer(answer):
        if m.start() > pos:
            yield ("text", answer[pos:m.start()])
        yield ("marker", m.group(1).strip(), m.group(2).strip())
        pos = m.end()
    if pos < len(answer):
        yield ("text", answer[pos:])


def convert_one(question: str, answer: str):
    final = FINAL_RE.findall(answer)
    if not final:
        return None
    gt = norm_number(final[-1])
    toks = list(split_answer(answer))
    markers = [(i, t) for i, t in enumerate(toks) if t[0] == "marker"]
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question + USER_SUFFIX},
    ]
    n_conv = 0
    i = 0
    toks_local = list(toks)
    while i < len(toks_local):
        kind = toks_local[i][0]
        if kind == "text":
            i += 1
            continue
        _, lhs, rhs = toks_local[i]
        ok = bool(PURE_ARITH_RE.fullmatch(lhs))
        if ok:
            try:
                val = safe_eval(lhs)
                ok = abs(val - float(rhs.replace(",", ""))) <= 1e-6 * max(1.0, abs(float(rhs.replace(",", ""))))
            except Exception:
                ok = False
        if not ok:
            # leave the annotation as prose
            toks_local[i] = ("text", rhs)
            i += 1
            continue
        # think text: preceding text with trailing '=' stripped
        j = i - 1
        think = ""
        while j >= 0 and j >= i - 1:
            if toks_local[j][0] == "text":
                think = toks_local[j][1].strip()
                while think.endswith("="):
                    think = think[:-1].rstrip()
                toks_local[j] = ("text", "")  # consumed
            j -= 1
        messages.append({
            "role": "assistant",
            "content": f"<think>{think}</think>",
            "tool_calls": [{"function": {"name": "calc", "arguments": {"expression": lhs}}}],
        })
        messages.append({"role": "tool", "content": {"result": norm_number(rhs)}})
        n_conv += 1
        i += 1
    # final assistant: remaining text minus the '####' line + final answer
    tail = "".join(t[1] for t in toks_local if t[0] == "text")
    tail = FINAL_RE.sub("", tail).strip()
    tail = re.sub(r"\[/?(think)\]?", "", tail).strip()
    messages.append({"role": "assistant", "content": f"<think>{tail}</think>\n#### {gt}" if tail else f"<think>Answer computed.</think>\n#### {gt}"})
    return messages, gt, n_conv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default=DEFAULT_INPUT)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--model", default="/scratch-shared/szhang2/rwkv-agentic/weights/g1l-1.5b-hf")
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--eval-size", type=int, default=256)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir)
    renderer = Renderer(args.model, max_len=args.max_len)

    eos_id = renderer.eos

    def tokenize_with_turn_eos(messages):
        """Tokenize a multi-turn conversation, inserting EOS at each assistant turn end.

        During RL rollouts the model must emit EOS after a tool call so that the
        environment can append the observation.  The stock chat template only puts
        EOS at the very end of the sequence, which teaches the model to keep
        generating fake tool outputs inside one turn.  We therefore build ids
        segment by segment and append EOS after every assistant message.
        """
        full = renderer.render(messages, [TOOL_CALC], add_generation_prompt=False)
        spans = []
        for i, msg in enumerate(messages):
            if msg["role"] != "assistant":
                continue
            prefix = renderer.render(messages[:i], [TOOL_CALC], add_generation_prompt=True)
            upto = renderer.render(messages[: i + 1], [TOOL_CALC], add_generation_prompt=False)
            if not upto.startswith(prefix):
                raise RuntimeError(f"template prefix mismatch at {i}")
            spans.append((len(prefix), len(upto)))
        bounds = sorted({0, len(full)} | {s for s, _ in spans} | {e for _, e in spans})
        off_map = {off: len(renderer.encode(full[:off])) for off in bounds}
        full_ids = renderer.encode(full)
        ids, mask = [], []
        for a, b in zip(bounds[:-1], bounds[1:]):
            ta, tb = off_map[a], off_map[b]
            seg = full_ids[ta:tb]
            is_assistant = any(a == s for s, _ in spans)
            ids.extend(seg)
            mask.extend([1 if is_assistant else 0] * len(seg))
            if is_assistant:
                ids.append(eos_id)
                mask.append(1)
        return ids, mask

    def build_rows(rows):
        kept, stats = [], {"rows": 0, "converted": 0, "render_fail": 0, "too_long": 0, "tool_calls": 0, "no_marker": 0}
        for idx, row in enumerate(rows):
            info = row["extra_info"]
            q, a = info["question"], info["answer"]
            conv = convert_one(q, a)
            if conv is None:
                continue
            messages, gt, n_conv = conv
            stats["rows"] += 1
            if n_conv == 0:
                stats["no_marker"] += 1
            stats["tool_calls"] += n_conv
            try:
                ids, mask = tokenize_with_turn_eos(messages)
            except Exception:
                stats["render_fail"] += 1
                continue
            if len(ids) > args.max_len:
                stats["too_long"] += 1
                continue
            stats["converted"] += 1
            kept.append({
                "uuid": hashlib.sha256(f"{q}::{idx}".encode()).hexdigest()[:16],
                "question_id": hashlib.sha256(q.encode()).hexdigest()[:16],
                "input_ids": ids,
                "loss_mask": mask,
                "meta": {"n_tool_calls": n_conv, "gt": str(gt)},
            })
        return kept, stats

    train_rows, train_stats = build_rows(pq.read_table(in_dir / "train.parquet").to_pylist())
    test_rows_all, test_stats = build_rows(pq.read_table(in_dir / "validation.parquet").to_pylist())
    import random
    rng = random.Random(args.seed)
    test_rows = list(test_rows_all)
    rng.shuffle(test_rows)
    eval_rows = test_rows[: args.eval_size]

    (out_dir / "train").mkdir(parents=True, exist_ok=True)
    (out_dir / "eval").mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(train_rows), out_dir / "train" / "train-00000.parquet")
    pq.write_table(pa.Table.from_pylist(eval_rows), out_dir / "eval" / "eval-00000.parquet")
    stats = {
        "input_dir": str(in_dir), "out_dir": str(out_dir),
        "train_rows": len(train_rows), "eval_rows": len(eval_rows),
        "train_stats": train_stats, "test_stats": test_stats,
        "avg_tool_calls": round(train_stats["tool_calls"] / max(1, train_stats["converted"]), 2),
    }
    (out_dir / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
