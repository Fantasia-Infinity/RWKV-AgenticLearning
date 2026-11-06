# The RWKV ecosystem for agentic RL — a verified review (2026-11-05)

> Public, neutral version of the internal 2026-11-05 handoff. Every claim below is traceable to
> `reports/skyrl/`, `reports/state/`, `reports/eco/` and their `evidence/` directories. Confidence marks:
> ✅ verified by source · ⚠️ partially verified / needs qualification · ❌ refuted or corrected.

## Abstract

RWKV's **single-turn RLVR is mature** and officially organized. **Multi-turn agentic RL training is still a public
gap**: no public recipe, no public training result, no state-native rollout layer. But the ecosystem is fuller than
earlier audits suggested: the `rwkv-rs` organization alone publishes 40 repositories, including an earlier native
`verl` integration; community projects already publish a 568-question multi-turn agent exam with scores, and an
830-question BrowseComp-Plus evaluation package exists. Official G1l (2026-10-31) ships tool-call / multi-turn chat
templates and points users to the community agent catalog. The accurate framing is therefore: *the official
organization does not train agentic RL, but has standardized the agentic interface and delegated practice to the
community* — while public multi-turn RL training remains absent.

## 1. Scope & method

- Snapshot date: 2026-11-05. Sources: primary repositories, model cards, official docs; zero-API-quota method
  (`git ls-remote`, commit atom feeds, raw files, HTML).
- Three parallel workstreams: (a) `skyrl-rwkv` deep-dive, (b) state layer (`wkvm`) + Megatron scale, (c) ecosystem
  inventory (`rwkv-rs` org) + official channels.
- Confidence marks are used per claim; corrections to the prior audit are listed in §5.

## 2. The stack (L0–L5) and its license slope

| Layer | Representative projects | License trend |
|---|---|---|
| L0 architecture / weights | RWKV-LM (G1/G1l), official weights, RWKV-X | permissive |
| L1 kernels / serving | FlashRWKV2 (MIT), vllm-rwkv (Apache-2.0), transformer/tokenizer forks, fla-rwkv (MIT) | mostly permissive |
| L2 training / RL | RWKV-PEFT (Apache-2.0), OpenMOSE RLHF (Apache-2.0), RWKV-Megatron (Apache-2.0), `skyrl-rwkv` (Apache-2.0), `verl-rwkv` (Apache-2.0), `torchtitan-rwkv` (BSD-3), `Megatrwkv-Bridge` | mostly permissive |
| L3 inference / state | `rwkv_lightning` (**no license**), `wkvm` (**no license**), ai00_server (MIT), web-rwkv / rwkv.cpp | mixed |
| L4 agent runtimes | RWKV-Agent, RWKV-LH (MIT), RWKV-Scout (MIT) | mixed |
| L5 evaluation | toolcaller-bench (Apache-2.0), `rwkv-skills` (**no license**), `primitive-bench` (**no license**), `browsecomp-plus-eval` (**no license**) | **licensing gap widens toward the agent layer** |

**Implication:** the closer a component is to agents, the less likely it is to be commercially usable. This matters
for any product plan built on top of the ecosystem.

## 3. What is verified

### 3.1 Single-turn RLVR (mature, official)

- `rwkv-rs/skyrl-rwkv` — fork of NovaSky-AI/SkyRL, created 2026-08-30, active through 2026-10-31, Apache-2.0.
  Five launchers (antidoom/FTPO, flashreinforce, opd, sao, sft), algorithms GRPO/DAPO/CISPO/SAO/OPD/Anti-Doom/FTPO.
  Evaluation is math-only (`eval/prepare.py`: gsm8k / math_500 / aime24 / aime25 / aimo_progress_prize_1). ✅
- Official 2026-10-26 seminar numbers: GSM8K avg@4 59.42%→71.85% (+12.43 pp) with 155-step warm-up + 1000-step DAPO;
  MATH500 avg@8 39.88%→49.75%; anti-doom repetition 63→0; async OPD +29.4% throughput. ✅
