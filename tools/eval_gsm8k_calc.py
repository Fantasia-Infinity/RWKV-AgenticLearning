"""Evaluate a policy on GSM8K-calc (tool-use) with a batched multi-turn rollout.

Loads a merged HF policy with vLLM, renders prompts with the same
function_calling RWKV template + calculator tool schema used for RL, executes
calc calls locally, and reports:

  - accuracy: final ``####`` answer matches the ground truth
  - format_rate: a ``####`` answer was emitted within the turn budget
  - tool_call_rate / avg_tool_calls / tool_error_rate
  - turns distribution

Usage:
  python tools/eval_gsm8k_calc.py --model <policy_dir> --data $SCRATCH/data/gsm8k-calc \
      --out $SCRATCH/results/p3-policy-eval.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow.parquet as pq

from skyrl_gym.envs.gsm8k.calc_env import (
    _answers_match,
    extract_final_answer,
    extract_tool_expression,
)
from skyrl_gym.tools.calculator import CalculatorToolGroup

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


def render(tok, messages):
    text = tok.apply_chat_template(
        messages,
        tools=[TOOL_CALC],
        add_generation_prompt=True,
        tokenize=False,
        rwkv_prompt_template="function_calling",
        rwkv_generation_prompt="open_think",
    )
    return tok.encode(text, add_special_tokens=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="gsm8k-calc-eval.json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-turns", type=int, default=6)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--max-model-len", type=int, default=16384)
    args = ap.parse_args()

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(args.model)
    rows = pq.read_table(Path(args.data) / "eval.parquet").to_pylist()
    if args.limit:
        rows = rows[: args.limit]

    llm = LLM(model=args.model, tokenizer=args.model, dtype="bfloat16",
              max_model_len=args.max_model_len, enforce_eager=True, gpu_memory_utilization=0.6,
              disable_log_stats=True)
    sp = SamplingParams(max_tokens=args.max_tokens, temperature=0.0)
    calc = CalculatorToolGroup()

    states = []
    for row in rows:
        states.append({
            "messages": list(row["prompt"]),
            "gt": row["reward_spec"]["ground_truth"],
            "done": False,
            "final": None,
            "turns": 0,
            "tool_calls": 0,
            "tool_errors": 0,
            "texts": [],
        })

    for turn in range(1, args.max_turns + 1):
        active = [i for i, s in enumerate(states) if not s["done"]]
        if not active:
            break
        prompts = [render(tok, states[i]["messages"]) for i in active]
        outs = llm.generate([{"prompt_token_ids": p} for p in prompts], sp)
        for i, o in zip(active, outs):
            st = states[i]
            text = o.outputs[0].text
            st["turns"] = turn
            st["texts"].append(text)
            st["messages"].append({"role": "assistant", "content": text})
            final = extract_final_answer(text)
            if final is not None:
                st["done"] = True
                st["final"] = final
                continue
            expr, err = extract_tool_expression(text)
            if expr is not None:
                st["tool_calls"] += 1
                payload = json.loads(calc.execute_tool("calc", expr))
                if "error" in payload:
                    st["tool_errors"] += 1
                obs = {"role": "tool", "content": payload}
            else:
                if err is not None:
                    st["tool_errors"] += 1
                obs = {"role": "tool", "content": {"error": err or "no final answer and no calc tool call found"}}
            st["messages"].append(obs)

    correct = 0
    formatted = 0
    tool_samples = 0
    tool_calls_total = 0
    tool_err_samples = 0
    turns_sum = 0
    records = []
    for st in states:
        acc = st["final"] is not None and _answers_match(st["final"], st["gt"])
        correct += int(acc)
        formatted += int(st["final"] is not None)
        tool_samples += int(st["tool_calls"] > 0)
        tool_calls_total += st["tool_calls"]
        tool_err_samples += int(st["tool_errors"] > 0)
        turns_sum += st["turns"]
        records.append({
            "gt": st["gt"], "final": st["final"], "correct": acc,
            "turns": st["turns"], "tool_calls": st["tool_calls"],
            "tool_errors": st["tool_errors"], "texts": st["texts"],
        })
    n = len(states)
    summary = {
        "model": args.model, "n": n, "max_turns": args.max_turns,
        "accuracy": round(correct / n, 4),
        "format_rate": round(formatted / n, 4),
        "tool_call_rate": round(tool_samples / n, 4),
        "avg_tool_calls": round(tool_calls_total / n, 2),
        "tool_error_sample_rate": round(tool_err_samples / n, 4),
        "avg_turns": round(turns_sum / n, 2),
    }
    Path(args.out).write_text(json.dumps({"summary": summary, "records": records},
                                         ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    import os
    os._exit(0)


if __name__ == "__main__":
    main()
