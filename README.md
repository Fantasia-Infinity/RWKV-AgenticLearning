# RWKV-AgenticLearning

**Verifiable research on RWKV agentic reinforcement learning** — ecosystem audit, SFT/RL experiments on RWKV-7 G1l-1.5B, multi-turn tool-use evaluation, and fully reproducible recipes.

> **Status:** results update `2026-11-20`. Since the founding audit snapshot (2026-11-05) this repository has run and published its own SFT/RL experiments on **RWKV-7 G1l-1.5B**: tool-call SFT, multi-turn tool RL (negative result), DAPO RLVR (+31.0% avg@4), and critic-based SAO (32.0% mean avg@4). All numbers below are from our runs; every claim links to a report with commands, result JSONs and cluster-local checkpoint paths (produced checkpoints are not published). Experiments are currently paused.

---

## Why this exists

RWKV's **single-turn RLVR is mature** (official `skyrl-rwkv`: GRPO/DAPO/CISPO/SAO/OPD/Anti-Doom, async RLVR, reward-checked math; published recipe-level gains). **Multi-turn agentic RL** — tool-using episodes, per-token log-probs across turns, episode-level training with stable state — remains the public gap: prior public RWKV agent scores are **mostly SFT adapters**; the few RL/benchmark data points are No.22's Search-R1 **0.407** and Terminal-Bench 2.0 **0/8**, still with no standard multi-turn tool benchmark coverage.

This repository does three things:

1. **Audits the ecosystem** (what exists, what is claimed, how to verify it).
2. **Runs reproducible SFT/RL experiments** on a small Apache-2.0 RWKV-7 model and publishes both positive and negative results.
3. **Ships the code** — data builders, eval scripts, training recipes, SLURM templates, and a static HTML report site.

**Scope note on priority.** The official `skyrl-rwkv` stack already reports positive RLVR gains; we do **not** claim algorithm or ecosystem priority. Our contribution is a **public, reproducible positive RLVR result at 1.5B** with code, recipes and JSON. The multi-turn tool RL result is our negative-result contribution to the public record.

## Results at a glance (2026-11-08 → 2026-11-12)

Model: **RWKV-7 G1l-1.5B** (2026-10-31, Apache-2.0, latest G1 generation at 1.5B). Eval unless noted: GSM8K, **avg@4 = 200 questions × k=4 samples at temp 1.0** (same protocol as the official RWKV RLVR talk); greedy pass@1 on 1,319 questions where noted.

| Experiment | Setup | Result | Verdict |
|---|---|---|---|
| **Tool-call SFT (P1.5 v3)** | 2,242 synthetic trajectories, 3 iterations | G3 tool-name **21.6% → 92.96%**, parse 100%; held-out 120 (same generators, new seed): 90 tool tasks → tool-name **98.9%**, args 100%; 30 direct → only **3.3%** correct no-call | ✅ SFT generalizes to held-out samples from the same task generators |
| **GSM8K-calc multi-turn SFT** | 7,473 GSM8K → `calc` tool trajectories; 262 eval | base **3.4%** → SFT **42.0%**, avg **3.15** tool calls | ✅ strong SFT baseline |
| **P3 multi-turn tool RL (answer-only)** | FlashREINFORCE, 100 steps | accuracy **35.9%**, avg calls **1.44** (collapse) | ❌ answer reward kills tool use |
| **P3c multi-turn tool RL (reward shaping)** | FlashREINFORCE + min-tool-calls shaping, 50 steps | accuracy **38.6%**, avg calls **2.97** | ❌ partial recovery, still below SFT |
| **Held-out tool benchmark** | 120 tasks from the **same generators, new seed** (90 tool + 30 direct) | tool-name **98.9% (SFT) → 82.2% (RL)** over the 90 tool tasks; direct no-call 3.3% → 0% | ❌ RL degrades held-out tool selection |
| **Plain GSM8K base** | greedy, 1,319 q | pass@1 **39.58%** (format 60.2%); avg@4 21.0% | — baseline |
| **Math-SFT warm start** | 7,473 solutions, 234 steps | greedy 40.5% (200 q); avg@4 17.5% | SFT learns format, not math |
| **FlashREINFORCE RLVR** | 50 steps, math-SFT start | greedy **41.39%** vs 39.58% (+1.81pp, **p=0.29 ns**); format 60→98% | ⚠️ not significant |
| **DAPO RLVR** | 1,000 steps, 16 rollouts/step, 2×A100, ~16h | **avg@4 21.0% → 31.0% (+10.0pp, p=6.6e-05)**; pass@4 50.0→50.5 (ns) | ✅ positive RLVR reproduced on G1l-1.5B |
| **SAO (critic-based RL)** | 100 steps, `gae_adaptive` + NoRA critic, 2×A100, ~3h | avg@4 **27.75 / 43.5 / 28.63 / 28.12%** at steps 25/50/75/100, **mean 32.0%**, best pass@4 71.5% | ✅ positive; ~1.6k rollouts |
| **DAPO vs SAO (strict matched)** | both 2×A100, 100 steps, ckpt@25/50/75/100, same base/data/eval | DAPO-100 mean **37.63%** vs SAO **32.00%** (p=7.8e-05); same DAPO config varies **19.25pp** between two runs | ⚠️ no reliable single-seed ranking |

