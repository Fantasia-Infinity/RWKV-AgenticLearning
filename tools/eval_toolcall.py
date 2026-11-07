"""G3-style evaluation: tool-call parse rate / tool choice on held-out synthetic set.

Loads an exported HF policy (merged adapters) with vLLM, renders prompts with the
same RWKV chat template used for SFT, generates greedily, and measures:
  - parse_rate: generated output contains exactly one valid fenced JSON tool call
  - tool_name_acc: parsed tool name == reference first tool name
  - no_call_rate: for direct/refusal samples, output has no tool call
Usage:
  python eval_toolcall.py --model <hf_export_dir> --data <sft-p15 dir> --out result.json [--limit N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "gen_sft_traj"))
from render import parse_tool_calls  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="g3-eval.json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-tokens", type=int, default=256)
    args = ap.parse_args()

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(args.model)
    samples = []
    for split in ("eval", "train"):
        f = Path(args.data) / "raw" / f"{split}.jsonl"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    samples.append(json.loads(line))
        if samples:
            break
    if args.limit:
        samples = samples[: args.limit]

    prompts, metas = [], []
    for s in samples:
        msgs = s["messages"]
        cut = next((i for i, m in enumerate(msgs) if m["role"] == "assistant"), len(msgs))
        text = tok.apply_chat_template(
            msgs[:cut], tools=s["tools"], add_generation_prompt=True, tokenize=False,
            rwkv_prompt_template="function_calling", rwkv_generation_prompt="open_think",
        )
        prompts.append(tok.encode(text, add_special_tokens=False))
        expected = None
        for m in msgs:
            if m["role"] == "assistant" and m.get("tool_calls"):
                expected = m["tool_calls"][0]["function"]["name"]
                break
        metas.append({"category": s["category"], "expected_tool": expected})

    llm = LLM(model=args.model, tokenizer=args.model, dtype="bfloat16",
              max_model_len=4096, enforce_eager=True, gpu_memory_utilization=0.6,
              disable_log_stats=True)
    outs = llm.generate([{"prompt_token_ids": p} for p in prompts],
                        SamplingParams(max_tokens=args.max_tokens, temperature=0.0))
    texts = [o.outputs[0].text for o in outs]

    per_cat = defaultdict(lambda: {"n": 0, "parsed": 0, "name_ok": 0, "no_expected": 0,
                                   "expected_n": 0, "parse_ok_when_expected": 0})
    records = []
    for text, meta in zip(texts, metas):
        calls = parse_tool_calls(text)
        cat = meta["category"]
        c = per_cat[cat]
        c["n"] += 1
        if len(calls) == 1:
            c["parsed"] += 1
        exp = meta["expected_tool"]
        if exp is None:
            c["expected_n"] += 0
            c["no_expected"] += 0 if calls else 1
        else:
            c["expected_n"] += 1
            if len(calls) == 1 and calls[0].get("name") == exp:
                c["name_ok"] += 1
            if len(calls) == 1:
                c["parse_ok_when_expected"] += 1
        records.append({"category": cat, "expected": exp, "text": text[:500],
                        "calls": calls, "parsed": len(calls) == 1})

    exp_tool = sum(1 for r in records if r["expected"])
    exp_none = sum(1 for r in records if not r["expected"])
    parsed_exp = sum(1 for r in records if r["expected"] and r["parsed"])
    name_ok = sum(1 for r in records if r["expected"] and r["parsed"]
                  and r["calls"][0].get("name") == r["expected"])
    no_call_ok = sum(1 for r in records if not r["expected"] and not r["calls"])
    summary = {
        "model": args.model,
        "n": len(records),
        "samples_with_expected_tool": exp_tool,
        "samples_expected_no_call": exp_none,
        "parse_rate_on_expected": round(parsed_exp / exp_tool, 4) if exp_tool else None,
        "tool_name_acc": round(name_ok / exp_tool, 4) if exp_tool else None,
        "no_call_rate_on_expected_none": round(no_call_ok / exp_none, 4) if exp_none else None,
        "per_category": {k: dict(v) for k, v in sorted(per_cat.items())},
    }
    Path(args.out).write_text(json.dumps({"summary": summary, "records": records},
                                         ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
