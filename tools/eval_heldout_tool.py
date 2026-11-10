"""Evaluate tool-call behaviour on the self-owned held-out tool benchmark.

Single-step evaluation (no environment execution):
  - tool-name accuracy: emitted first tool call name == expected tool
  - argument validity: calc expression parses, or required args non-empty
  - direct tasks: no tool call emitted + answer matches expected
  - format rate: a valid fenced JSON tool call (or direct answer) was produced
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "gen_sft_traj"))
from render import parse_tool_calls  # noqa: E402

PURE_ARITH = re.compile(r"[\d\s.+\-*/()]+")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", default="/scratch-shared/szhang2/rwkv-agentic/data/heldout-tool-eval/tasks.json")
    ap.add_argument("--out", default="heldout-tool-eval.json")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--max-model-len", type=int, default=4096)
    args = ap.parse_args()

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    tasks = json.loads(Path(args.data).read_text())["tasks"]
    tok = AutoTokenizer.from_pretrained(args.model)
    SYSTEM = ("You are an RWKV agent. If the task requires an arithmetic calculation, "
              "call the calc tool. For non-arithmetic questions, answer directly without tools. "
              "When you call a tool, write exactly one fenced JSON tool call. Do not invent tool outputs.")
    prompts = []
    for t in tasks:
        text = tok.apply_chat_template(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": t["question"]}],
            tools=t["tools"], add_generation_prompt=True, tokenize=False,
            rwkv_prompt_template="function_calling", rwkv_generation_prompt="open_think",
        )
        prompts.append(tok.encode(text, add_special_tokens=False))

    llm = LLM(model=args.model, tokenizer=args.model, dtype="bfloat16",
              max_model_len=args.max_model_len, enforce_eager=True,
              gpu_memory_utilization=0.6, disable_log_stats=True)
    outs = llm.generate([{"prompt_token_ids": p} for p in prompts],
                        SamplingParams(max_tokens=args.max_tokens, temperature=0.0))

    recs = []
    for t, o in zip(tasks, outs):
        text = o.outputs[0].text
        calls = parse_tool_calls(text)
        call = calls[0] if calls else None
        name = call.get("name") if isinstance(call, dict) else None
        args_ok = True
        if name == "calc":
            expr = (call.get("arguments") or {}).get("expression", "")
            args_ok = bool(isinstance(expr, str) and expr.strip() and PURE_ARITH.fullmatch(expr.strip()))
        elif call is not None:
            args_ok = bool(isinstance(call.get("arguments"), dict) and call["arguments"])
        if t["expected_tool"] is None:
            ok = call is None and str(t["answer"]).split()[0] in text
            recs.append({"category": t["category"], "expected": None, "emitted": name,
                         "name_ok": None, "args_ok": None, "direct_ok": ok})
        else:
            recs.append({"category": t["category"], "expected": t["expected_tool"], "emitted": name,
                         "name_ok": name == t["expected_tool"], "args_ok": args_ok, "direct_ok": None})

    summary = {"model": args.model, "n": len(recs)}
    tool = [r for r in recs if r["expected"] is not None]
    direct = [r for r in recs if r["expected"] is None]
    if tool:
        summary["tool_name_acc"] = round(sum(1 for r in tool if r["name_ok"]) / len(tool), 4)
        summary["arg_valid_rate"] = round(sum(1 for r in tool if r["args_ok"]) / len(tool), 4)
    if direct:
        summary["direct_no_call_rate"] = round(sum(1 for r in direct if r["emitted"] is None) / len(direct), 4)
        summary["direct_answer_acc"] = round(sum(1 for r in direct if r["direct_ok"]) / len(direct), 4)
    by_cat = {}
    for cat in sorted({r["category"] for r in recs}):
        rs = [r for r in recs if r["category"] == cat]
        by_cat[cat] = {
            "n": len(rs),
            "name_acc": round(sum(1 for r in rs if r["name_ok"]) / len(rs), 4) if rs[0]["expected"] else None,
            "direct_ok": round(sum(1 for r in rs if r["direct_ok"]) / len(rs), 4) if not rs[0]["expected"] else None,
        }
    summary["per_category"] = by_cat
    Path(args.out).write_text(json.dumps({"summary": summary, "records": recs}, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    import os
    os._exit(0)


if __name__ == "__main__":
    main()
