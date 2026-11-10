"""Build plain-math (no tool) SFT trajectories from GSM8K solutions.

Messages use the *bot* prompt style (same as the plain-GSM8K RLVR recipe), so the
resulting warm start matches P2's prompt format exactly:

    User: <question> Let's think step by step and output the final answer after "####".
    Assistant: <full GSM8K solution> #### <answer>

Output: pretokenized parquet (uuid/question_id/input_ids/loss_mask).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

FINAL_RE = re.compile(r"####\s*([\-+]?[0-9][0-9.,]*(?:[eE][\-+]?[0-9]+)?)")
INSTR = ' Let\'s think step by step and output the final answer after "####".'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="/scratch-shared/szhang4/rwkv-agentic/data/gsm8k")
    ap.add_argument("--out-dir", default="/scratch-shared/szhang2/rwkv-agentic/data/sft-gsm8k-math")
    ap.add_argument("--model", default="/scratch-shared/szhang2/rwkv-agentic/weights/g1l-1.5b-hf")
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--eval-size", type=int, default=256)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model)
    kwargs = dict(rwkv_prompt_template="bot", rwkv_generation_prompt="open_think")

    def render(msgs, gen):
        text = tok.apply_chat_template(msgs, add_generation_prompt=gen, tokenize=False, **kwargs)
        return text, tok.encode(text, add_special_tokens=False)

    def encode_with_mask(q: str, full_answer: str):
        gt = FINAL_RE.findall(full_answer)[-1]
        body = FINAL_RE.sub("", full_answer).strip()
        user = q + INSTR
        assistant = f"<think>{body}</think>\n#### {gt}"
        msgs = [{"role": "user", "content": user}, {"role": "assistant", "content": assistant}]
        prefix_text, prefix_ids = render(msgs[:1], gen=True)
        full_text, full_ids = render(msgs, gen=False)
        if not full_text.startswith(prefix_text):
            raise RuntimeError("template prefix mismatch")
        n_prefix = len(prefix_ids)
        mask = [0] * len(full_ids)
        for i in range(n_prefix, len(full_ids)):
            mask[i] = 1
        return full_ids, mask

    def build(split_name):
        rows = pq.read_table(Path(args.data) / f"{split_name}.parquet").to_pylist()
        out = []
        for idx, row in enumerate(rows):
            info = row["extra_info"]
            try:
                ids, mask = encode_with_mask(info["question"], info["answer"])
            except Exception:
                continue
            if len(ids) > args.max_len:
                continue
            qid = hashlib.sha256(info["question"].encode()).hexdigest()[:16]
            out.append({"uuid": hashlib.sha256(f"{info['question']}::{idx}".encode()).hexdigest()[:16],
                        "question_id": qid, "input_ids": ids, "loss_mask": mask})
        return out

    train = build("train")
    test = build("validation")
    import random
    rng = random.Random(args.seed)
    rng.shuffle(test)
    ev = test[: args.eval_size]
    (Path(args.out_dir) / "train").mkdir(parents=True, exist_ok=True)
    (Path(args.out_dir) / "eval").mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(train), Path(args.out_dir) / "train" / "train-00000.parquet")
    pq.write_table(pa.Table.from_pylist(ev), Path(args.out_dir) / "eval" / "eval-00000.parquet")
    lens = [len(r["input_ids"]) for r in train]
    stats = {"train_rows": len(train), "eval_rows": len(ev), "tokens_total": sum(lens),
             "len_min": min(lens), "len_p50": statistics.median(lens), "len_max": max(lens)}
    (Path(args.out_dir) / "stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
