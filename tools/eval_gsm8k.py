"""GSM8K pass@1 evaluation for the plain-math (no-tool) RLVR control run.

Batched greedy generation with vLLM using the same *bot* prompt style as the
P2 RLVR recipe.  Reports pass@1 + per-sample records.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pyarrow.parquet as pq

FINAL_RE = re.compile(r"####\s*([\-+]?[0-9][0-9.,]*(?:[eE][\-+]?[0-9]+)?)")
BOXED_RE = re.compile(r"\\boxed\{([^{}]+)\}")


def normalize(text: str) -> str:
    s = text.strip().strip("$").replace(",", "").replace(" ", "").rstrip(".")
    return s[1:] if s.startswith("+") else s


def match(pred: str, gt: str) -> bool:
    p, g = normalize(pred), normalize(gt)
    if p == g:
        return True
    try:
        return abs(float(p) - float(g)) <= 1e-6 * max(1.0, abs(float(g)))
    except ValueError:
        return False


def extract(text: str):
    m = FINAL_RE.findall(text)
    if m:
        return m[-1]
    b = BOXED_RE.findall(text)
    return b[-1] if b else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", default="/scratch-shared/szhang4/rwkv-agentic/data/gsm8k")
    ap.add_argument("--split", default="validation")
    ap.add_argument("--out", default="gsm8k-eval.json")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--max-model-len", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    import random
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(args.model)
    rows = pq.read_table(Path(args.data) / f"{args.split}.parquet").to_pylist()
    rng = random.Random(args.seed)
    rng.shuffle(rows)
    rows = rows[: args.limit]

    prompts, gts = [], []
    for row in rows:
        info = row["extra_info"]
        q = info.get("question") or row["prompt"][0]["content"]
        ans = info["answer"]
        m = FINAL_RE.findall(ans)
        if not m:
            continue
        gts.append(normalize(m[-1]))
        text = tok.apply_chat_template(
            [{"role": "user", "content": q + ' Let\'s think step by step and output the final answer after "####".'}],
            add_generation_prompt=True, tokenize=False,
            rwkv_prompt_template="bot", rwkv_generation_prompt="open_think",
        )
        prompts.append(tok.encode(text, add_special_tokens=False))

    llm = LLM(model=args.model, tokenizer=args.model, dtype="bfloat16",
              max_model_len=args.max_model_len, enforce_eager=True,
              gpu_memory_utilization=0.6, disable_log_stats=True)
    outs = llm.generate([{"prompt_token_ids": p} for p in prompts],
                        SamplingParams(max_tokens=args.max_tokens, temperature=0.0))
    records, correct = [], 0
    for o, gt in zip(outs, gts):
        text = o.outputs[0].text
        pred = extract(text)
        ok = pred is not None and match(pred, gt)
        correct += int(ok)
        records.append({"gt": gt, "pred": pred, "correct": ok, "text": text[:800]})
    n = len(records)
    summary = {"model": args.model, "n": n, "pass@1": round(correct / n, 4),
               "format_rate": round(sum(1 for r in records if r["pred"] is not None) / n, 4)}
    Path(args.out).write_text(json.dumps({"summary": summary, "records": records}, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    import os
    os._exit(0)


if __name__ == "__main__":
    main()