- vLLM fork pin: `rwkv-rs/vllm-rwkv@2852a7b1d` (`pyproject.toml:584`), **public** repository, 2 commits behind
  HEAD `7a6adcc6`. The previously assumed `67f0c599` is an old commit (2026-08-04) not in the branch history. ✅
- CI: the fork inherits 16 workflows, **all** gated on `github.repository == 'NovaSky-AI/SkyRL'`; so the fork has no
  CI at all (the 3,354 lines of RWKV tests are real but never executed in CI). ✅

### 3.2 Earlier RWKV RL integration: `verl-rwkv`

- Fork of `verl-project/verl`, branch `rwkv`, created 2026-05-21 (101 days before `skyrl-rwkv`), last commit
  2026-08-02, Apache-2.0. Native `rwkv_lm` engine (EngineRegistry), RWKV7 GRPO launcher, MaxRL entry point, daily
  upstream rebase workflow; 43 RWKV files, 18 PRs. ✅
- Same main contributor as `skyrl-rwkv` (`Cai-z-us`) → the history reads as "verl-rwkv stopped, work moved to
  skyrl-rwkv". `skyrl-rwkv` is the *current* base, not the *only* one. ✅

### 3.3 Multi-turn tooling: code exists, training does not

- `skyrl-rwkv` has `use_conversation_multi_turn`, per-turn `loss_mask` (observation excluded), and
  `RWKVTrajectoryLogger`; **but `max_turns` is never set in RWKV recipes (default 1)**, and `skyrl-agent/` has zero
  RWKV references. ✅
- The `feat/heli-r00-training-eval` branch (8 commits, 2026-10-24→28, +516/−48) adds bounded training/evaluation
  phases and a scoreboard callback `python -m helicopter checkpoint-result <spec> train` in its README. The
  `rwkv-rs/Helicopter` repository itself is publicly **404** (GitHub, Codeberg, HF all checked). ✅
- `skyrl-rwkv` evaluation is math-only — **no agent tasks**. ✅

### 3.4 State layer: primitives exist, integration does not

- `xiaol/wkvm` (Apache-2.0 declared in `pyproject.toml`, **no LICENSE file**): per-request state slots with
  create/snapshot/fork/hibernate/resume; RWKV-7 state enumerated per layer (`recurrent_state` fp32, `conv_state`,
  `ffn_state`). Documented RWKV-7 numbers: 8,077 tok/s @B256 (1.5B), 2,000 hibernated sessions @2.29 MiB, p50 8.2 ms
  warm resume (⚠️ p99 explicitly excluded by the authors; single-run measurements; no independent reproduction).
- **`live-migrate` is not implemented** (`wkvm/server.py` exposes only `/v1/states` + `/v1/generate`; ROADMAP lists
  migration as deferred). ✅
- Chat API hard-rejects **tools / logprobs / custom stop** (`wkvm/gemma_server.py`), which blocks RL rollout use
  without a state-service integration. ✅
- Main branch froze after the technical-report publication (2026-08-02); the `m4-qwen35-hybrid` branch stayed active
  until 2026-09-10 (+12k lines, Qwen3.5 hybrid guest allocator). ✅

### 3.5 Scale: `RWKV-Megatron`

- Real Megatron-Core integration (ModuleSpec injection, TP/PP/SP/CP), Apache-2.0, default branch `muon` (last commit
  2026-07-06); branches `2026-10-10` (10-15), `codex/rwkv7-cp` (10-22), `codex/qwen-rwkv28b-distill` (10-30). ✅
- **28B evidence exists but is short-run capacity only**: on `codex/rwkv7-cp`, 4 layouts × 30 steps with machine-
  readable JSON (TP4/PP2/CP1: 75,829 MiB, 2.0712 s/step, final val CE 7.497223, no NaN/skip/OOM); the distill branch
  has 3 × 28B configs plus a capacity probe that explicitly "*does not save checkpoints or certify model quality*";
  `docs/`, `training-smoke/` are gitignored (0 files); the only 12-hour run in the org is **2.7B**, not 28B. ✅
  → Scale path = **exists + engineering partially proven; training effectiveness unproven**.

