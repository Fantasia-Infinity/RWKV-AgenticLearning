# P1.5 SFT trajectory generator

Deterministic, offline generator for RWKV agent multi-turn SFT data.
No model calls, no external data: every trajectory is scripted from a seeded RNG.

## What it produces
- 6 categories: `calc` 15%, `file_edit` 20%, `code_task` 20%, `local_search` 20%,
  `stats` 10%, `direct/refusal` 15%
- Negative samples from real failure modes: duplicate-read rejection, tool-error retry,
  empty search retry, test-fail-then-fix, bad-pipe retry
- Format: RWKV `function_calling` chat template + `<think>` first; assistant-only loss mask
- Output: skyrl-rwkv SFT pretokenized store `train/*.parquet`, `eval/*.parquet`
  (schema: `uuid, question_id, input_ids, loss_mask`)

## Usage
```bash
V=/scratch-shared/$USER/rwkv-agentic/env/skyrl-rwkv
W=/scratch-shared/$USER/rwkv-agentic/weights/g1l-1.5b-hf
$V/bin/python gen.py --model $W --out $SCRATCH/data/sft-p15 --n 2500
$V/bin/python validate.py --data $SCRATCH/data/sft-p15 --model $W
```

## Files
- `envs.py` — deterministic tool environments (6 categories)
- `render.py` — chat-template rendering + assistant-only mask (prefix-consistency check)
- `gen.py` — sampling, dedupe, 90/10 split, parquet writing, stats
- `validate.py` — mask/length/EOS checks + independent re-render + tool-call parse rate

Data is generated locally (scratch) and not committed; only this code is.
