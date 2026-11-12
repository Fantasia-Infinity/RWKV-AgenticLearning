# RWKV-AgenticLearning

**Verifiable research on RWKV agentic reinforcement learning** — ecosystem audit, multi-turn agent evaluation, and rollout/RL groundwork.

> **Status:** founding snapshot `v0.1.0` (2026-11-05). This repository publishes a verified cross-section of the RWKV ecosystem and the evidence behind it. It is a research/audit repository, not a model release.

---

## Why this exists

RWKV's **single-turn RLVR is mature**: the official organization ships a full RL stack (`skyrl-rwkv`: GRPO/DAPO/CISPO/SAO/OPD/Anti-Doom, async RLVR, reward-checked math) and has published recipe-level results (GSM8K +12.43 pp, etc.).

**Multi-turn agentic RL — tool-using episodes, per-token log-probs across turns, episode-level training — is still a public gap.** There is no public recipe, no public training result, and no state-native rollout layer connecting a state manager to an RL trainer.

Before building in that gap, we audited the ecosystem. This repo is the audit: what exists, what is missing, what is only claimed, and how to check every claim.

## Key findings (2026-11-05)

1. **The ecosystem map was incomplete.** The `rwkv-rs` organization alone has **40 public repositories** (17 source + 21 forks + 2 archived); a previous audit missed 30 of them. The missing layer includes `verl-rwkv` (a *native verl* RWKV RL integration, 43 RWKV files / 18 PRs, created 2026-05-21, stopped 2026-08-02), `torchtitan-rwkv` (active 2026-10-31), `Megatrwkv-Bridge`, evaluation forks, quantization, and a Rust full stack.
2. **"No agentic models, no scores" is partly wrong.** Outside the official org, `No-22-Github/RWKV-Agent` publishes a **568-question multi-turn agent exam** with public numbers: G1l base model 187/568 = **32.9%**, a NoRA adapter 320.5/568 = **56.4%** (⚠️ different base model, not a strict same-base comparison). `rwkv-rs/browsecomp-plus-eval` is a complete reproducible **830-question BrowseComp-Plus** evaluation package — but it publishes **no scores**.
3. **The official position is more nuanced than "no agentic".** G1l (released 2026-10-31) ships chat templates with multi-turn / strict tool-call support, and official docs now point users to the community agent catalog. The accurate statement is: **the official org does not train agentic RL itself, but it has standardized the agentic interface and delegated practice to the community.**
4. **What is still blank is specific:** public multi-turn agentic RL training recipes/results, public RWKV scores on standard agent benchmarks (BrowseComp-Plus 830 / τ-bench / BFCL), and a state-native rollout layer.
5. **The audit corrected 12 factual claims** — including the vLLM pin (`2852a7b1d`, not `67f0c599`; public, not private), wkvm's unimplemented `live-migrate` (and its RWKV-7 numbers *do* exist in-repo), Megatron's 28B branch (real short-run capacity runs, no long-run/convergence evidence), and the still-publicly-missing "Helicopter" scoreboard (its contract appears in a public `skyrl-rwkv` branch). Full table in [`reports/2026-11-05-verification.md`](reports/2026-11-05-verification.md).

## Repository layout

