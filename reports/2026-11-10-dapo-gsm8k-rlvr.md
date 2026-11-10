# DAPO on GSM8K for RWKV-7 G1l-1.5B: first positive RL result (avg@4 +10pp)

> Date: 2026-11-10. Status: complete. All numbers are from our own runs on Snellius
> (A100-40GB), license-clean: code in this repo, weights Apache-2.0, eval data from GSM8K.

## TL;DR

- Started from a plain-math SFT warm start (GSM8K train, 7,473 trajectories, 234 steps).
- Ran **DAPO for 1,000 steps** (16 rollouts/step, single policy + reference-free-style setup,
  no dynamic-sampling filter) on 2×A100 in ~16 h (~4.1k SBU incl. evaluations).
- **avg@4 (200 GSM8K test questions, temperature 1.0, k=4): 21.0% → 31.0% (+10.0pp,
  paired t=3.99, p=6.6e-05; per-question wins/losses/ties 74/40/86).**
- pass@4 unchanged (50.0% → 50.5%, McNemar p=1.0): RL improves per-sample accuracy, not coverage.
- Checkpoint-to-checkpoint variance is ±5pp (small batch), so treat single checkpoints with care;
  mean of the last five checkpoints (600–1000) is 29.5% (+8.5pp over base).

## Setup

| Item | Value |
|---|---|
| Base model | RWKV-7 **G1l-1.5B** (2026-10-31, Apache-2.0; the latest G1 generation at 1.5B) |
| SFT warm start | GSM8K train solutions → plain-math trajectories (bot chat template), 234 steps, batch 32, lr 1e-6 |
| RL data | GSM8K train (7,473 prompts), answer reward from `#### <number>` exact match (non-strict extraction) |
| Algorithm | DAPO: GRPO advantage, dual-clip (ε_low 0.2 / ε_high 0.28), token-mean loss, overlong filtering; `dynamic_sampling=null` (filter crashed on all-zero-variance batches in early attempts) |
| Rollouts | 4 prompts × 4 samples = 16 rollouts/step; max generation 1,280 tokens; sampling temperature 1.0 (RWKV raw-logprobs backend requires an unmodified rollout distribution) |
| Training | 1,000 steps, lr 1e-6, FSDP on 2×A100-40GB, ~16 h; checkpoints every 100 steps |
| Evaluation | 200 GSM8K test questions, **avg@4 / pass@4 at temperature 1.0** (same protocol as the official RWKV RLVR talk), `tools/eval_gsm8k_avgk.py` |

## Learning curve (avg@4 / pass@4, 200 questions)

| step | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| avg@4 | 21.5 | 25.6 | 27.9 | 30.3 | 25.3 | 29.8 | 27.1 | 30.6 | 29.0 | **31.0** |
| pass@4 | 45.0 | 46.0 | 46.0 | 48.5 | 43.5 | 53.5 | 51.5 | 51.0 | 52.5 | 50.5 |

Reference points (same metric/protocol): base 21.0%, math-SFT 17.5%, earlier FlashREINFORCE run (50 steps) 26.0%.

## Interpretation

1. **The gain is real on this metric**: +10pp avg@4 with p≈7e-05 under paired comparison.
   The improvement is in *per-sample reliability* (more of the 4 samples are correct), not in
   the probability that at least one sample is correct (pass@4 was already 50% for base).
2. **SFT warm start alone hurt** (17.5% avg@4 vs base 21.0%): a 234-step GSM8K SFT mostly taught
   output format (`####` rate 65% → 97%) without improving math accuracy. DAPO then recovered
   and exceeded the base model.
3. **Small-batch DAPO is noisy**: checkpoints oscillate ±5pp; the final point (31.0%) is at the
   high end of the 27–31% band. We report both the final checkpoint and the mean of the last five.
4. **Scale caveat vs the official claim**: the official talk reports g1k + 155 SFT + 1,000 DAPO
   steps: GSM8K avg@4 59.42→71.85 (+12.4pp). Their run is ~320× larger per step than ours
   (upstream DAPO reference uses 1,024 prompts × 5 samples per step ≈ 5.12M rollouts for 1,000
   steps; ours is 16k). Absolute numbers are therefore not comparable — but the **direction
   agrees**, and our result is public, reproducible, and license-clean.

## Artifacts

- Checkpoints: `global_step_100 … 1000` exported as HF policy dirs (on Snellius scratch)
- Eval JSONs: `results/b1-{100,200,…,1000}-*.json`, `results/avg-{base,mathsft,rl50}-*.json`
- Scripts: `tools/eval_gsm8k_avgk.py`, `tools/build_gsm8k_math_sft.py`; training recipe in the
  skyrl-rwkv fork (DAPO variant)
- Ecosystem context (verified): `reports/2026-11-10-verified-update.md`

## Limitations

- 200-question eval subset; pass@4 saturates at ~50% (100/200 questions unsolved by 4 samples for
  both models), so avg@4 is the informative metric.
- Single seed per configuration; small-batch variance means the exact +10pp point estimate is
  optimistic relative to the last-5 mean (+8.5pp).
- g1l-1.5B only; scaling to 2.9B/7.2B untested here.
- `dynamic_sampling=null` deviates from the DAPO paper; the filter was disabled after an
  all-zero-variance-batch crash, so this is DAPO minus dynamic sampling.
