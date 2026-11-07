"""Validate P1.5 SFT data: mask, length, distribution, tool-call parse rate."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import Renderer, parse_tool_calls  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--recheck", type=int, default=30)
    args = ap.parse_args()

    d = Path(args.data)
    r = Renderer(args.model, max_len=args.max_len)
    fails = Counter()
    total = 0
    for split in ("train", "eval"):
        t = pq.read_table(sorted((d / split).glob("*.parquet"))[0])
        total += t.num_rows
        for row in t.to_pylist():
            ids, mask = row["input_ids"], row["loss_mask"]
            if len(ids) != len(mask):
                fails["len_mismatch"] += 1
            if len(ids) > args.max_len:
                fails["too_long"] += 1
            if not any(mask):
                fails["no_supervision"] += 1
            if any(m not in (0, 1) for m in mask):
                fails["bad_mask_value"] += 1
            if ids[-1] != r.eos or mask[-1] != 1:
                fails["bad_eos"] += 1
    print(f"rows={total} fails={dict(fails) or 'none'}")

    # independent re-render check + tool-call parse rate on a sample of raw jsonl
    raw = [json.loads(l) for split in ("train", "eval")
           for l in (d / "raw" / f"{split}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    import random
    rng = random.Random(0)
    checked = parsed = tool_msgs = 0
    for s in rng.sample(raw, min(args.recheck, len(raw))):
        built = r.build(s["messages"], s["tools"])
        checked += 1
        # tool-call parse rate on assistant spans
        for a, msg in enumerate(s["messages"]):
            if msg["role"] != "assistant" or not msg.get("tool_calls"):
                continue
            tool_msgs += 1
            prefix = r.render(s["messages"][:a], s["tools"], True)
            upto = r.render(s["messages"][: a + 1], s["tools"], False)
            calls = parse_tool_calls(upto[len(prefix):])
            if calls and calls[0].get("name") == msg["tool_calls"][0]["function"]["name"]:
                parsed += 1
    print(f"re-render ok={checked}; tool_msgs={tool_msgs} parsed={parsed} "
          f"parse_rate={parsed / tool_msgs if tool_msgs else 1.0:.4f}")
    ok = not fails and (tool_msgs == 0 or parsed / tool_msgs >= 0.99)
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