**Compute (this phase):** ≈**12,171 SBU** used since 2026-11-07; project balance ≈**108,481 SBU** — ≈**90%** of the 120,652 SBU phase-start balance and ≈**60%** of the original 180,000 SBU allocation. The DAPO 1,000-step run ≈4.1k SBU; the SAO 100-step run ≈0.9k SBU incl. evals.

Headline reports: [`reports/2026-11-10-rl-results-summary.md`](reports/2026-11-10-rl-results-summary.md) ·
[`reports/2026-11-10-dapo-gsm8k-rlvr.md`](reports/2026-11-10-dapo-gsm8k-rlvr.md) ·
[`reports/2026-11-12-sao-gsm8k.md`](reports/2026-11-12-sao-gsm8k.md) ·
[`reports/2026-11-12-dapo-vs-sao-strict.md`](reports/2026-11-12-dapo-vs-sao-strict.md) ·
machine-readable: [`reports/data/2026-11-10-summary.json`](reports/data/2026-11-10-summary.json), [`reports/data/2026-11-12-dapo-vs-sao-strict.json`](reports/data/2026-11-12-dapo-vs-sao-strict.json).

### What the results mean

1. **RLVR works on RWKV-1.5B — but the recipe and budget matter.** FlashREINFORCE at 50 steps added nothing significant; DAPO at 1,000 steps added **+10pp avg@4**; SAO (critic-based) reached a similar range with **1/10 of the rollouts** (1.6k vs 16k) in 100 steps.
2. **Checkpoint variance dominates single-run comparisons** (±5pp; the same DAPO configuration differed by 19.25pp between two runs at step 100). Report means over checkpoints, not best points.
3. **SFT teaches format/tool selection extremely well, but multi-turn tool RL is the hard part.** Note that our held-out set reuses the P1.5 task generators with a **new seed** — it measures held-out-sample generalization, not generalization to novel task types or unseen tools. Answer-only rewards still produce a tool-call shortcut and degrade even this same-generator held-out tool selection. This is the clearest public RWKV *negative* result and the motivation for process rewards / tool constraints / KL-capable algorithms next.
4. **Repo is license-clean and reproducible**: Apache-2.0 weights, our own code, GSM8K for train/eval; external ecosystem claims are cited, never copied.

## Ecosystem audit findings (2026-11-05, still relevant)

