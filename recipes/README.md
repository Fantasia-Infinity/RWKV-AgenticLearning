# Recipes (reproducible launchers)

These are the launchers and configurations used for the results in
[`reports/2026-11-10-rl-results-summary.md`](../reports/2026-11-10-rl-results-summary.md)
and the two dedicated write-ups:

- DAPO (group-relative RL): [`reports/2026-11-10-dapo-gsm8k-rlvr.md`](../reports/2026-11-10-dapo-gsm8k-rlvr.md)
- SAO (critic-based RL): [`reports/2026-11-12-sao-gsm8k.md`](../reports/2026-11-12-sao-gsm8k.md)

## Provenance

Both `run.sh` files are modified copies of launchers from
[`rwkv-rs/skyrl-rwkv`](https://github.com/rwkv-rs/skyrl-rwkv) (Apache-2.0).
Our changes: GSM8K environment instead of UltraData, DAPO/Sao hyperparameters
scaled down to 2×A100-40GB, 16 rollouts/step, max_gen 1,280, prompt length 512,
checkpoint interval configurable via `CKPT_INTERVAL`, console logger.
The upstream project is not vendored here; install it first (see its README).

## Layout

| Path | Purpose |
|---|---|
| `dapo-gsm8k/run.sh` | DAPO on GSM8K (`advantage_estimator=grpo`, `policy_loss_type=dual_clip`, token-mean loss, overlong filtering) |
| `sao-gsm8k/run.sh` | SAO on GSM8K (`gae_adaptive`, `rollout_is`, critic NoRA r64) |
| `slurm/b1-dapo-1000.slurm` | 2×A100 template for the B1 DAPO run (1,000 steps) |
| `slurm/sao-gsm8k-2gpu-100.slurm` | 2×A100 template for the SAO run (100 steps, ckpt@25) |

Evaluation scripts live in [`tools/`](../tools): `eval_gsm8k.py` (greedy pass@1),
`eval_gsm8k_avgk.py` (avg@4/pass@4, the primary metric of the reports).

## Environment notes

- RWKV training requires `temperature=1.0` sampling (raw-logprob backend requires an unmodified
  rollout distribution); with `top_p=1`, `top_k=-1`.
- The model is a plain HF RWKV-7 export (`model_type="rwkv"` in config.json) so the critic wrapper
  can attach a value head; NoRA critics are supported only for `model_type="rwkv"`.
- DAPO with `dynamic_sampling=filter` crashed on all-zero-variance batches in our small-batch setup;
  the reported runs use `dynamic_sampling=null` (DAPO minus dynamic sampling).
- Host memory: 4-GPU colocated runs needed ≥120 GB host RAM; 2-GPU runs used 120 GB safely.