### 3.6 Evaluation layer

- `lm-evaluation-harness-rwkv` / `lighteval-rwkv` / `evalscope-rwkv` forks form a production evaluation pipeline
  (scoreboard publishing branches, resumable orchestration, HTTP backends). `benchmarks.toml` lists 16 benchmarks,
  with the **`agentic` category empty**. ✅
- `rwkv-rs/browsecomp-plus-eval` — reproducible 830-question BrowseComp-Plus package (search top-5 / get_document /
  final_answer, 100 steps, 3-way candidate router, vendored vLLM-RWKV, official judge). **No scores, no root LICENSE.** ✅
- `No-22-Github/RWKV-Agent` (outside the org) — public 568-question multi-turn agent exam (15 scenarios, per-question
  `verify.py`) with public baseline numbers: G1l base 187/568 = **32.9%**, NoRA adapter 320.5/568 = **56.4%**
  (⚠️ the NoRA number comes from a different/earlier base model — not a strict same-base comparison). Assets are
  **unlicensed**. ✅
- `rwkv-rs/rwkv-skills` mentions a public scoreboard in the "Helicopter repository" (which does not exist publicly);
  dashboard code exists in-repo but no public score data. ✅

### 3.7 Official positioning

- G1l (`rwkv7-g1l-13.3b-20261031`) chat template supports multi-turn and strict model-generated **tool-call**
  prompts; the official prompt-format documentation has a `function call` section; the official hub card and
  RWKV-LM README point to the community agent catalog as "*latest best practices for agentic work*". ✅
- At the same time, the official 2026-10-26 seminar describes a **single-turn RLVR** roadmap (math/reasoning/code),
  and the rwkv_lightning tutorial notes that real agent RL requires running tools yourself. ✅
- Correct framing: **official does not train agentic RL; it standardizes the interface and points to the community.**

## 4. What is still missing (the actual gap)

1. **Public multi-turn agentic RL training recipe/results** — current agent models are SFT/NoRA/MiSS adapters, not RL.
2. **Public scores on standard agent benchmarks** — BrowseComp-Plus 830 / τ-bench / BFCL have no RWKV numbers; the
   `agentic` category in the evaluation pipeline is empty.
3. **State-native rollout layer** — connect `wkvm` state slots → episode → per-token log-probs → reward, or use
   `skyrl-rwkv` re-prefill as the pragmatic first step.

## 5. Corrections to the prior internal audit (2026-11-05)

| Prior claim | Verified state |
|---|---|
| skyrl-rwkv binds a **private** vLLM fork at `67f0c599` | public `rwkv-rs/vllm-rwkv@2852a7b1d`; `67f0c599` is an old commit not in history |
| wkvm README only has Gemma numbers | RWKV-7 numbers are in-repo (`experiments/results/m2/m3`, `paper/CLAIMS.md`); but p99 is excluded by the authors |
| wkvm supports live-migrate | not implemented (deferred/refused in ROADMAP) |
| Megatron branch `codex/rwkv28b-distill` | actual name `codex/qwen-rwkv28b-distill`; 28B = short-run capacity only |
| `rwkv-rs/Helicopter` does not exist (404) | still 404 publicly, but the scoreboard contract appears in a public skyrl-rwkv branch; treated as internal/unpublished |
| "No agentic models, no scores" | No-22 publishes a 568-q exam with scores; browsecomp package exists (no scores) |
| "Official deliberately does not do agentic" | official standardized tool-call/multi-turn and points to the community; still no agentic RL training |
| only `howard-hou/RWKV-SFT` supports multi-turn SFT | No-22 trained multi-turn agent adapters with `rwkv_lightning_cuda`; skyrl code is multi-turn capable |
| FlashRWKV2 under `BlinkDL/` | moved to `rwkv-rs/FlashRWKV2`, MIT |
| `rwkv-rs` org has ~10 relevant repos | 40 public repos (17 source + 21 forks + 2 archived); 30 were missing from the prior map |
| skyrl-rwkv is the *only/best* RL base | `verl-rwkv` was an earlier native verl integration (2026-05→08); skyrl is the *current* one |
| CI missing only for RWKV tests | the whole fork has no CI (16/16 workflows gate on the upstream repo) |

