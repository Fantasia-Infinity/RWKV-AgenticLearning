# DAPO vs SAO: strict matched comparison (GSM8K, G1l-1.5B)

> Date: 2026-11-12. Scope: only the parts of our two RL runs that can be matched
> strictly; everything else is listed as not comparable. Raw numbers:
> [`reports/data/2026-11-12-dapo-vs-sao-strict.json`](data/2026-11-12-dapo-vs-sao-strict.json).

## 0. Which runs are strictly comparable

Only the two 100-step runs can be paired:

| Algorithm | Job | Script | Steps | GPUs |
|---|---|---|---|---|
| DAPO | `29045605` | `recipes/dapo-gsm8k/run.sh` | 100 (ckpt@25/50/75/100) | 2×A100-40GB |
| SAO | `29143646` | `recipes/sao-gsm8k/run.sh` | 100 (ckpt@25/50/75/100) | 2×A100-40GB |

**Not comparable:** the DAPO **B1** run (`29048910`, 1,000 steps). Its `@100` checkpoint is
reported separately only as a *run-variance* reference, never as part of the algorithm comparison.

## 1. Identical dimensions (verified)

| Dimension | Value (both runs) |
|---|---|
| Base policy | math-SFT `p15-sft-29014001/hf_exports/global_step_234/policy` |
| Train data | GSM8K train, 7,473 prompts (same parquet) |
| Reward | exact `#### <number>` match (non-strict extraction, same env) |
| Sampling | temp=1.0, top_p=1.0, top_k=−1, max_gen=1,280, bot chat template, `logprobs=1` |
| Rollouts/step | 16 trajectories |
| Steps / checkpoints | 100 steps; 25 / 50 / 75 / 100 |
| Evaluation | `tools/eval_gsm8k_avgk.py`, **same 200 GSM8K test questions, same seed order, k=4, temp=1.0** |
| Metrics | avg@4 (primary), pass@4 |
| GPUs | 2×A100-40GB each |
| Dynamic-sampling filter | disabled in both (DAPO `dynamic_sampling=null`; SAO has no filter) |

Wall time incl. startup/export: DAPO **2 h 16 m**, SAO **3 h 21 m** (~1.5× due to the critic).

## 2. Differences that are *not* possible to match (must be disclosed)

| Dimension | DAPO-100 | SAO-100 |
|---|---|---|
| Algorithm | GRPO advantage + dual_clip PPO loss + token-mean + overlong filtering | `gae_adaptive` (α=1.5) + `rollout_is` loss |
| Critic | none | RWKV critic, NoRA r64, lr 5e-6, 2 critic epochs/rollout |
| Batch composition | **4 prompts × 4 samples** (group-relative) | **16 prompts × 1 sample** (token-level GAE) |
| Host memory | 64 GB | 120 GB |

The batch composition difference is structural: same 16 trajectories/step but DAPO sees 4 prompts
with 4 samples each (group advantage) while SAO sees 16 distinct prompts (token-level value
targets). Differences cannot be attributed to the algorithm alone.

## 3. Matched-step results (200 questions, k=4, temp=1.0)

| checkpoint | DAPO avg@4 | DAPO pass@4 | SAO avg@4 | SAO pass@4 | SAO − DAPO | paired p |
|---|---:|---:|---:|---:|---:|---:|
| step 25 | **30.50%** | 58.0% | 27.75% | 54.5% | −2.75pp | 0.137 (ns) |
| step 50 | 40.38% | 66.0% | **43.50%** | **71.5%** | +3.12pp | 0.201 (ns) |
| step 75 | **38.88%** | 68.0% | 28.62% | 51.5% | −10.25pp | 1.9e-05 |
| step 100 | **40.75%** | 66.5% | 28.12% | 49.5% | −12.62pp | 1.0e-07 |
| **mean of 4 ckpts** | **37.63%** | 64.6% | 32.00% | 56.8% | **−5.62pp** | **7.8e-05** |
| base (same eval) | 21.00% | 50.0% | — | — | — | — |
| vs base | **+16.62pp (p≈0)** | — | **+11.00pp (p=1.9e-08)** | — | — | — |

Statistical tests: per-question paired t-test, n=200, two-sided. "ns" = not significant.

## 4. Run-to-run variance (the key caveat)

| Run | Config | step-100 avg@4 | step-100 pass@4 |
|---|---|---:|---:|
| DAPO-100 (`29045605`) | batch 4×4, 2 GPU, 100 steps | **40.75%** | 66.5% |
| DAPO-B1 (`29048910`) | same config, 1,000 steps | **21.50%** | 45.0% |

**Two runs of the same DAPO configuration differ by 19.25pp at the same step and evaluation.**
This variance is larger than any algorithm difference measured here. (B1's own curve later rises:
400 steps 30.25%, final 1,000 steps 31.0%, last-5 mean 29.5%.)

## 5. What the strict comparison does and does not support

Supported:
1. Both algorithms significantly beat the base policy (DAPO +16.6pp, SAO +11.0pp at the
   4-checkpoint mean level).
2. On this single 100-step pair, the DAPO run has the higher mean (37.63% vs 32.00%, p=7.8e-05),
   while SAO has the higher single best checkpoint (43.5% vs 40.75%, difference not significant).
3. SAO costs ~1.5× wall time per step because of the critic forward/backward passes.

Not supported:
- Any claim that DAPO is better than SAO (or vice versa). With same-config DAPO runs differing by
  19pp at the same point, a single-seed ranking is not statistically meaningful.
- Comparisons of DAPO-B1 (1,000 steps) against SAO-100 (100 steps).

Reproduction: `python tools/eval_gsm8k_avgk.py --model <export> --out <json> --limit 200 --k 4 --temperature 1.0`;
the per-checkpoint JSONs are listed in the data file above.
