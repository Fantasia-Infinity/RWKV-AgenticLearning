"""Build a small self-owned held-out tool-use benchmark (120 tasks).

Reuses the P1.5 trajectory generators with a *held-out* seed, extracts the
question, the expected first tool call and the final answer, and writes JSON
for the multi-turn evaluation harness.  Content is generated locally -> no
external license constraints.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "gen_sft_traj"))
from envs import calc_samples, search_samples, stats_samples, direct_samples  # noqa: E402

GENERATORS = {
    "calc": calc_samples,
    "local_search": search_samples,
    "stats": stats_samples,
    "direct": direct_samples,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/scratch-shared/szhang2/rwkv-agentic/data/heldout-tool-eval/tasks.json")
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed", type=int, default=20261109)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    cats = list(GENERATORS)
    tasks, seen = [], set()
    while len(tasks) < args.n:
        cat = cats[len(tasks) % len(cats)]
        sample = GENERATORS[cat](rng)
        q = sample["messages"][1]["content"]
        if sample["question_id"] in seen:
            continue
        seen.add(sample["question_id"])
        expected = None
        for m in sample["messages"]:
            if m["role"] == "assistant" and m.get("tool_calls"):
                expected = m["tool_calls"][0]["function"]
                break
        tasks.append({
            "category": cat,
            "question": q,
            "question_id": sample["question_id"],
            "tools": sample["tools"],
            "expected_tool": None if expected is None else expected["name"],
            "expected_arguments": None if expected is None else expected["arguments"],
            "answer": sample["answer"],
        })
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"n": len(tasks), "seed": args.seed, "tasks": tasks}, ensure_ascii=False, indent=2))
    from collections import Counter
    print(json.dumps({"n": len(tasks), "categories": dict(Counter(t["category"] for t in tasks)),
                      "with_tool": sum(1 for t in tasks if t["expected_tool"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