## 6. Implications

- **If the goal is a stronger RWKV on verifiable tasks**: use `skyrl-rwkv` + DAPO, copy the official 155+1000 recipe.
  No need to touch the agent layer.
- **If the goal is agentic RL**: the parts exist but the assembly does not. Start by reusing the public evaluation
  assets (P0), then take the official single-turn RL path (P1–P2), then build the multi-turn rollout (P3: re-prefill
  first, state slots later). See [`ROADMAP.md`](../ROADMAP.md).

## 7. References

- `reports/2026-11-05-verification.md` — summary table + 12 corrections
- `reports/skyrl/REPORT.md`, `reports/state/REPORT.md`, `reports/eco/REPORT.md` — full evidence dossiers
- `data/eco-org-repos.txt` — 40-repo inventory
- `tracking/sources.md` — source layers and signals

---

## 8. Addendum（2026-11-06）：helicopter、v8/ROSA 与活跃度分层

本文件发布后 24 小时内出现三项需要修正/补充的信息，详见 [`../reports/2026-11-06-ecosystem-update.md`](../reports/2026-11-06-ecosystem-update.md)（含证据与复现命令）：

1. **`helicopter` 存在**：在 `w1c2j3/helicopter`（不是 `rwkv-rs` 下），是 5 管线 / 24 benchmark / 27 EvalScope agent 数据集的 leaderboard 编排框架 —— 但**无 LICENSE、0 star、2026-08-10 停更、从未公开分数、官方 harness 依赖 Docker**。因此"评测基建空白"应修正为"**基建存在但不可依赖、无公开成绩**"。
2. **新增 L6 前沿层 v8/ROSA**：`RWKV-LM/RWKV-v8/README.md` 列出 8 个社区 ROSA 项目（多数 MIT/Apache，3 个无许可证），是当前最活跃的方向；但**无官方 HF 权重、无 vLLM/RL/agent 栈**，故不影响本仓库近期的 v7 执行路线。
3. **活跃度分层**：v7 引擎侧在退潮、v8/ROSA 最活跃；v7 的 agent/RL 层由少数单人维持（Chase Jay、shiroko98、Alic-Li、No-22）。另发现 `Alic-Li/rwkv_lightning_cuda` 有 5 个 `Claude` 提交（含 RL 相关改动），提示上游 RL 代码的数值正确性需要独立门禁。

**对 §2 栈表的修正**：在 L0–L5 之外增加 **L6 前沿（v8/ROSA）**；L5 评测层补充 helicopter 作为"未公开的编排框架"。

---

## 9. Addendum 2（2026-11-06 晚）：agentic RL 已在私有侧运行

- `rwkv-org/rwkv-agent-eval`（2026-11-04 建，当天仍在提交，**无 LICENSE**）表明公开的 agent 评测框架正在搭建，
  但依赖 Harbor + Docker、私有 `rwkv-agent-pipeline` 与未发布 DSH commit 与训练数据 `mix-20261106`。
- `No-22-Github/dsh-rwkv-plugin`（无 LICENSE）把 RWKV-7 注册进 DeepSeek Harness（8 工具、XML 信封）。
- **对 §0/§4 的修正**：不是"没有 agentic RL"，而是"**公开配方与结果尚未发布；私有管线已在运行**"。
- 详见 [`../reports/2026-11-06-ecosystem-update.md`](../reports/2026-11-06-ecosystem-update.md) §9。