```
├── docs/
│   ├── ecosystem-review-2026-11-05.md   # public ecosystem review (the neutral handoff)
│   └── methodology.md                   # evidence standard & confidence marks
├── reports/
│   ├── 2026-11-05-verification.md       # summary: 5 open questions resolved, 12 corrections
│   ├── 2026-11-06-ecosystem-update.md   # delta: helicopter found, v8/ROSA frontier, activity tiers
│   ├── 2026-11-10-verified-update.md    # PR #20/#21, irwkv PR states, NextTransformer #38 (with corrections)
│   ├── 2026-11-10-dapo-gsm8k-rlvr.md    # DAPO 1000 steps on G1l-1.5B: avg@4 21.0→31.0 (+10pp, p=6.6e-05)
│   ├── 2026-11-10-rl-results-summary.md # consolidated SFT/RL results (positive + negative) + artifacts
│   ├── 2026-11-11-verified-update.md    # irwkv #7/#4 merged; FlashRWKV2 a19 (NaN fix + large batch); daily-check corrections
│   ├── 2026-11-12-sao-gsm8k.md          # SAO (critic RL) on GSM8K: avg@4 27.8/43.5/28.6/28.1, mean 32.0 vs base 21.0
│   ├── 2026-11-12-verified-update.md    # eval 58.7 (7.2B SFT) / loss breakdown / hashline negative / 3 open eval PRs
│   ├── data/2026-11-10-summary.json     # machine-readable summary of all results
│   ├── skyrl/  REPORT.md + evidence/    # skyrl-rwkv deep-dive (CI, pin, multi-turn, 8×GPU)
│   ├── state/  REPORT.md + evidence/    # wkvm, RWKV-Megatron 28B, Helicopter traces
│   └── eco/    REPORT.md + evidence/    # 40-repo inventory + new signals
├── tracking/
│   ├── sources.md                       # 3 source layers / 8 signals / distortion log
│   ├── repos.txt                        # 35 tracked repositories
│   ├── check.sh                         # zero-GitHub-API snapshot script
│   └── runs/                            # dated snapshots
├── recipes/                            # reproducible launchers (DAPO, SAO on GSM8K) + SLURM templates
├── site/                               # 全部报告的 HTML 版本（由 tools/build_report_site.py 生成）
├── tools/
│   ├── sync_rwkv_chat_template.py       # sync post-PR#20 chat template (pinned sha256)
│   ├── test_chat_template.py            # CPU regression: tool-call history rendering
│   └── gen_sft_traj/                    # synthetic agent-trajectory generators (P1.5)
├── data/eco-org-repos.txt               # full 40-repo table
├── data/rwkv-cn-eco-projects-2026-11-06.tsv  # official catalog (95 projects)
└── ROADMAP.md                           # P0–P5 plan (revised after the audit)
```

> 所有报告的 HTML 版本见 [`site/index.html`](site/index.html)（Markdown 源文件仍是事实来源）。

> The original internal handoff is kept in a private archive and is **not** part of the public repository. `docs/ecosystem-review-2026-11-05.md` is the public, neutral rewrite.

## Quick start

```bash
git clone https://github.com/Fantasia-Infinity/RWKV-AgenticLearning.git
cd RWKV-AgenticLearning

# Snapshot the tracked ecosystem (≈90 s, zero GitHub API calls)
bash tracking/check.sh

# Only show the delta since the previous snapshot
bash tracking/check.sh --diff
```

The tracker uses only `git ls-remote`, commit `.atom` feeds, `raw.githubusercontent.com` and GitHub HTML —
so it does not consume the 60/h unauthenticated API quota.

## Evidence policy (short version)

Every claim in `reports/` is backed by a command output, a timestamp, and a URL/commit. We do **not** redistribute
third-party full texts: removed copies are recorded in `ARCHIVED.tsv` files with **sha256**, so anyone can re-fetch
and verify them byte-for-byte. See [`reports/EVIDENCE.md`](reports/EVIDENCE.md) and each `evidence/CITATIONS.md`.

## Roadmap (summary)

| Phase | Weeks | Deliverable | Gate |
|---|---|---|---|
| P0 baseline | 0–3 | Reuse the 568-q agent exam + 830-q BrowseComp-Plus package; freeze prompt/tool format; first public RWKV scores | G1 reproducible baseline |
| P1 single-turn SFT | 3–6 | Tool-call traces → single-step SFT | G2 tool-call parse > 99% |
| P2 single-turn RLVR | 6–10 | `skyrl-rwkv` + DAPO (official recipe) | G3 RL beats SFT |
| P3 multi-turn rollout | 10–17 | Plan B: re-prefill on `skyrl-rwkv` → Plan A: state slots (`wkvm`) | G4 ≥3-step episode runs |
| P4 multi-turn RL | 17–22 | Episode-level GRPO / turn-level GAE | G5 multi-turn RL beats single-turn |
| P5 scale | 22+ | Megatron CPT to 7B/13B; τ-bench / BFCL | — |

Details and the three non-negotiables (per-token log-probs, state invalidation after weight updates, per-turn loss mask):
[`ROADMAP.md`](ROADMAP.md).

## Scope & status

