"""GSM8K avg@k / pass@k evaluation (sampled, k completions per question)."""
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


def extract(text: str):
    m = FINAL_RE.findall(text)
    if m:
        return m[-1]
    b = BOXED_RE.findall(text)
    return b[-1] if b else None


def match(pred, gt) -> bool:
    if pred is None:
        return False
    p, g = normalize(pred), normalize(gt)
    if p == g:
        return True
    try:
        return abs(float(p) - float(g)) <= 1e-6 * max(1.0, abs(float(g)))
    except ValueError:
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", default="/scratch-shared/szhang4/rwkv-agentic/data/gsm8k")
    ap.add_argument("--split", default="validation")
    ap.add_argument("--out", default="gsm8k-avgk.json")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=1536)
    ap.add_argument("--max-model-len", type=int, default=4096)
    ap.add_argument("--temperature", type=float, default=1.0)
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
        m = FINAL_RE.findall(info["answer"])
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
    sp = SamplingParams(max_tokens=args.max_tokens, temperature=args.temperature,
                        top_p=1.0, top_k=-1, n=args.k)
    outs = llm.generate([{"prompt_token_ids": p} for p in prompts], sp)

    per_q, passk, sum_k = [], 0, 0.0
    for o, gt in zip(outs, gts):
        text = o.outputs[0].text  # vLLM: first completion text (joined style?)
        preds = [extract(o.outputs[0].text)]
        # vLLM n>1: outputs[0].outputs has k entries
        if hasattr(o, "outputs") and isinstance(o.outputs, list) and len(o.outputs) > 1:
            preds = [extract(x.text) for x in o.outputs]
        corr = [match(p, gt) for p in preds]
        per_q.append({"gt": gt, "preds": preds, "correct": corr})
        passk += int(any(corr))
        sum_k += sum(corr) / len(corr)
    n = len(per_q)
    summary = {
        "model": args.model, "n": n, "k": args.k, "temperature": args.temperature,
        f"pass@{args.k}": round(passk / n, 4),
        f"avg@{args.k}": round(sum_k / n, 4),
    }
    Path(args.out).write_text(json.dumps({"summary": summary, "records": per_q}, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    import os
    os._exit(0)


if __name__ == "__main__":
    main()
