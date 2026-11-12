# RWKV-7 G1l-1.5B agentic RL: consolidated results (2026-11-08 → 2026-11-12)

> All numbers from our own runs on Snellius (A100-40GB). Code: this repo (Apache-2.0).
> Weights: RWKV-7 G1l-1.5B-20261031 (Apache-2.0). GSM8K used for evaluation/training only.
> Machine-readable copy: [`reports/data/2026-11-10-summary.json`](data/2026-11-10-summary.json).

## 1. What was tested

| Stage | Setup | Purpose |
|---|---|---|
| P1.5 SFT v3 | 2,242 synthetic tool-call trajectories (6 categories), 3 iterations | teach fenced-JSON tool calls + tool discipline |
| G3 tool-call eval | 258 single-step tasks (held-in style) | did SFT learn tool selection? |
| held-out tool benchmark | 120 self-built tasks (calc/search/stats/direct, independent seed) | generalization of tool selection |
| GSM8K-calc | 7,473 GSM8K train → tool-call trajectories; 262 eval (multi-turn, `calc` tool) | does tool RL help math? |
| P3 / P3c tool RL | FlashREINFORCE multi-turn, answer-only reward (P3), +min-tool-calls shaping (P3c) | RL on multi-turn tool use |
| P2 plain GSM8K RLVR | math-SFT warm start → FlashREINFORCE 50 steps | RLVR without tools |
| **B1 DAPO** | math-SFT warm start → DAPO 1,000 steps (16 rollouts/step, 2×A100, ~16h) | RLVR with a stronger recipe |

## 2. Headline results

### ✅ Two positive RL lines: DAPO (group-relative) and SAO/PPO-style (critic-based)
- **DAPO, 1,000 steps**: avg@4 21.0% → 31.0% (+10.0pp, p=6.6e-05); pass@4 unchanged.
- **SAO (critic-based), 100 steps**: checkpoints 27.75 / **43.5** / 28.63 / 28.12%,
  **mean 32.0%** (best ckpt pass@4 71.5%); all checkpoints beat base significantly.
  Cost: ~1.6k rollouts vs DAPO's 16k, ~0.9k SBU vs ~4.1k.
- Both show large checkpoint-to-checkpoint variance (±5pp+); report means, not only best points.
- Details: [`2026-11-10-dapo-gsm8k-rlvr.md`](2026-11-10-dapo-gsm8k-rlvr.md) and
  [`2026-11-12-sao-gsm8k.md`](2026-11-12-sao-gsm8k.md).
- **Strict matched comparison (DAPO-100 vs SAO-100, same base/data/eval/2 GPU/100 steps):
  DAPO mean 37.63% vs SAO 32.00% (paired p=7.8e-05), but the same DAPO config varies 19.25pp
  between two runs at step 100 → no reliable single-seed algorithm ranking.
  See [`2026-11-12-dapo-vs-sao-strict.md`](2026-11-12-dapo-vs-sao-strict.md).**

### ✅ DAPO on plain GSM8K (details)
- **avg@4 (200 questions, k=4, temp 1.0): 21.0% → 31.0% (+10.0pp, paired t=3.99, p=6.6e-05)**
- pass@4 unchanged (50.0% → 50.5%, p=1.0) → RL improves per-sample reliability, not coverage
- last-5-checkpoint mean 29.5%; checkpoint variance ±5pp (small-batch DAPO)
- Report: [`2026-11-10-dapo-gsm8k-rlvr.md`](2026-11-10-dapo-gsm8k-rlvr.md)

### ✅ SAO (critic-based RL, gae_adaptive) aligns with and slightly exceeds DAPO
- Same base (math-SFT 234), same data, same eval as the B1 DAPO run; 16 prompts × 1 sample per step
  (same 16 trajectories/step), critic = RWKV + value head with NoRA r64.
- 100 steps on 2×A100 (~2.7 h): avg@4 = 27.75 / **43.5** / 28.63 / 28.12% at steps 25/50/75/100;
  mean 32.0% vs base 21.0%, math-SFT 17.5%, B1 DAPO final 31.0% and DAPO@50 40.4%.
- Best checkpoint 43.5% (pass@4 71.5%); SAO@50 vs DAPO@50 not significant (p=0.20), vs base p≈0,
  vs B1 final p=9.7e-08.
- Report: [`2026-11-12-sao-gsm8k.md`](2026-11-12-sao-gsm8k.md). Recipe: [`recipes/sao-gsm8k`](../recipes).