- Research notes are written in Chinese (the original working language); top-level docs are in English.
- Static analysis only for now: no GPU runs were executed for this audit. The open "can it run on 8 GPUs" item is documented with its blockers (single-node 8×96 GB recipe, hard `NUM_GPUS==8` gate, CUDA 13 vs cluster 12.9).
- Third-party content remains under its own license; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## License

Apache-2.0 for this repository's own content. Third-party quotations are attributed and not redistributed in full.

---

## 中文摘要

**RWKV agentic RL 的可核验研究仓库**：生态审计、多轮 agent 评测、rollout/RL 前期准备。

**为什么做**：RWKV 的单轮 RLVR 已成熟（官方 `skyrl-rwkv` + DAPO 配方，GSM8K +12.43pp）；多轮 agent 的**公开结果刚刚出现，但全部是 SFT**——2026-11-07 `rwkv-org/rwkv-agent-eval` 发布首批公开多轮 agent 评测（1019 题配对 **30.9%→52.8%，+21.9±3.2pp**，7.2B 基模 + NoRA SFT adapter）。而**多轮 agentic RL 训练**（工具使用回合、逐 token logprob、episode 级训练）仍是公开空白——没有公开配方、没有公开 RL 结果、也没有把 state 管理器和 RL 训练器焊起来的 rollout 层。本仓库先把这个生态审计清楚，并让每条结论都可复核。

**2026-11-05 的五个核心发现**：
1. 生态图不全：仅 `rwkv-rs` 组织就有 **40 个公开仓库**（此前审计漏 30 个），包括更早的 **verl 原生 RWKV RL 集成 `verl-rwkv`**（43 个 RWKV 文件/18 PR，2026-08-02 停更）、活跃的 `torchtitan-rwkv`、`Megatrwkv-Bridge`、评测 fork、量化与 Rust 全栈；
2. **"没有 agentic 模型/成绩"已被推翻**：`rwkv-org/rwkv-agent-eval` 于 **2026-11-07** 发布首批公开多轮 agent 评测——1019 题同题配对差 **30.9% → 52.8%（+21.9 ±3.2pp）**，12 个能力块全部上涨，留出题 +22.1pp；被测是 **7.2B 基模 + NoRA SFT adapter**（`mix-20261106`，**不是 RL**）；生态外 `No-22` 另有 568 题多轮考卷（G1l 基模 32.9% → NoRA 56.4%，非同基模严格对照）；`browsecomp-plus-eval` 是 830 题 BrowseComp-Plus 完整评测包（无公开分数）；
3. **官方口径比"不做 agentic"更细**：G1l（2026-10-31）已官方支持多轮 tool-call 模板，官方文档指向社区 agent 目录——准确说法是"官方不做 agentic RL 训练，但把接口官方化、实践交给社区"；
4. **仍空白的是**：公开的多轮 **agentic RL** 训练配方与结果（现有 agent 成绩全部是 SFT/NoRA/MiSS 适配器）、标准 benchmark（τ-bench / BFCL / BrowseComp-Plus）上的 RWKV 公开分数、把 state 管理器与 RL 训练器焊起来的 rollout 层；
5. **纠正了 12 处事实**（vLLM pin、wkvm live-migrate 未实现、Megatron 28B 只有短跑证据、Helicopter 公开不存在但契约已进公开分支等），详见 [`reports/2026-11-05-verification.md`](reports/2026-11-05-verification.md)。

**2026-11-07 更新**：首批公开 agent 评测结果已发布（SFT，非 RL），见 [`reports/2026-11-06-ecosystem-update.md`](reports/2026-11-06-ecosystem-update.md) §11。

**怎么用**：`bash tracking/check.sh` 约 90 秒打一份生态快照（不消耗 GitHub API 配额），`--diff` 看变化；报告里每条结论都带命令、时间戳与证据路径。**证据政策**：不重新分发第三方全文，删除的副本以 `ARCHIVED.tsv` 中的 sha256 记录，可随时重新抓取校验。规划（P0–P5）见 [`ROADMAP.md`](ROADMAP.md)。

**许可**：本仓库自有内容 Apache-2.0；第三方引用均署名，不全文转载。

---

*Founding snapshot: 2026-11-05 · maintained by [@Fantasia-Infinity](https://github.com/Fantasia-Infinity)*
