"""RWKV chat-template rendering + assistant-only loss mask.

Uses the *actual* HF chat template of the converted G1l checkpoint so that SFT
format matches inference. Mask construction relies on the prefix property of
the template for assistant turns: render(messages[:a], add_generation_prompt=True)
is a prefix of render(messages[:a+1], add_generation_prompt=False).
"""
from __future__ import annotations

import json
from typing import Any

from transformers import AutoTokenizer


class Renderer:
    def __init__(self, model_dir: str, max_len: int = 4096):
        self.tok = AutoTokenizer.from_pretrained(model_dir)
        self.max_len = max_len
        self.eos = self.tok.eos_token_id
        self.template_kwargs = dict(
            rwkv_prompt_template="function_calling",
            rwkv_generation_prompt="open_think",
        )

    def render(self, messages: list[dict], tools: list[dict], add_generation_prompt: bool) -> str:
        return self.tok.apply_chat_template(
            messages,
            tools=tools,
            add_generation_prompt=add_generation_prompt,
            tokenize=False,
            **self.template_kwargs,
        )

    def encode(self, text: str) -> list[int]:
        return self.tok.encode(text, add_special_tokens=False)

    def build(self, messages: list[dict], tools: list[dict]) -> dict[str, Any]:
        """Return input_ids / loss_mask / stats for one multi-turn trajectory."""
        full = self.render(messages, tools, add_generation_prompt=False)
        spans: list[tuple[int, int]] = []
        for a, msg in enumerate(messages):
            if msg["role"] != "assistant":
                continue
            prefix = self.render(messages[:a], tools, add_generation_prompt=True)
            upto = self.render(messages[: a + 1], tools, add_generation_prompt=False)
            if not upto.startswith(prefix):
                raise RuntimeError(f"template prefix mismatch at assistant {a}")
            spans.append((len(prefix), len(upto)))
        ids = self.encode(full)
        # token offsets via prefix tokenization (RWKV tokenizer is greedy -> prefix stable)
        bounds = sorted({s for s, _ in spans} | {e for _, e in spans} | {len(full)})
        off_map = {off: len(self.encode(full[:off])) for off in bounds}
        mask = [0] * len(ids)
        for s, e in spans:
            ts, te = off_map.get(s), off_map.get(e)
            if ts is None or te is None:
                raise RuntimeError("missing offset")
            for i in range(ts, te):
                mask[i] = 1
        ids.append(self.eos)
        mask.append(1)
        if len(ids) > self.max_len:
            raise ValueError(f"too long: {len(ids)}")
        n_assist = sum(mask)
        return {
            "input_ids": ids,
            "loss_mask": mask,
            "n_tokens": len(ids),
            "n_assistant": n_assist,
            "assistant_ratio": n_assist / len(ids),
        }


def parse_tool_calls(rendered: str) -> list[dict]:
    """Extract fenced JSON tool calls from a rendered assistant span (our parser)."""
    calls = []
    in_json = False
    buf = []
    for line in rendered.splitlines():
        if line.strip().startswith("```json"):
            in_json = True
            buf = []
            continue
        if in_json and line.strip().startswith("```"):
            in_json = False
            try:
                payload = json.loads("\n".join(buf))
                if isinstance(payload, dict) and "name" in payload:
                    calls.append(payload)
            except json.JSONDecodeError:
                pass
            continue
        if in_json:
            buf.append(line)
    return calls