1. **The ecosystem map was incomplete.** `rwkv-rs` alone has **39 public repositories** (as of 2026-11-18; `torchtitan-rwkv` → `torchtitan-rwkv-old` in November, training mainline moved to `Megatrwkv-Bridge`). A previous audit missed 30 of them.
2. **"No agentic models, no scores" is partly wrong.** The official `rwkv-agent-eval` released a 1,019-question multi-turn agent exam in November (SFT/NoRA adapters: base 30.9% → 52.8%, later **58.7** with more SFT data — still **SFT, not RL**; repository has **no LICENSE**). Outside the org, `No-22-Github/RWKV-Agent` publishes a 568-question exam with numbers.
3. **The official position is nuanced**: the official org does not train agentic RL itself, but it standardized the agentic interface (chat templates, tools, DSH plugin tutorial) and delegates practice to the community.
4. **What is still blank**: public multi-turn **tool-use RL** results on standard benchmarks (our P3 is still the only public negative evidence; the label-side `end_target: 0` fix landed in `rwkv_lightning_cuda` #27, but no multi-turn tool-RL result exists), public RWKV scores on τ-bench / BFCL / SWE-bench (only Terminal-Bench 2.0 0/8 and Search-R1 0.407 are public), and a state-native rollout layer.
5. **The audit corrected 12 factual claims** (vLLM pin, wkvm `live-migrate`, Megatron 28B evidence, missing Helicopter scoreboard, …). Full table in [`reports/2026-11-05-verification.md`](reports/2026-11-05-verification.md); weekly deltas in `reports/2026-11-*.verified-update.md`.

## Repository layout

```
├── docs/
│   ├── ecosystem-review-2026-11-05.md   # public ecosystem review (the neutral handoff)
│   └── methodology.md                   # evidence standard & confidence marks
├── reports/
│   ├── 2026-11-05-verification.md       # audit: 5 open questions resolved, 12 corrections
│   ├── 2026-11-06-ecosystem-update.md   # delta: helicopter found, v8/ROSA frontier, activity tiers
│   ├── 2026-11-10-rl-results-summary.md # consolidated SFT/RL results (positive + negative) + artifacts
│   ├── 2026-11-10-dapo-gsm8k-rlvr.md    # DAPO 1000 steps: avg@4 21.0→31.0 (+10pp, p=6.6e-05)
│   ├── 2026-11-12-sao-gsm8k.md          # SAO critic RL 100 steps: mean avg@4 32.0, best 43.5
│   ├── 2026-11-12-dapo-vs-sao-strict.md # strict matched DAPO-100 vs SAO-100 + variance caveat
│   ├── 2026-11-12-…                     # 2026-11-1x verified ecosystem updates (deltas + corrections)
│   ├── data/                            # machine-readable summaries of the experiments
│   └── skyrl/ state/ eco/               # deep-dives (skyrl-rwkv, wkvm/Megatron, repo inventory) + evidence
├── site/                                # 32 HTML report pages (built from Markdown)
├── tracking/
│   ├── sources.md                       # source layers / signals / distortion & license log
│   ├── repos.txt                        # 39 rwkv-rs repos + external repos of interest
│   ├── check.sh                         # zero-GitHub-API snapshot script
│   └── runs/                            # dated snapshots
├── recipes/                             # reproducible launchers: DAPO + SAO on GSM8K, SLURM templates
├── tools/                               # data builders + eval + chat-template sync/regression tests
├── data/                                # ecosystem tables (39-repo org table, official catalog)
└── ROADMAP.md                           # P0–P5 plan (revised after the audit)
```

> All reports have HTML versions: [`site/index.html`](site/index.html) (Markdown remains the source of truth).

> The original internal handoff is kept in a private archive and is **not** part of the public repository. `docs/ecosystem-review-2026-11-05.md` is the public, neutral rewrite.

## Reproduce

```bash
git clone https://github.com/Fantasia-Infinity/RWKV-AgenticLearning.git
cd RWKV-AgenticLearning

# 1) ecosystem snapshot (≈90 s, zero GitHub API calls)
bash tracking/check.sh
bash tracking/check.sh --diff        # delta since the previous snapshot

# 2) rebuild the HTML report site (needs `pip install markdown`)
python tools/build_report_site.py --out site

# 3) inspect our results (no GPU needed)
#    summaries + evidence JSONs live in reports/data/
```

Training recipes are reproducible end-to-end, but **produced checkpoints stay on the cluster** and are not published as public weights. They need a `skyrl-rwkv` checkout and a recent RWKV-7 HF export — see
[`recipes/README.md`](recipes/README.md) for the exact DAPO / SAO settings, hardware
(2×A100-40GB) and the environment constraints (sampling temperature must stay 1.0 for
the RWKV raw-logprob backend; NoRA critic requires `model_type="rwkv"`; host RAM ≥120 GB
for 4-GPU colocated runs).

## Artifacts & availability

**Public in this repository**
- training recipes (`recipes/`), data builders and eval scripts (`tools/`), SLURM templates;
- all result JSONs (`reports/data/` summaries; per-checkpoint eval JSONs are summarized in the reports);
- reports (Markdown) and their HTML build (`site/`), ecosystem tracking data.

**Not public**
- training checkpoints and training logs: they remain on the Snellius scratch filesystem
  (`runs/...`; each report lists the exact paths) and are **not** released as public weights;
- environment-specific Slurm scripts and cluster paths.

Base model weights are the official **RWKV-7 G1l-1.5B-20261031** (Apache-2.0) from Hugging Face; all fine-tuned/RL
checkpoints in this project are derived from it and are cluster-local.

## Evidence policy (short version)

Every claim in `reports/` is backed by a command output, a timestamp, and a URL/commit. We do **not** redistribute
third-party full texts: removed copies are recorded in `ARCHIVED.tsv` files with **sha256**, so anyone can re-fetch
and verify them byte-for-byte. External numbers (e.g. the official 58.7 SFT score) are cited, never reused.
See [`reports/EVIDENCE.md`](reports/EVIDENCE.md) and each `evidence/CITATIONS.md`.

## Roadmap (status as of 2026-11-20)

| Phase | Deliverable | Status |
|---|---|---|
| P0 audit | verified ecosystem map, signal tracker | ✅ done (2026-11-05, kept current by verified updates) |
| P1 single-turn SFT | tool-call + math SFT data + training | ✅ done (G3 tool-name 92.96%; held-out tool-name 98.9% over 90 same-generator tasks) |
| P2 single-turn RLVR | DAPO on GSM8K | ✅ done (avg@4 +10.0pp, p=6.6e-05) |
| P2b critic RL | SAO on GSM8K (with a critic) | ✅ done (mean avg@4 32.0%; best 43.5%) |
| P3 multi-turn tool RL | GSM8K-calc multi-turn | ❌ negative (RL < SFT; tool-call shortcut) |
| P4 evaluation & public delivery | held-out benchmark, reports, HTML site | ✅ mostly done; expand held-out tasks next |
| P5 scale | 2.9B / 7.2B, standard agent benchmarks | ⏸ paused (needs new budget decision) |

Details and the three non-negotiables (per-token log-probs, state invalidation after weight updates, per-turn loss mask):
[`ROADMAP.md`](ROADMAP.md).

## Scope & status

- Research notes are written in Chinese (the original working language); top-level docs are in English.
- **Experiments are paused** (2026-11-20). All published numbers come from our own runs; nothing here is a benchmark claim beyond the stated protocol.
- Third-party content remains under its own license; several interesting upstream repos have **no LICENSE** (`rwkv-agent-eval`, `rwkv_lightning_cuda`, `any2rwkv`, `browsecomp-plus-eval`) — we cite them but do not reuse their code/data.
- See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for license details.

## License

Apache-2.0 for this repository's own content. Third-party quotations are attributed and not redistributed in full.

---

## 中文摘要

**RWKV agentic RL 的可核验研究仓库**：生态审计 + 在 RWKV-7 G1l-1.5B 上可复现的 SFT/RL 实验 + 多轮工具评测 + 全部公开配方。

**为什么做**：RWKV 的**单轮 RLVR 已成熟**（官方 `skyrl-rwkv` 提供 GRPO/DAPO/CISPO/SAO/OPD/Anti-Doom 等）；而**多轮 agentic RL**（工具使用回合、逐 token logprob、episode 级训练）仍是公开空白——此前公开的 RWKV agent 成绩全部是 **SFT 适配器**，不是 RL。

**我们的结果（2026-11-08 → 11-12，G1l-1.5B，Apache-2.0）**：

| 实验 | 结果 | 判定 |
|---|---|---|
| 工具调用 SFT（P1.5 v3） | G3 tool-name **21.6%→92.96%**，parse 100%；自建 held-out 120 题（**同生成器、新 seed**）：90 工具题 tool-name **98.9%**，30 direct 题仅 **3.3%** 正确不调工具 | ✅ 同生成器 held-out 样本上泛化（非全新任务泛化） |
| GSM8K-calc 多轮 SFT | 262 题：base 3.4% → **SFT 42.0%**，平均 **3.15** 次工具调用 | ✅ 强 SFT 基线 |
| P3 多轮工具 RL（纯答案奖励） | FlashREINFORCE 100 步：准确率 **35.9%**，平均调用 **1.44** 次（坍缩） | ❌ 答案奖励导致工具调用偷懒 |
| P3c 多轮工具 RL（奖励塑形） | FlashREINFORCE + 最少调用塑形 50 步：准确率 **38.6%**，平均 **2.97** 次 | ❌ 部分修复，但仍低于 SFT |
| held-out 工具集 | 120 题（**同生成器、新 seed**；90 工具 + 30 direct）：tool-name 98.9%→**82.2%**；direct 不调工具率 3.3%→0% | ❌ RL 降低 held-out 工具选择 |
| DAPO RLVR（1000 步，2×A100，~16h） | GSM8K **avg@4 21.0%→31.0%（+10.0pp，p=6.6e-05）**；pass@4 不变（50.0→50.5） | ✅ 在 G1l-1.5B 上复现正向 RLVR |
| SAO critic RL（100 步，2×A100，~3h） | avg@4 27.75/43.5/28.63/28.12，**均值 32.0%**，best pass@4 71.5%；rollout 数仅 1.6k | ✅ 正向、成本更低 |
| DAPO vs SAO 严格对照 | 同为 100 步/同基座/同数据/同评测：DAPO 均值 37.63 vs SAO 32.00（p=7.8e-05）；但同 DAPO 配置两次 run 相差 **19.25pp** | ⚠️ 单 seed 排名不可靠 |

**关键结论**：RLVR 在 1.5B 上有效，但**配方与预算决定成败**（50 步 FlashREINFORCE 无显著增益；1000 步 DAPO +10pp；SAO 用 1/10 rollout 达到同区间）；**检查点方差 ±5pp 且同配置可差 19pp**，必须报告多点均值；**SFT 教格式与工具选择极强，多轮工具 RL 是最难的一环**（答案级奖励导致工具调用偷懒）。需注意：held-out 集与训练**同一批任务生成器**、只换 seed，只能说明"同生成器新样本泛化"，不能说明"全新任务/工具泛化"。

**生态审计（2026-11-05，持续更新）**：`rwkv-rs` 组织现有 **39 个公开仓库**；官方 `rwkv-agent-eval` 的 1,019 题多轮 agent 考卷已发 SFT 分数（30.9%→52.8%，后到 **58.7**，仍**非 RL**，且仓库**无 LICENSE**）；**仍空白**的是公开的多轮 agentic RL 配方/结果、标准 agent benchmark 分数、state-native rollout 层。审计纠正了 12 处事实，详见 [`reports/2026-11-05-verification.md`](reports/2026-11-05-verification.md)。

**表述边界**：官方 `skyrl-rwkv` 已报告正向 RLVR 增益；本仓库不主张算法或生态首创权，贡献是**在 1.5B 上公开、可复现的正向 RLVR 结果**（含配方/脚本/JSON）。

**怎么用**：`bash tracking/check.sh` 约 90 秒打一份生态快照（不消耗 GitHub API 配额），`--diff` 看变化；`python tools/build_report_site.py --out site` 重建全部报告的 HTML 版（入口 [`site/index.html`](site/index.html)）；训练配方见 [`recipes/`](recipes/)。**证据政策**：不重新分发第三方全文，删除的副本以 sha256 记录，可随时重抓校验。**许可**：自有内容 Apache-2.0；第三方引用均署名。

---

*Founding snapshot: 2026-11-05 · results update: 2026-11-20 · maintained by [@Fantasia-Infinity](https://github.com/Fantasia-Infinity)*
