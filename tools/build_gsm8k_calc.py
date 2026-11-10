"""Build the GSM8K-calc RL dataset from GSM8K (CPU only).

Unlike SFT conversion, no target trajectory is written: RL rollouts are
sampled by the policy itself against the calculator environment.  The original
solution is used only to extract (a) the final ground-truth answer and
(b) an `expected_calls` statistic from the `<<expr=val>>` annotations.

Usage:
    python tools/build_gsm8k_calc.py --out-dir $SCRATCH/data/gsm8k-calc
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

DEFAULT_INPUT = "/scratch-shared/szhang4/rwkv-agentic/data/gsm8k"
FINAL_RE = re.compile(r"####\s*([\-+]?[0-9][0-9.,]*(?:[eE][\-+]?[0-9]+)?)")
MARKER_RE = re.compile(r"<<([^<>]+?)=([^<>]+?)>>")
PURE_ARITH_RE = re.compile(r"[\d\s.+\-*/()]+")

AGENT_SYSTEM = (
    "You are an RWKV agent. Use the provided tools when they help; otherwise answer directly. "
    "When you call a tool, write exactly one fenced JSON tool call. Do not invent tool outputs."
)
USER_SUFFIX = (
    "\nUse the calc tool for arithmetic calculations. "
    "Put the final numeric answer after '####'."
)
TOOLS = [
    {
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
]


def normalize_answer(raw: str) -> str:
    s = raw.strip().strip("$").replace(",", "").replace(" ", "").rstrip(".")
    return s[1:] if s.startswith("+") else s


def safe_eval_expression(expr: str) -> float:
    allowed = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)
    tree = ast.parse(expr, mode="eval")

    def walk(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            v = walk(node.operand)
            return v if isinstance(node.op, ast.UAdd) else -v
        if isinstance(node, ast.BinOp) and isinstance(node.op, allowed):
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("exponent too large")
            return {
                ast.Add: lambda: left + right,
                ast.Sub: lambda: left - right,
                ast.Mult: lambda: left * right,
                ast.Div: lambda: left / right,
                ast.FloorDiv: lambda: left // right,
                ast.Mod: lambda: left % right,
                ast.Pow: lambda: left**right,
            }[type(node.op)]()
        raise ValueError(f"unsupported node {type(node).__name__}")

    return walk(tree.body)


def analyze_answer(answer: str) -> dict:
    final = FINAL_RE.findall(answer)
    markers = MARKER_RE.findall(answer)
    pure = 0
    consistent = 0
    convertible = 0
    for lhs, rhs in markers:
        lhs = lhs.strip()
        if PURE_ARITH_RE.fullmatch(lhs):
            pure += 1
            try:
                value = safe_eval_expression(lhs)
                claimed = float(rhs.strip().replace(",", ""))
                if abs(value - claimed) <= 1e-6 * max(1.0, abs(claimed)):
                    consistent += 1
                    convertible += 1
            except Exception:
                pass
    return {
        "final": normalize_answer(final[-1]) if final else None,
        "n_markers": len(markers),
        "n_pure": pure,
        "n_consistent": consistent,
        "n_convertible": convertible,
    }


def load_split(path: Path) -> list[dict]:
    return pq.read_table(path).to_pylist()


def build_rows(rows: list[dict], split: str, require_tool: bool = False, max_turns: int = 3, min_tool_calls: int = 0) -> tuple[list[dict], dict]:
    out = []
    stats = Counter()
    for idx, row in enumerate(rows):
        info = row["extra_info"]
        question = info.get("question") or row["prompt"][0]["content"]
        answer = info["answer"]
        meta = analyze_answer(answer)
        stats["rows"] += 1
        stats["final_parsed"] += int(meta["final"] is not None)
        stats["markers_total"] += meta["n_markers"]
        stats["markers_pure"] += meta["n_pure"]
        stats["markers_consistent"] += meta["n_consistent"]
        stats["problems_with_markers"] += int(meta["n_markers"] > 0)
        if meta["final"] is None:
            continue
        out.append(
            {
                "data_source": "openai/gsm8k",
                "prompt": [
                    {"role": "system", "content": AGENT_SYSTEM},
                    {"role": "user", "content": question + USER_SUFFIX},
                ],
                "env_class": "gsm8k_calc",
                "reward_spec": {
                    "method": "rule",
                    "ground_truth": meta["final"],
                    "require_tool": require_tool,
                    "max_turns": max_turns, "min_tool_calls": min_tool_calls,
                },
                "extra_info": {
                    "split": split,
                    "index": idx,
                    "answer": answer,
                    "question": question,
                    "expected_calls": meta["n_markers"],
                },
            }
        )
    return out, dict(stats)


def question_hash(row: dict) -> str:
    return hashlib.sha256(row["extra_info"]["question"].strip().encode()).hexdigest()


def write_parquet(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default=DEFAULT_INPUT)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--eval-size", type=int, default=262)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tools-json", default=None, help="optional path to write tools schema json")
    ap.add_argument("--require-tool", action="store_true", help="only reward correct answers that used the calc tool")
    ap.add_argument("--max-turns", type=int, default=3, help="turn budget per episode")
    ap.add_argument("--min-tool-calls", type=int, default=0, help="partial credit if correct but fewer calc calls")
    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir or (Path.home() / "gsm8k-calc"))
    train_rows, train_stats = build_rows(load_split(in_dir / "train.parquet"), "train", args.require_tool, args.max_turns, args.min_tool_calls)
    test_rows_all, test_stats = build_rows(load_split(in_dir / "validation.parquet"), "test", args.require_tool, args.max_turns, args.min_tool_calls)
    rng = random.Random(args.seed)
    test_rows = list(test_rows_all)
    rng.shuffle(test_rows)
    eval_rows = test_rows[: args.eval_size]

    write_parquet(out_dir / "train.parquet", train_rows)
    write_parquet(out_dir / "eval.parquet", eval_rows)
    write_parquet(out_dir / "test-full.parquet", test_rows_all)
    if args.tools_json:
        Path(args.tools_json).write_text(json.dumps(TOOLS, indent=2), encoding="utf-8")

    train_q = {question_hash(r) for r in train_rows}
    eval_q = {question_hash(r) for r in eval_rows}
    stats = {
        "input_dir": str(in_dir),
        "out_dir": str(out_dir),
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "test_full_rows": len(test_rows_all),
        "eval_size_requested": args.eval_size,
        "leakage_train_eval": len(train_q & eval_q),
        "train_stats": train_stats,
        "test_stats": test_stats,
        "drop_rate": round(1 - (len(train_rows) / train_stats["rows"]), 6),
        "tools": TOOLS,
        "agent_system": AGENT_SYSTEM,
        "user_suffix": USER_SUFFIX,
    }
    (out_dir / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
