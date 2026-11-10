"""CPU regression tests for the rwkv tool-call chat template (PR #20 semantics).

Validates:
  1. tool-call history + system + `tools=None` renders without TypeError (tools or [])
  2. past tool calls use the one-line instructed format: {"name": ..., "arguments": ...}
  3. string-typed arguments are inserted raw (not double-encoded)
  4. conversations without tool calls render byte-identically to the old template

Usage:
    python tools/test_chat_template.py --model-dir <hf_export> \
        --new-template /tmp/rwkv_post20.jinja --old-template <hf_export>/chat_template.pre-pr20.jinja
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SYSTEM = "Tools:\n- get_weather(location: string)"


def render(tok, template: str, messages, tools):
    return tok.apply_chat_template(
        messages,
        tools=tools,
        add_generation_prompt=True,
        tokenize=False,
        chat_template=template,
        rwkv_prompt_template="function_calling",
        rwkv_generation_prompt="open_think",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True, type=Path)
    ap.add_argument("--new-template", required=True, type=Path)
    ap.add_argument("--old-template", default=None, type=Path)
    args = ap.parse_args()

    from transformers import AutoTokenizer

    new = args.new_template.read_text()
    old = args.old_template.read_text() if args.old_template else None
    tok = AutoTokenizer.from_pretrained(args.model_dir)
    failures = []

    # 1 + 2: crash edge + one-line format, tools=None
    history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the weather in Paris?"},
        {"role": "assistant", "content": None,
         "tool_calls": [{"function": {"name": "get_weather", "arguments": {"location": "Paris"}}}]},
        {"role": "tool", "content": {"temperature": 21}},
        {"role": "assistant", "content": "It is 21 C in Paris."},
        {"role": "user", "content": "And in Berlin?"},
    ]
    try:
        text = render(tok, new, history, None)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"tools=None + tool history raised {type(exc).__name__}: {exc}")
        text = ""
    if text:
        if '"name": "get_weather", "arguments": {"location": "Paris"}' not in text:
            failures.append("one-line tool-call format missing from rendered history")
        if "\\\"arguments\\\"\n" in text or "\n  \"arguments\"" in text:
            failures.append("tool-call arguments still rendered as indented/escaped JSON")

    # 3: string arguments stay raw, not escaped
    str_args = [
        {"role": "user", "content": "Weather?"},
        {"role": "assistant", "content": None,
         "tool_calls": [{"function": {"name": "get_weather", "arguments": '{"location": "Paris"}'}}]},
        {"role": "tool", "content": {"temperature": 21}},
    ]
    try:
        text2 = render(tok, new, str_args, None)
        if '"arguments": {"location": "Paris"}' not in text2:
            failures.append("string-typed arguments were not inserted raw")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"string-arguments case raised {type(exc).__name__}: {exc}")

    # 4: no-tool conversations byte-identical between old and new template
    if old is not None:
        plain = [
            {"role": "user", "content": "What is 2+2? Let's think step by step."},
        ]
        a = render(tok, old, plain, None)
        b = render(tok, new, plain, None)
        if a != b:
            failures.append("no-tool conversation rendering changed between old and new template")

    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        return 1
    print("PASS: tool-call template regression tests (4 cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
