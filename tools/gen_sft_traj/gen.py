"""Generate P1.5 SFT trajectories -> raw JSONL + pretokenized parquet."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import envs  # noqa: E402
from render import Renderer  # noqa: E402

WEIGHTS = {"calc": 0.15, "file_edit": 0.20, "code_task": 0.20,
           "local_search": 0.20, "stats": 0.10, "direct": 0.15}
GENS = {
    "calc": envs.calc_samples,
    "file_edit": envs.file_edit_samples,
    "code_task": envs.code_task_samples,
    "local_search": envs.search_samples,
    "stats": envs.stats_samples,
    "direct": envs.direct_samples,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=2500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--val-frac", type=float, default=0.1)
    args = ap.parse_args()

    out = Path(args.out)
    (out / "raw").mkdir(parents=True, exist_ok=True)
    r = Renderer(args.model, max_len=args.max_len)
    rng = random.Random(args.seed)

    samples: list[dict] = []
    for cat, w in WEIGHTS.items():
        k = round(args.n * w)
        gen = GENS[cat]
        seen = set()
        made = 0
        attempts = 0
        while made < k:
            attempts += 1
            if attempts > k * 300:
                raise SystemExit(f"generator {cat!r} exhausted unique samples: {made}/{k}")
            s = gen(rng)
            h = hashlib.sha256(json.dumps(s["messages"], sort_keys=True).encode()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            s["_hash"] = h
            samples.append(s)
            made += 1

    rng.shuffle(samples)
    splits = {"train": [], "eval": []}
    for s in samples:
        h = int(s["question_id"], 16) / 2**64
        split = "eval" if h < args.val_frac else "train"
        splits[split].append(s)

    stats = {"requested": args.n, "categories": Counter(), "negatives": Counter(),
             "tokens": [], "assistant_ratio": [], "render_failures": 0, "too_long": 0}
    rows = {"train": [], "eval": []}
    for split, items in splits.items():
        raw_path = out / "raw" / f"{split}.jsonl"
        with raw_path.open("w", encoding="utf-8") as f:
            for s in items:
                try:
                    built = r.build(s["messages"], s["tools"])
                except ValueError:
                    stats["too_long"] += 1
                    continue
                except RuntimeError as e:
                    stats["render_failures"] += 1
                    print(f"render fail {s['category']}: {e}", file=sys.stderr)
                    continue
                stats["categories"][s["category"]] += 1
                if s["meta"].get("negative") not in (None, "none"):
                    stats["negatives"][s["meta"]["negative"]] += 1
                stats["tokens"].append(built["n_tokens"])
                stats["assistant_ratio"].append(built["assistant_ratio"])
                f.write(json.dumps({k: v for k, v in s.items() if k != "_hash"}, ensure_ascii=False) + "\n")
                rows[split].append({
                    "uuid": s["_hash"][:16],
                    "question_id": s["question_id"],
                    "input_ids": built["input_ids"],
                    "loss_mask": built["loss_mask"],
                })

    schema = pa.schema([("uuid", pa.string()), ("question_id", pa.string()),
                        ("input_ids", pa.list_(pa.int32())), ("loss_mask", pa.list_(pa.int8()))])
    for split, rs in rows.items():
        (out / split).mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.Table.from_pylist(rs, schema=schema), out / split / f"{split}-00000.parquet")

    lengths = sorted(stats["tokens"])
    summ = {
        "requested": args.n,
        "written_train": len(rows["train"]), "written_eval": len(rows["eval"]),
        "categories": dict(stats["categories"]), "negatives": dict(stats["negatives"]),
        "render_failures": stats["render_failures"], "too_long": stats["too_long"],
        "token_len": {"min": lengths[0] if lengths else 0,
                      "p50": lengths[len(lengths)//2] if lengths else 0,
                      "p95": lengths[int(len(lengths)*0.95)] if lengths else 0,
                      "max": lengths[-1] if lengths else 0},
        "assistant_ratio_p50": sorted(stats["assistant_ratio"])[len(stats["assistant_ratio"])//2] if stats["assistant_ratio"] else 0,
    }
    (out / "stats.json").write_text(json.dumps(summ, indent=2, ensure_ascii=False))
    print(json.dumps(summ, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