### ⚠️ FlashREINFORCE RLVR (50 steps) is not significant
- greedy pass@1: base 39.58% (1,319 q) → RL 41.39%; **+1.81pp, McNemar p=0.29** — not significant
- format rate 60.2% → 98.4% (the real, deterministic gain)
- avg@4 metric: base 21.0% → 26.0% (suggestive but same small-sample caveat)

### ❌ Multi-turn tool RL (P3/P3c) underperforms SFT
| Model | GSM8K-calc accuracy (262) | avg tool calls |
|---|---:|---:|
| base | 3.4% | 0.03 |
| **SFT warm start** | **42.0%** | 3.15 |
| P3 RL (100 steps) | 35.9% | 1.44 |
| P3c RL (50 steps, min-call shaping) | 38.6% | 2.97 |

- Answer-only RL learns a **tool-call shortcut** (calls per sample drop 3.15 → 1.44) and loses accuracy
- Held-out benchmark confirms degradation: tool-name accuracy **98.9% (SFT) → 82.2% (P3c)**, direct no-call rate 3.3% → 0%
- No-KL constraint of FlashREINFORCE blocked the usual KL-regularized fix; reward shaping only partially recovered

### ✅ SFT tool-call ability generalizes
- G3 tool-call tool-name accuracy: 21.6% (base) → **92.96%** (SFT v3), parse rate 100%
- held-out 120 tasks: tool-name **98.9%**, argument validity 100%

## 3. Interpretation

1. **RLVR can work on RWKV-1.5B — but the recipe matters.** FlashREINFORCE at 50 steps gave no
   significant greedy gain; DAPO at 1,000 steps gave a significant avg@4 gain (+10pp). The
   difference is consistent with the official report (g1k + 155 SFT + 1,000 DAPO steps:
   GSM8K avg@4 59.42 → 71.85, +12.4pp), though their scale is ~320× ours per step
   (upstream DAPO reference: 1,024 prompts × 5 samples = 5,120 rollouts/step vs our 16).
2. **SFT teaches format and tool selection extremely well** (G3 +71pp, held-out 98.9%) but a
   short math SFT does not improve math accuracy (avg@4 21 → 17.5). RL then recovers and exceeds
   the base on sampling reliability.
3. **Multi-turn tool RL is the hard part.** Answer-only rewards create shortcuts; no-KL
   FlashREINFORCE limits stabilizing tricks; held-out tool selection degrades. This is the
   clearest public negative result in the RWKV agentic-RL space and motivates process rewards /
   tool-call constraints / KL-capable algorithms for future work.
4. **Small-batch DAPO is noisy (±5pp)**. Report both final checkpoint and last-5 mean; do not
   over-read a single checkpoint.

## 4. Artifacts

Local (Snellius scratch): archive manifest at
`/scratch-shared/szhang2/rwkv-agentic/archive/2026-11-10/MANIFEST.md` — all 39 eval JSONs,
training logs, run directories and export checkpoints, plus deletable-obsolete list.
Key models: B1 final `runs/p2b-dapo-29048910/exports/global_step_1000/policy`; math-SFT
`runs/p15-sft-29014001/hf_exports/global_step_234/policy`; P2 RL
`runs/p2-gsm8k-rlvr-29019986/exports/global_step_50/policy`.

SAO checkpoints: `runs/sao-gsm8k-29143646/exports/global_step_{25,50,75,100}/policy` (2×A100 run);
evaluations in `results/sao-{25,50,75,100}-*.json`.

Launchers: [`recipes/dapo-gsm8k`](../recipes/dapo-gsm8k), [`recipes/sao-gsm8k`](../recipes/sao-gsm8k),
[`recipes/slurm`](../recipes/slurm). Scripts: `tools/eval_gsm8k_avgk.py`, `tools/eval_gsm8k.py`, `tools/build_gsm8k_math_sft.py`,
`tools/build_gsm8k_calc.py`, `tools/gen_sft_traj/`, `tools/build_heldout_tool_eval.py`,
`tools/sync_rwkv_chat_template.py` + regression test.

## 5. Caveats

- 200-question eval subset for avg@4 (1319 for greedy pass@1); single seed per configuration.
- g1l-1.5B only; 2.9B/7.2B untested.
- SAO run: 100 steps, one seed, scaled-down official config (batch 16 vs 128, 2 GPUs vs 8,
  512 vs 24,576 context, no UltraData, no offline critic pretraining); treat as direction/feasibility.
- DAPO ran with `dynamic_sampling=null` (filter crashed on all-zero-variance batches); i.e. DAPO
  minus dynamic sampling.
- External official numbers (59.42 → 71.85) are talk-level claims with undisclosed batch/GPU
  settings; not reproduced here.
