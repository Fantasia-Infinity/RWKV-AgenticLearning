# ROADMAP — RWKV agentic RL

> Revised 2026-11-05 after the ecosystem audit (`reports/2026-11-05-verification.md`).
> The original plan assumed building the first multi-turn evaluation from scratch; the audit showed public assets
> that can be reused (No-22's 568-question agent exam, `browsecomp-plus-eval`'s 830-question package).

## Phase overview

| Phase | Weeks | Deliverable | Gate | Infrastructure |
|---|---|---|---|---|
| **P0 — baseline** | 0–3 | Freeze prompt/tool format; run the 568-question agent exam + the 830-question BrowseComp-Plus package on G1l / G1k; publish first RWKV agentic scores | G1 baseline reproducible | Reuse public assets (⚠️ No-22 assets are unlicensed) |
| **P1 — single-turn SFT** | 3–6 | Split trajectories into single steps; SFT with assistant-only mask | G2 tool-call parse rate > 99% | ✅ RWKV-PEFT / RWKV-SFT |
| **P2 — single-turn RLVR** | 6–10 | `skyrl-rwkv` + **DAPO** (not GRPO); deterministic checker as reward; Anti-Doom first | G3 single-turn RL > SFT | ✅ official recipe (155-step GSM8K warm-up + 1000-step DAPO) |
| **P3 — multi-turn rollout** | 10–17 | Plan B first: re-prefill episodes on `skyrl-rwkv` (~2 weeks); then Plan A: `wkvm` state slots | G4 ≥3-step episode runs end-to-end | ❌ ecosystem gap (only primitives exist) |
| **P4 — multi-turn RL** | 17–22 | Episode-level GRPO or turn-level GAE; process + outcome rewards | G5 multi-turn RL > single-turn | ⚠️ code exists upstream, never trained multi-turn |
| **P5 — scale** | 22+ | Megatron CPT to 7B/13B; connect τ-bench / BFCL | — | ✅ Megatron stack exists (28B = short-run evidence only) |

## Three non-negotiables (any path)

1. **Per-token log-probs must be persisted** for every generated token (trainer/rollout alignment); `wkvm` currently
   does not support logprobs, `skyrl-rwkv` does.
2. **Recurrent state must be invalidated after any policy weight update** — the upstream contract in
   `skyrl-rwkv/docs/rwkv/upstream-weight-sync-handoff.md` says: *"Recurrent state/cache slots must not survive a policy
   weight update"*; CUDA graphs must be discarded too.
3. **Per-turn loss mask**: observation tokens (tool outputs) must not contribute to the gradient.

## P0 in detail (first deliverable)

- **Assets to reuse**
  - `No-22-Github/RWKV-Agent`: 568-question exam (15 scenarios, per-question `verify.py`) + public baseline numbers
    (G1l 32.9%, NoRA 56.4%) — ⚠️ no license, evaluation only.
  - `rwkv-rs/browsecomp-plus-eval`: 830-question BrowseComp-Plus package (100-step search/get_document/final_answer
    loop, vendored vLLM-RWKV, official judge) — ⚠️ no license, no published scores.
- **Tasks**
  1. Freeze prompt/tool format (align with G1x function-call template).
  2. Run both suites against G1l / G1k baselines; publish per-category numbers (multi-step category is the gap).
  3. Record exact model/commit/harness hashes so scores are reproducible.
- **Exit criteria**: a public table of RWKV agentic scores with re-runnable configs; report which categories remain 0.

## Open questions (from the audit)

- Can `skyrl-rwkv` run on real 8 GPUs as-is? Static analysis says **not** on the current cluster: single-node
  8×96 GB Pro6000 recipe, hard `NUM_GPUS==8` in `examples/train/rwkv/eval/run.sh`, CUDA 13 (repo) vs 12.9 (cluster).
- Does the `feat/heli-r00-training-eval` branch merge into `main`? (bounded training/eval + `python -m helicopter
  checkpoint-result` callback; `rwkv-rs/Helicopter` repo is still 404.)
- Does `RWKV-Megatron`'s 28B distill branch produce a long run / checkpoint? (currently 30-step capacity evidence only.)
- Will the official org merge TLPO or other algorithms into `skyrl-rwkv`? (TLPO not present as of 2026-11-05.)

## Tracking cadence

Run the zero-API-quota tracker before each planning update:

```bash
bash tracking/check.sh --diff
```

Signals watched: `rwkv-rs` new repos, `skyrl-rwkv` branches (esp. `heli`), `vllm-rwkv` pin drift, `wkvm` LICENSE,
Megatron 28B evidence, standard-benchmark scores, official docs/roadmap, agent catalog changes.
See [`tracking/sources.md`](tracking/sources.md).
