# 状态层（wkvm）与规模化（RWKV-Megatron）、Helicopter 踪迹 —— 核验报告

| 项目 | 内容 |
|---|---|
| 核验员 | `state-megatron`（Team Lead 派出的核验员，任务 `task-2`） |
| 核验时间 | 2026-11-05 21:07–21:22 CET（20:07–20:22 UTC），主证据时间戳见每条 |
| 主机 / 路径 | `Snellius login node`，工作区根 `~/AlchemyRepos/RWKV-AgenticLearning/` |
| 写入范围 | 仅 `reports/state/`、`repos/wkvm/`、`repos/RWKV-Megatron/` |
| 方法 | `git ls-remote` / `git clone --depth 1` + shallow branch fetch / `raw.githubusercontent.com` / `github.com/<repo>/commits/<branch>.atom` / GitHub HTML / Codeberg API / HuggingFace API / `web_search` / `web_fetch`；**未安装依赖、未跑 GPU/SLURM、未执行训练或测试** |
| GitHub API 配额使用 | **1 次**（`GET api.github.com/repos/rwkv-rs/Helicopter` → HTTP 404），远低于 4 次上限；其余全部无配额路径 |
| 原始证据 | `reports/state/evidence/`（索引见 `INDEX.md`；汇总裁剪见 `KEY-FACTS_*.txt`） |

> 本报告的判定口径：✅ = 交接说法成立且证据充分；⚠️ = 交接说法方向对但需修正/限定，或证据只支持部分结论；❌ = 交接说法错误或证据相反。


> **公开版说明（2026-11-05）**：为符合公开发布政策，第三方全文/HTML/ATOM 已从本仓库移除（原始文件 sha256 见 `evidence/ARCHIVED.tsv` 与 `evidence/CITATIONS.md`，可按其中的 URL 重新抓取）。保留的命令输出与结构化数据可直接查看；正文引用中已移除的文件名仍保留，用于追溯当时证据。

---

## 1. 结论摘要表

### 任务 1 —— `xiaol/wkvm`（LICENSE / 性能证据 / Chat API / 活动含义）

| # | 核验项 | 交接原说法 | 核验结论 | 状态 |
|---|---|---|---|---|
| 1.1 | 根目录 LICENSE 是否存在 | 不存在 | **确认不存在**：raw `LICENSE/LICENSE.md/LICENSE.txt/COPYING` 全 404；clone 内 0 个 license 类文件；`git ls-files` 无；paper 的 arXiv 元数据自己写着"仓库声明 Apache-2.0 但顶层 LICENSE 文件 pending，需先解决矛盾" | ✅ |
| 1.2 | `pyproject.toml` 许可声明 | Apache-2.0 | 确认：`pyproject.toml:11 license = { text = "Apache-2.0" }`（另有 `[project.scripts]` 等，无 SPDX 头） | ✅ |
| 1.3 | README "LICENSE file pending" | 有 | 确认：`README.md:272-274` "Apache-2.0 (LICENSE file pending)." | ✅ |
| 1.4 | RWKV-7 durable-state 引擎是否有性能数据/benchmark 产物 | §10.1#2：README 只给了 Gemma 路径的完整数字 | **交接说法错误**：README `Status` 段（L244-253）直接给出 RWKV-7 数字；且仓库有专门的 RWKV 基准产物 `experiments/results/m2_engine_bench.md`（1.5B 8,077 tok/s @B256；191M 38,856 tok/s @B256）、`m3_results.md`（2,000 会话/2.29 MiB/p50 8.2ms/64-way fork/16-16 续接）、`m3_run.log`、`bench_albatross_2.9b.log`；`paper/CLAIMS.md` C2/C3 为逐条 claim-SHA256-commit 台账。缺的不是"RWKV 数字"，而是**多次重复/独立复现**（作者自己列入 excluded/strict caveat） | ⚠️（交接需改） |
| 1.5 | 现有 chat API 是否支持 tools / logprobs / 自定义 stop | 不支持（三项） | **代码逐项确认全部硬拒绝**：`wkvm/gemma_server.py:2057-2072`（tools/tool_choice/logprobs/stop）、`:1818-1823`（logprobs/stop）、`:1879/:2176/:2200`（response 中 `"logprobs": None`）；README L52-55。另有引擎级**全局** `stop_token_ids`（`wkvm/engine.py:58,92-95`，per-request 只允许空集或与全局一致），不是"自定义 stop" | ✅ |
| 1.6 | 最后提交 2026-08-02 之后无活动的含义 | 未展开 | **需修正**：main 最后提交 `93e7a87` = 2026-08-02T03:15:22Z *"Publish rendered WKVM technical report"*（同日两条均为论文发布）；但 `m4-qwen35-hybrid` 分支活跃到 **2026-09-10T03:18:07Z**，相对 main 61 文件 +12,086/−116 行（Qwen3.5 hybrid guest allocator、hybrid runner/state、RULER-lite 网格、vLLM 对比等）。含义 = **主线在论文发布后冻结、开发转入 M4 分支，2026-09-10 后停止（距今 56 天）**，不是"项目弃更" | ⚠️（交接需补） |
| 1.7 | create / snapshot / fork / hibernate / resume | 支持 | 确认（M3，2026-07-06 完成）：`wkvm/store.py`（`name@version`、fork、mutation）、`wkvm/engine.py`（snapshot/hibernate/resume/submit_from_handle）、`wkvm/server.py:8-16` `/v1/states`（create/get/fork/mutate/persist/delete）+ `/v1/generate`；`m3_results.md` 有 2,000 会话、64-way fork（544.8ms，8.5ms/fork）、进程重启后重建等实测 | ✅ |
| 1.8 | **live-migrate** | 支持 | **未实现**：`wkvm/server.py` 无任何 migrate 端点；`ROADMAP.md:52` 把 P/D disaggregation / "one RDMA write per session" 列入 *Deferred / refused*；`paper/CLAIMS.md` excluded 列表明确排除 "live migration"；`docs/ANGLE.md:142` 仍把它列为未来 demo (c)。README 的 "live-migrate" 是愿景措辞 | ❌（交接过度） |
| 1.9 | "2000 hibernated 会话 @2.29MiB，p50 8.2ms / p99 9.5ms；64-way fork；1.5B 8.1k tok/s @B256" | 实测 | **数字本身成立，但限定条件被交接省略**：p50 8.2 / p99 9.5 仅为 **WARM（pinned-host→slot）层**，COLD（NVMe）为 p50 8.6 / p99 17.6；作者 claim 台账明写 *"Exclude reported p99"*（单次运行、磁盘层未清 OS page cache）；8.1k 实为 **8,077 tok/s（单次 64-step 计时、无重复/无 CI/无同规模 incumbent 对照）**；fork 64 子 544.8ms | ⚠️（需加限定） |
| 1.10 | 10x 撤回 / A800 PROVISIONAL / vLLM 更快一行 | 有 | 确认：`README.md:112-158` 有 "no honest workload-independent 10x claim"、9.827x 修正行、A800 12.107x 标 PROVISIONAL、0.586x 行。**补充**：0.586x 行是标 OUTDATED 的历史 Open WebUI 行；真正代表"当前 vLLM 更快"的是 L139 的 **0.790x（Repeated A800 strict short-session gate，overall gate fail）**，交接未提 | ✅（可补强） |

### 任务 2 —— `TimeMobius/RWKV-Megatron`（28B 分支 / 默认分支 / 规模化路径）

| # | 核验项 | 交接原说法 | 核验结论 | 状态 |
|---|---|---|---|---|
| 2.1 | 28B 分支名 | `codex/rwkv28b-distill`（已知有误） | 确认真名为 **`codex/qwen-rwkv28b-distill`**（`git ls-remote --heads` + 默认 HEAD 对照） | ✅（已纠正） |
| 2.2 | 该分支是否有 28B **真实训练**证据 | §10.1#3 待验证："若成熟，规模化路径从存在变被证明" | **有真实 28B 训练证据，但只到"短跑/容量验证"级别**：① 分支内 3 个 28B 蒸馏配置（88 层/hidden 5120/80 heads/FFN 17408，`rwkv7_28b_88_mapped.pt`，教师 Qwen3.8-27B）+ `tests/run_28b_distill_capacity.py`；② 配置注释记录实测："30 full-context local-target steps passed. Peak 75063 MiB; mean 2.513 s/step"；③ 同组织的 `codex/rwkv7-cp` 分支有 **4 种 28B 布局 × 30 步 + 固定验证**的机器可读结果（TP4/PP2/CP1: 75829MiB、2.0712s、final val CE 7.497223）；④ 但 `run_28b_distill_capacity.py` 自述 *"does not save ... checkpoints or certify model quality"*；distill 分支的 `docs/`、`training-smoke/` 被 `.gitignore` 整体忽略（0 个文件入库），28B 短测不上 W&B。**结论：真实 28B 前向/反向/优化器步 + 显存/步速被证明；28B 收敛/质量/长跑无证据**（组织内唯一 12 小时长跑是 **2.7B**，非 28B） | ⚠️ |
| 2.3 | 分支最后提交 2026-10-30 | 有 | 确认：HEAD `2fab35c` = 2026-10-30T01:30:24Z（"Revert 'feat(distill): stop JSONL training at the finite epoch boundary'"）；atom 首页 20 条提交覆盖 2026-10-27→10-30（10-23 起活跃；总提交数未逐条核，atom 每页 20 条） | ✅ |
| 2.4 | 默认分支已变 `muon`、2026-07-06 停 | 是 | 确认：`ls-remote --symref HEAD` → `refs/heads/muon`；HEAD `34e447c` = 2026-07-06T09:09:04Z | ✅ |
| 2.5 | `2026-10-10` / `codex/rwkv7-cp` 分支状态 | 2026-10-10 2026-10-15；cp 未提 | 确认并补全：`2026-10-10` = 2026-10-15T06:52:36Z（FP8/精度/3B 参考配置/SP 分片等 15 条提交，2026-10-10→10-15）；**`codex/rwkv7-cp` = 2026-10-22T08:18:50Z**，含 CP+SP/recurrent 训练与 **28B 显存/CP2/offload/严格续训**证据目录（`training-smoke/` 共 1,041 个入库文件、5 个 28B 配置）。因此 §2 "实际活在 2026-10-10 分支" 在交接时已过期 | ⚠️（需更新） |
| 2.6 | 规模化路径结论：存在 / 被证明 / 仍无证据 | 存在（推测可升级） | **判定：存在 ✅ + 工程可行性"部分被证明" ⚠️；训练有效性仍无证据 ❌**。即：8×H800 上 28B 能跑（4 布局 ×30 步、固定验证、无 NaN/skip/OOM）、显存/步速可测、CP2/offload/严格续训有修复；但没有任何 28B 收敛曲线、质量评测或长跑，且 TP 数值分叉（step26 grad-norm 相对差 28.42%）按用户决定**暂不修复** | ⚠️ |
| 2.7 | §2 "14B 配置、TP2×PP2 实测 26,892 tok/s、77 测试通过" | 有 | 14B 配置确认存在（`configs/config-mobius-r7-pretrain-14b-megatron.yaml`，muon 默认分支）；但 **"26,892 tok/s" 与 "77 测试通过" 在公开树（muon 分支 280 行 README、README_EN、全部 tracked 文件）中检索不到**，疑在未入库的本地报告里 → 至少"不可从公开仓库复核" | ⚠️（未决） |

### 任务 3 —— Helicopter 踪迹

| # | 核验项 | 交接原说法 | 核验结论 | 状态 |
|---|---|---|---|---|
| 3.1 | `rwkv-rs/Helicopter` 是否存在 | 404（已复验仍 404） | **确认不存在**（多路复验）：repo 页面 404、`.atom` 404、raw README 404、未认证 API 404；`rwkv-rs` 组织页首页可见的 30 个公开仓库中无 helicopter/heli/scoreboard；Codeberg 搜索无该仓库；HuggingFace models/datasets/spaces 搜索直升机类结果全是无关的 RL/旋翼物理项目，无 RWKV scoreboard | ✅ |
| 3.2 | `rwkv-skills` README 引用 Helicopter | 有 | 确认：`rwkv-rs/rwkv-skills` main README **第 8 行**："The public scoreboard is maintained separately in the Helicopter repository."（无链接）。该句在 **2026-08-09T04:14:31Z** 的合并提交 `6c9282b`（"Consolidate local evaluation runtime on main"）中出现；2026-07-20 的旧 README 无此句、只有 `SCOREBOARD_API_BASE_URL` | ✅ |
| 3.3 | Helicopter 是否以其他名字/平台存在 | — | **❌ 不存在**（GitHub 组织/Codeberg/HF 三路均无；访问 GitHub 会触发凭据提示，也可能为私有仓库，但公开侧零踪迹） | ❌ |
| 3.4 | "scoreboard 以别处形式存在" | — | **⚠️ 部分成立**：scoreboard **机制/代码**确实存在于 `rwkv-skills` 仓库内——`vllm-rwkv` 分支有 `client/`（Next.js 前端）+ `src/dashboard`（FastAPI，`:7860`）+ `SCOREBOARD_API_BASE_URL`；main 分支有 `ops/`、`docs/function_calling_open_leaderboard.zh-CN.md`、`.env.example` 的 "Evaluation dashboard (FastAPI API + Next.js frontend)" 与 `RWKV_SPACE_SCORE_INDEX`。但**没有找到任何公开的 RWKV 评测成绩数据/在线榜单**（仍只有 handoff §5.1 的 toolcaller-bench 成绩是公开可复现的）。`rwkv-rs/browsecomp-plus-eval` 是另一个独立评测包（README 无 Helicopter/scoreboard 字样），不是 scoreboard 别名 | ⚠️ |
| 3.5 | `skyrl-rwkv` 的 `feat/heli-r00-training-eval` 分支 | — | 确认存在（`785a231`），2026-10-24→10-28 约 20 条提交，标题集中在 bounded training/evaluation、SFT/SST、SAO、probe scoring 等；**未出现 Helicopter 仓库/URL 引用**（分支 diff 由 skyrl-deep 负责，本报告不重复） | ✅（记录） |

### 任务 4 —— §7 许可证事实（低成本复核）

| # | 核验项 | 交接原说法 | 核验结论 | 状态 |
|---|---|---|---|---|
| 4.1 | `rwkv_lightning` 无许可证 | 无 | 确认：仓库 `RWKV-Vibe/rwkv_lightning`，main 分支文件树无 LICENSE，raw LICENSE/main 404，main 无 `pyproject.toml`（404），13,832 字节 README 无 license 字样 | ✅ |
| 4.2 | `FlashRWKV2` 为 MIT | MIT | 确认：`rwkv-rs/FlashRWKV2` raw `LICENSE` HTTP 200，1,110 字节，首行 "MIT License Copyright (c) 2026 MoonshotAI / FlashRWKV2 contributors" | ✅ |
| 4.3 | `toolcaller-bench` Apache-2.0（Codeberg raw LICENSE） | Apache-2.0 | 确认：`codeberg.org/scarletwolf_ai/rwkv-toolcaller-bench/raw/branch/main/LICENSE` HTTP 200，**11,358 字节**（与交接一致），Apache License 2.0 头 | ✅ |
| 4.4 | `json2binidx_tool` 无许可证 | 无 | 确认：`Abel2076/json2binidx_tool` main 文件树（data/tools/20B_tokenizer.json/README.md/requirements.txt/rwkv_vocab…/sample.jsonl）无 LICENSE；raw LICENSE（main、master）均 404；README 无 license 字样 | ✅ |
| 4.5 | （附）`rwkv-skills` 无许可证 | §5 称无 | 确认：main 文件树无 LICENSE，raw LICENSE 404，`pyproject.toml` 无 license 字段 | ✅ |

---

## 2. 逐条证据

> 每条都给出：证据文件（`reports/state/evidence/…`，含命令原始输出与 UTC 时间戳）、仓库文件 `路径:行号`、或 URL + 抓取时间。汇总裁剪版：`KEY-FACTS_20261105T201626Z.txt`。

### 2.1 wkvm —— LICENSE（双证）

命令与原始输出（`evidence/02_atom_wkvm_20261105T200845Z.txt`，2026-11-05T20:08:45Z UTC）：

```
404  https://raw.githubusercontent.com/xiaol/wkvm/main/LICENSE
404  https://raw.githubusercontent.com/xiaol/wkvm/main/LICENSE.md
404  https://raw.githubusercontent.com/xiaol/wkvm/main/LICENSE.txt
404  https://raw.githubusercontent.com/xiaol/wkvm/main/COPYING
200  https://raw.githubusercontent.com/xiaol/wkvm/main/pyproject.toml
200  https://raw.githubusercontent.com/xiaol/wkvm/main/README.md
```

Clone 双证（`repos/wkvm`，HEAD `93e7a87`，2026-11-05T20:09:31Z UTC，`evidence/04_wkvm_structure_*.txt`、`evidence/04b_wkvm_tracked_files_CLEAN_*.txt`）：

```
--- any license-ish file tracked ---
(none tracked)
--- pyproject license lines ---
11:license = { text = "Apache-2.0" }
--- README license mentions ---
272:## License
274:Apache-2.0 (LICENSE file pending).
```

作者自己把"许可矛盾"列为发布阻塞（`repos/wkvm/paper/arxiv-metadata.md` "## License" 段；`paper/README.md` "Before submission" 第 2 条）：

> The repository currently declares Apache-2.0 in `pyproject.toml` but also says the top-level `LICENSE` file is pending; resolve that inconsistency before advertising the code as Apache-licensed.

补充：全仓无 `SPDX-License-Identifier` 头（`evidence/12_wkvm_paper_license_scripts_*.txt`）。

### 2.2 wkvm —— RWKV-7 durable-state 引擎的性能/benchmark 产物（对 §10.1#2 的直接反证）

**README 本身给了 RWKV-7 数字**（`README.md:244-253`，clone 2026-11-05T20:10:09Z UTC，`evidence/07_wkvm_README_full_*.txt`）：

```
246	**M3—Durable State API:** ... Measured demos include 2,000 hibernated sessions
247	at 2.29 MiB each, p50 8.2 ms / p99 9.5 ms resume, process-restart recovery,
248	64-way fork, and provenance-recorded mutation.
251	**M2—native RWKV-7 serving:** ... A 1.5B model measured 8.1k tok/s at B256 on an RTX 4090.
```

**专门的 RWKV 基准产物**（非 Gemma）：`experiments/results/m2_engine_bench.md`（2026-07-03，RTX 4090，`evidence/08_wkvm_rwkv_bench_artifacts_*.txt`）：

```
m2_engine_bench.md:9   ## RWKV-7 World 1.5B (24 layers, d=2048) — 12.19 MiB state/slot
m2_engine_bench.md:18  | 256 | 7,913 | 8,077 | 3,132 | 19.02 |
m2_engine_bench.md:20  ## RWKV-7 World 191M (12 layers, d=768) — 2.29 MiB state/slot
m2_engine_bench.md:29  | 256 | 26,707 | 38,856 | 587 | 2.94 |
```

`experiments/results/m3_results.md`（2026-07-06，RWKV-7 191M，`evidence/08…`）：

```
m3_results.md:7   2000 sessions ... in 31.7s; WARM tier 4.46 GiB (2.29 MiB/session); 500 evicted to COLD
m3_results.md:11  WARM (pinned host → slot) | 224 | 8.2 ms | 9.5 ms | 35.7 ms
m3_results.md:12  COLD (NVMe safetensors → slot) | 76 | 8.6 ms | 17.6 ms | 18.4 ms
m3_results.md:14  Exactness: 16/16 interrupted+resumed continuations token-identical ...
m3_results.md:19  Fork: 64 children in 544.8 ms (8.5 ms/fork ...)
```

**作者自己的 claim 台账把限制写死**（`paper/CLAIMS.md`，`evidence/08…` + `12…`）：

- C2：8,077 tok/s 的证据是 `m2_engine_bench.md` + SHA-256 + commit `cb421af…`；required caveat = *"Single 64-step timing; no repeats, confidence interval, model hash, or matched incumbent."*
- C3：2,000 snapshot / 2.29 MiB / 8.2/8.6ms / 16-16 的 caveat = *"Single run. Disk-backed reload did not flush OS page cache. **Exclude reported p99.** Fingerprint is layout/dtype only."*
- Excluded 列表："Any workload-independent or engine-wide '10x faster' statement"、"...live migration, ..."、"Trainer/server parity..."（M3 报告 0/8 within 5e-3）。

**训练器/服务端 logprob 一致性**（对 agentic RL 关键，`m3_results.md:22-32`）：`max |Δlogprob|=1.38e-1, mean=1.99e-2, rollouts within 5e-3: 0/8`；作者给出的替代是"用与训练器相同的 chunked 路径做 rescoring"。

### 2.3 wkvm —— Chat API 能力（代码核实）

`evidence/09_wkvm_api_capabilities_*.txt`（2026-11-05T20:10:31Z UTC，clone `93e7a87`）：

```
wkvm/gemma_server.py:2057-2062  tools / tool_choice / stop 全部 raise ValueError("...not supported")
wkvm/gemma_server.py:2071-2072  logprobs raise ValueError("logprobs are not supported")
wkvm/gemma_server.py:1818-1823  logprobs / per-request stop sequences 拒绝
wkvm/gemma_server.py:1879,2176,2200  "logprobs": None
wkvm/engine.py:92-95   per-request stop_token_ids 必须为空或等于引擎全局集合
```

README `Current chat contract`（L52-55）与 `This UI path exercises approximate Gemma routed-span mode. WKVM's native RWKV-7 durable-state engine and API are separate paths.`（L68-69）与代码一致。**"RWKV-7 durable-state 引擎与 API 是独立路径"成立**：`wkvm/server.py:1-18` 是 token-id 的 `/v1/states` + `/v1/generate`（`evidence/11…`），与 OpenAI chat 前端分属两个 server。

### 2.4 wkvm —— "2026-08-02 后无活动"的真实含义

`git ls-remote --heads` + atom（`evidence/01…`、`02…`；2026-11-05T20:08:37/45Z UTC）：

```
refs/heads/main                    93e7a87…  (atom updated 2026-08-02T03:15:22Z)
refs/heads/demo/open-webui-video   5a5fda5…  (atom updated 2026-07-17T05:29:03Z)
refs/heads/m4-qwen35-hybrid        241affd…  (atom updated 2026-09-10T03:18:07Z)
```

main 最近提交（`evidence/11…`）：`2026-08-02T03:15:22Z Publish rendered WKVM technical report`、`03:11:04Z Add arXiv-ready WKVM technical report`（同日论文收尾）；此前 07-21/22/23 为 Open WebUI/10x 基准收尾。

m4 分支实测（`evidence/10_wkvm_branches_*.txt`，shallow fetch 2026-11-05T20:10:38Z UTC）：

```
== origin/m4-qwen35-hybrid ==
241affd2… 2026-09-10T11:18:07+08:00 Docs: R=144 RULER-lite grid for the routed bank
61 files changed, 12086 insertions(+), 116 deletions(-)   # vs main
# 新增 wkvm/models/qwen35.py、runner/hybrid_{graph,routed,runner,state}.py、experiments/{routed_probe,ruler_lite}.py、
#      scripts/convert_rwkv7_pth.py、results/qwen35_*_20260910.md、4 个 RULER-lite/benchmark JSON 等
Co-Authored-By: Claude Fable 5.1 <email redacted>
```

含义：**主线在论文发布后冻结（95 天未动），但 2026-08-02→09-10 的真实开发在 M4 分支（Qwen3.5 混合模型，含真实 A100 对 vLLM 0.29 的对比报告），2026-09-10 后整体停止（56 天）**。另外 M4 分支也未加 LICENSE（`git ls-tree origin/m4-qwen35-hybrid` 无 LICENSE，`evidence/10…`）。

### 2.5 wkvm —— live-migrate 与 10x 口径

- 未实现证据：`wkvm/server.py:8-16` 路由清单无 migrate；`ROADMAP.md:52` "Deferred / refused: ... P/D disaggregation (one transport, one RDMA write per session)"；`paper/CLAIMS.md` excluded "live migration"（`evidence/11…`、`06…`）。
- 10x 撤回口径（`README.md:112-158`）逐行核对：`L114-117` 明说没有 workload-independent 10x；`L136` 9.827x（later mode-3 audit）；`L137` A800 12.107x **PROVISIONAL**（dirty worktree、无 SGLang T12）；`L138` 0.586x 一行标 **OUTDATED**；`L139` **0.790x** "Repeated A800 strict short-session gate ... overall gate fail"（交接未提）；`L145` 不再从该 artifact 做 10x-vLLM 结论。

### 2.6 RWKV-Megatron —— 分支全景（ls-remote + atom + shallow clone）

`evidence/01…`（2026-11-05T20:08:37Z UTC）+ `evidence/23_megatron_atom_feeds_*.txt`（20:11:29Z UTC）+ `evidence/27…`（20:12:16Z UTC）：

| 分支 | 远端 SHA | 最后提交（UTC） | 内容（提交标题归纳） |
|---|---|---|---|
| `muon`（默认，`--symref HEAD`→refs/heads/muon） | `34e447c` | 2026-07-06T09:09:04Z | 历史预训练主线；14B 配置在此分支（`config-mobius-r7-pretrain-14b-megatron.yaml`） |
| `2026-10-10` | `69aa22a` | 2026-10-15T06:52:36Z | FP8、BF16/FP32 精度诊断、3B 参考配置、SP v0 分片、固定 eval 等 16 条 |
| `codex/rwkv7-cp` | `240d9a4` | 2026-10-22T08:18:50Z | CP+SP/recurrent CP 训练、28B 显存/CP2/offload、严格续训；test 证据 1,041 文件入库 |
| `codex/qwen-rwkv28b-distill` | `2fab35c` | 2026-10-30T01:30:24Z | Qwen→RWKV 蒸馏（3 个 28B 配置 + 2.7B 六布局冒烟 + capacity probe）；atom 首页 20 条提交覆盖 10-27→10-30 |

`git ls-remote --symref https://github.com/TimeMobius/RWKV-Megatron HEAD` → `ref: refs/heads/muon`（2026-11-05T20:12:16Z UTC，`evidence/27…`）→ **默认分支确已从旧主线变为 muon**。

### 2.7 RWKV-Megatron —— 28B 证据链（本任务核心）

**(a) 蒸馏分支（`codex/qwen-rwkv28b-distill`，HEAD `2fab35c`，2026-10-30T01:30:24Z）**

- HEAD 提交全文（`evidence/20…`，20:11:12Z UTC）：`Revert "feat(distill): stop JSONL training at the finite epoch boundary"`（前一条同主题提交 01:17:50Z）。
- 28B 配置 3 个（`git ls-tree`，`evidence/22…`；内容 `evidence/25…`）：
  - `configs/config-qwen-28b-distill-tp2-sp-pp2-cp2-offload50-smoke.yaml`
  - `configs/config-qwen-28b-distill-tp2-sp-pp4-balanced-smoke.yaml`
  - `configs/config-qwen-28b-distill-tp4-sp-pp2-smoke.yaml`
- 配置内实测记录（`config…tp2-sp-pp4-balanced-smoke.yaml:1-3`）：
  > `# 8xH800: TP2 x PP4 + SP, layer split [18,26,26,18], no CPU offload.`
  > `# Requires global-layer checkpoint loader fix. 30 full-context local-target steps passed.`
  > `# Peak 75063 MiB; mean 2.513 s/step. Online Qwen and checkpoint resume remain separate checks.`
  另一配置（`config…tp2-sp-pp2-cp2-offload50-smoke.yaml:1-2`）：`# Real 28B, 8xH800, seq4096, micro1/global2. Capacity tested with local top100 targets. # Online Qwen availability and checkpoint resume need separate validation.`
- 模型几何/初始化（`config…tp2-sp-pp4-balanced-smoke.yaml:29-57,116,144`）：`num_layers: 88`、`hidden_size: 5120`、`num_attention_heads: 80`、`ffn_hidden_size: 17408`、`load_pretrained_rwkv: …/rwkv7_28b_88_mapped.pt`、教师 `Qwen3.8-27B`、`train_iters: 30`、`wandb_project: rwkv-qwen-distill-28b`。
- **证据边界**（`tests/run_28b_distill_capacity.py:1-6`，`evidence/26…`）：
  > `Compare 28B/4096-token distillation layouts on eight GPUs with local targets. ... Synthetic top100 targets isolate capacity from the availability of the online teacher. This probe does not save hundreds of GB of checkpoints or certify model quality.`
- **证据不可得**（`evidence/26…`、`40…`）：该分支 `.gitignore` 末尾 `/training-smoke/`、`/docs/`、`/todolist.txt` → `git ls-tree` 中 `docs/`+`training-smoke/` 文件数 = **0**；README（463 行）除分支名 `codex/qwen-rwkv28b-distill`（L55）外**无任何 28B 训练/结果内容**（只有 Qwen→RWKV 蒸馏的通用说明与 2.7B 六布局冒烟）。即 README/Branch 文档引用的 `docs/distillation-*.md` 验收记录均未公开。
- 提交信息（atom，`evidence/23…`）：`2026-10-28 07:39:42Z feat(distill): add tested 28B training layouts and capacity probes`、`2026-10-28 08:05:56Z feat(distill): supervise 28B PP4 stability runs with sparse checkpoints`。

**(b) CP 分支（`codex/rwkv7-cp`，HEAD `240d9a4`，2026-10-22T08:18:50Z）—— 28B 真实短跑有机器可读证据**

`TESTING_STATUS.md:17-37`（`evidence/28_megatron_cp_testing_status_*.txt`，20:12:34Z UTC）原文节选：

```
17  ## 28B实际跑通的配置
19  模型：`/hikscale/models/XiaoKe/rwkv7_28b_88_mapped.pt`（88层，hidden5120，80heads，FFN17408，日志约27.46B）。
22  下表均为SP开启、BF16计算、FP32梯度及Adam m/v、full recompute、MB1/GB2、30步训练＋固定验证。
24  | 布局 | seq | 优化器存储 | 整卡峰值 | 步耗时 | 最终验证CE |
26  | TP4/PP2/CP1 | 4096 | 全GPU，完整FP32主权重 | 75829MiB / 74.05GiB | 2.0712s | 7.497223 |
27  | TP2/PP4/CP1 | 4096 | 全GPU，完整FP32主权重 | 79969MiB / 78.09GiB | 2.40035s | 7.499003 |
28  | TP2/PP2/CP2 | 4096 | 50% Adam CPU offload，完整FP32主权重 | 79595MiB / 77.73GiB | 4.5298s | 7.502898 |
29  | TP2/PP2/CP2 | 2048 | 全GPU，TE int16主权重余数 | 80797MiB / 78.90GiB | 5.6694s | 7.754669 |
33  - TP2/PP2/CP2的完整FP32主权重全GPU方案常驻约81.10GiB/卡，超过本机容量，首次Adam状态初始化OOM。
37  - 这些28B短测没有上传W&B；此前2.7B长跑和质量评测有W&B记录。
```

机器可读结果（`training-smoke/audit/28b-oom-20261022/tp4pp2cp1-no-offload-results.json:1-25`，`evidence/29…`）：`"status": "passed"`, `"train_steps": 30`, `"tp": 4, "pp": 2, "cp": 1`, `"median_step_ms_after_step2": 2071.2`, `"max_cuda_allocated_gib": 67.98`, `"sampled_gpu_peak_mib": 75829`, `"final_validation_loss": 7.497223`, `"finite_and_zero_nan_skips": true`。同目录 `RESULTS.md`、`gpu-summary.json`、逐 rank JSONL、失败日志、Megatron 修复补丁均在库（`evidence/28/29…`）。

**(c) 组织内唯一 12 小时长跑是 2.7B，不是 28B**（`TESTING_STATUS.md:59`，同一证据文件）：

```
| CP4半天长跑 | ...：**2.7B，非28B**，TP2/PP1/CP4+SP、16K，12小时49189步、约16.118亿token，无日志NaN/跳步；
  固定验证loss13.49113→4.067253；不是CP1收敛等价试验 |
```

**(d) 风险/限制**：28B TP 数值分叉（`TESTING_STATUS.md:39-48`，`evidence/28…`）：两条 30 步轨迹第 26 步 grad-norm 21.372573 vs 27.448297，**相对差约 28.42%**；定位到第 0 层 Attention 行并行 `linear_proj` 的 BF16/TP 部分和差异；"用户决定暂不做精度修复"（当前没有把生产 TP 通信/部分结果切到 FP32）。此外 `COMMIT_AND_PUSH.md:28`："本轮没有重跑28B完整训练"。

### 2.8 Helicopter —— 全生态踪迹

- 多路 404（`evidence/30_helicopter_probes_*.txt`，20:13:03Z UTC）：`https://github.com/rwkv-rs/Helicopter`(404)、`/helicopter`(404)、`/heli`(404)、`/scoreboard`(404)、raw main README(404)、`.atom`(404)；未认证 API `GET /repos/rwkv-rs/Helicopter` → **HTTP 404**（本任务唯一一次 API 调用）。
- `rwkv-rs` 组织公开仓库（HTML 首页抽取到 **30** 个，`evidence/30…`）：antidoom-rwkv, any2rwkv, browsecomp-plus-eval, chinese-babylm-eval-pipeline, codex-compact-router, evalscope-rwkv, fla-rwkv, FlashRWKV2, hf-adapter, lighteval-rwkv, llm-compressor-rwkv, lm-evaluation-harness-rwkv, Megatrwkv-Bridge, rwkv7-ascend-npu, RWKV-AUTODECO, RWKV-LH, rwkv-rs, rwkv-rs-stable, rwkv-rs-test, RWKV-Scout, rwkv-skills, skyrl-rwkv, tokenizers-rwkv, torchtitan-rwkv, torchtitan-rwkv-old, transformers-rwkv, verl-rwkv, vllm-rwkv, wandb-rs, wx-cli … **无 Helicopter/scoreboard**。
- `rwkv-skills` 的引用（`evidence/03…`、`31…`、`33…`、`35…`）：
  - main README `:8`："Third-party benchmark data and evaluation artifacts stay out of the source package. The public scoreboard is maintained separately in the **Helicopter** repository."（无超链接）。
  - 该句引入时间：main 提交 `6c9282b`（2026-08-09T04:14:31Z，"Consolidate local evaluation runtime on main"）；2026-07-20 的旧 README（`54639619`）**无 Helicopter 字样**，只有 Scoreboard API 变量（`SCOREBOARD_API_BASE_URL`、`NEXT_PUBLIC_BASE_PATH=/new-eval`）。
- scoreboard 机制存在（`evidence/32…`、`35…`）：`rwkv-skills` 的 `vllm-rwkv` 分支 README `:8-19`：`client/`（Next.js + React dashboard，`/api/*` 代理到 FastAPI）、`src/dashboard/{web,core}`；`:58-70`：`SCOREBOARD_API_BASE_URL`、`NEXT_PUBLIC_BASE_PATH=/new-eval`、admin panel 驱动 eval scheduler。main 分支有 `ops/`、`docs/function_calling_open_leaderboard.zh-CN.md`、`.env.example:44-49`（"Evaluation dashboard (FastAPI API + Next.js frontend)"、`RWKV_SPACE_SCORE_INDEX`）。
- 其他平台（`evidence/34…`、`39…`）：Codeberg `repos/search?q=helicopter` 仅 3 个无关项目；`q=rwkv` 无 scoreboard/helicopter；HuggingFace models/datasets/spaces 搜 `helicopter` 均为无关的 RL/旋翼物理项目，无 RWKV 成绩榜。
- 相关但不同名：`rwkv-rs/browsecomp-plus-eval` 存在（HTTP 200），是 BrowseComp-Plus 的独立评测包（README 无 Helicopter/scoreboard 字样）；`skyrl-rwkv` 的 `feat/heli-r00-training-eval`（`785a231`）2026-10-24→10-28 约 20 条"bounded training/evaluation"提交，**无 Helicopter 引用**（该分支 diff 属 skyrl-deep，本报告不重复）。

### 2.9 §7 许可证复核（命令 + 状态码 + 字节数）

`evidence/36_license_spotchecks_*.txt`（20:14:35Z UTC）、`37…`（20:14:51Z）、`38…`（20:15:02Z）：

| 仓库 | 检查方式 | 原始结果 | 判定 |
|---|---|---|---|
| `RWKV-Vibe/rwkv_lightning` | main 文件树 + raw LICENSE + pyproject + README | 树内仅 `API_servers/ infer/ model_load/ state_manager/ test/ .gitignore README.md README.md.bak app.py app_big_batch.py benchmark.py test_gemm.py webui_rwkv.py`；raw `LICENSE/main`=404；`pyproject.toml/main`=404；README 13,832B 无 license 字样 | 无许可证 ✅ |
| `rwkv-rs/FlashRWKV2` | raw LICENSE | HTTP **200**，**1,110 字节**，`MIT License Copyright (c) 2026 MoonshotAI Copyright (c) 2026 FlashRWKV2 contributors` | MIT ✅ |
| `scarletwolf_ai/rwkv-toolcaller-bench`（Codeberg） | raw `/raw/branch/main/LICENSE` | HTTP **200**，**11,358 字节**，`Apache License Version 2.0, January 2004` | Apache-2.0 ✅ |
| `Abel2076/json2binidx_tool` | main 文件树 + raw LICENSE(main/master) + README | 树内 `data/ tools/ 20B_tokenizer.json README.md requirements.txt rwkv_vocab_v20230424.txt sample.jsonl`；LICENSE 两个分支都 404；README 1,071B 无 license 字样 | 无许可证 ✅ |
| `rwkv-rs/rwkv-skills` | main 文件树 + raw LICENSE + pyproject | 树内无 LICENSE；raw LICENSE 404；pyproject 无 license 字段 | 无许可证 ✅（§5 一致） |

---

## 3. 对交接文档的修订建议

### 3.1 §4.1 `xiaol/wkvm`

| 交接原文（要点） | 建议改为 |
|---|---|
| "支持 state 的 create / snapshot / fork / hibernate / resume / **live-migrate**" | 改为："支持 create / snapshot / fork / hibernate / resume / persist / mutate（M3，`/v1/states` + `/v1/generate`）；**live-migrate 未实现**，属 ROADMAP 的 deferred/refused（P/D disaggregation），README 的 'live-migrate' 仅愿景措辞（`ROADMAP.md:52`，`paper/CLAIMS.md` excluded 列表）" |
| "实测：2000 个 hibernated 会话 @2.29 MiB，p50 8.2ms / p99 9.5ms 恢复；64-way fork" | 加限定："WARM 层（pinned-host→slot）p50 8.2ms / p99 9.5ms；COLD 层（NVMe）p50 8.6ms / **p99 17.6ms**。作者 `paper/CLAIMS.md` C3 明确 **'Exclude reported p99'**（单次运行、磁盘层未清 OS page cache），引用时宜只引 p50 或同时标注该 caveat" |
| "RWKV-7 1.5B 8.1k tok/s @B256" | 改为精确值："**8,077 tok/s**，RTX 4090，B256，单次 64-step 计时（`m2_engine_bench.md:18`；`CLAIMS.md` C2 caveat：无重复/无置信区间/无模型哈希/无同规模 incumbent 对照）；同表 191M 为 38,856 tok/s" |
| "许可问题：pyproject Apache-2.0、README LICENSE pending、根目录无 LICENSE → 法律上仍歧义" | 保留并补一句："作者在 `paper/arxiv-metadata.md`『## License』与 `paper/README.md` 提交前清单里**自己把它列为发布阻塞**（'resolve that inconsistency before advertising the code as Apache-licensed'）；全仓无 SPDX 头" |
| 未提 M4 分支 | 新增一句："`m4-qwen35-hybrid` 分支是 main 之后的真实开发（2026-09-10 止）：Qwen3.5 hybrid guest allocator/routed bank/RULER-lite，相对 main 61 文件 +12k 行，且含真实 A100 对 vLLM 0.29 对比（wkvm 在 13,824 ctx 的 E2E 约为 vLLM 的 0.5×，报告自述为 active box）。该分支同样无 LICENSE。" |
| "诚实度罕见：... 列出 vLLM 更快（0.586x）的一行" | 补一句："更代表当前状态的是 `README.md:139` 的 **0.790x Repeated A800 strict short-session gate（overall gate fail）**；0.586x 行标 OUTDATED，引用它容易误导" |
| 未提 API 限制的具体代码位置 | 建议在 §4.1 末补："三项限制的硬编码位置：`wkvm/gemma_server.py:1818-1823, 2057-2072`；引擎级只有**全局** `stop_token_ids`（`wkvm/engine.py:92-95`）" |

### 3.2 §5 评测层（Helicopter 相关）

| 交接原文 | 建议改为 |
|---|---|
| "README 说成绩在 'Helicopter 仓库'，该仓库**不存在**（`git ls-remote` 验证）" | 保留结论，补两点：① 多路复验（GitHub 页面/atom/raw/未认证 API 全 404；`rwkv-rs` 公开组织 31 仓库无此名；Codeberg/HF 无踪迹）→ 判定"**公开不存在**"（私有仓库无法排除）；② 该句来自 `rwkv-skills` main README L8，是 2026-08-09 合并提交 `6c9282b` 才写进去的，2026-07-20 旧 README 无此句 |
| 未提"scoreboard 以别处形式存在" | 新增："**scoreboard 机制并不完全缺失**：`rwkv-skills` 仓库内含 dashboard/scoreboard 前后端（`vllm-rwkv` 分支 `client/` Next.js + `src/dashboard` FastAPI + `SCOREBOARD_API_BASE_URL`/`NEXT_PUBLIC_BASE_PATH=/new-eval`；main 分支 `ops/` 与 `docs/function_calling_open_leaderboard.zh-CN.md`、`.env.example:44-49` 的 `RWKV_SPACE_SCORE_INDEX`）。缺的是**公开成绩数据/在线榜单**——目前公开的 RWKV agent 成绩仍只有 toolcaller-bench（§5.1）。因此 §5 结论'有框架没成绩'成立，但'Helicopter 不存在 ⇒ scoreboard 不存在'的推论不成立" |
| 未提 heli-r00 分支 | 可加注："`skyrl-rwkv` 有 `feat/heli-r00-training-eval`（`785a231`，2026-10-24→28，~20 提交，bounded training/eval/SFT/SST/SAO 等），无 Helicopter 引用；是否为 Helicopter 代号待 skyrl-deep 的 diff 结论" |

### 3.3 §10.1 未验证项

| 交接编号 | 原文 | 建议改为（结论 + 证据） |
|---|---|---|
| 10.1-2 | "`wkvm` 的 RWKV-7 durable-state 引擎的真实性能（README 只给了 Gemma 路径的完整数字）" | **删除/改写**："**已核实（部分）**：README §Status 与 `experiments/results/m2_engine_bench.md`/`m3_results.md` 都有 RWKV-7 路径完整数字（8,077 tok/s@B256；2,000 会话/2.29MiB/p50 8.2ms/16-16 续接/64-way fork），并已进 `paper/CLAIMS.md` C2/C3 台账。**仍缺**：多次重复与独立复现（作者自己把重复运行/置信区间列为 'Required before a stronger revision'），以及 p99 不应直接引用。" |
| 10.1-3 | "`RWKV-Megatron` 的 `codex/rwkv28b-distill` 分支是否有 28B 的真实训练（若成熟，'规模化路径'从'存在'变'被证明'）" | **改写**："分支名实为 `codex/qwen-rwkv28b-distill`（HEAD `2fab35c`，2026-10-30）。**28B 真实训练证据存在但只到短跑/容量级**：distill 分支 3 个 28B 配置（88L/d5120/80heads，教师 Qwen3.8-27B）+ capacity probe（自述 *does not certify model quality*，`docs/` 与 `training-smoke/` 被 gitignore、0 文件入库）；姊妹分支 `codex/rwkv7-cp` 有 4 种 28B 布局 × 30 步 + 固定验证的机器可读结果（TP4/PP2/CP1 75829MiB、2.0712s、val CE 7.497223、无 NaN/skip）。**结论：规模化路径 = 存在（✅）+ 工程可行性部分被证明（⚠️，仅短跑）；28B 收敛/质量/长跑仍无证据（组织内 12h 长跑是 2.7B，非 28B）**，且 28B TP 数值分叉 28.42% 暂不修复，不宜升格为'被证明'。" |
| 10.1-4 | "`rwkv-rs/Helicopter`（scoreboard 仓库）是否存在（当前 404）" | **改写**："公开不存在（GitHub 页面/atom/raw/API 全 404；`rwkv-rs` 公开组织页首页 30 仓库无此名；Codeberg/HF 无踪迹；不能排除私有）。`rwkv-skills` main README L8 的 Helicopter 引用自 2026-08-09 起存在但无链接。scoreboard **机制**在 rwkv-skills 仓库内有代码，但**无公开成绩数据**。" |
| 10.1-1（顺带） | "`skyrl-rwkv` 在真实 8 卡上能否跑通" | 不在本任务范围，但与 10.1-3 交叉的信息：`skyrl-rwkv` 已有 `feat/heli-r00-training-eval`（2026-10-28 止）与 main（2026-10-31 止）继续开发，说明项目活跃；跑通性仍待 skyrl-deep/GPU 侧核验。 |

### 3.4 §2 训练层（顺带修正，因与 28B 分支强相关）

| 交接原文 | 建议改为 |
|---|---|
| "默认分支停在 2026-07-06，**实际活在 `2026-10-10` 分支**" | 改为："默认分支 `muon` 停在 2026-07-06；此后工作分叉到 `2026-10-10`（→10-15）、`codex/rwkv7-cp`（→10-22，CP/SP/recurrent + 28B 显存与续训）、`codex/qwen-rwkv28b-distill`（→10-30，Qwen→RWKV 蒸馏）。最后活动 2026-10-30（距今 6 天）。" |
| "只做预训练/CPT，无 SFT 入口、无 RL" | 改为："以预训练/CPT 为主，**新增 Qwen→RWKV 在线 logit 蒸馏**（vLLM top-k teacher、KL、JSONL、teacher pool、DP2/4、TP/PP/SP/CP2 等，2.7B 六布局真实在线 3 步冒烟通过）；仍无 SFT/RL 入口（`README.md:18-115` 功能清单）。" |
| "14B 配置、TP2×PP2 实测 26,892 tok/s、77 测试通过" | 建议标注复核状态："14B 配置可在 muon 分支复现（`configs/config-mobius-r7-pretrain-14b-megatron.yaml`）；**26,892 tok/s 与 '77 测试通过' 未能在公开树找到**（muon README 280 行及全部 tracked 文件检索无果），疑在未入库的本地报告 → 引用前需补来源或降级为传闻。" |

---

## 4. 未决事项 / 无法在本环境验证的内容

1. **28B 蒸馏的训练有效性**：无任何 28B 收敛曲线、loss 质量、下游评测或长跑。distill 分支的 `docs/distillation-*.md`（README 引用）与 `training-smoke/` 均为本地、未入库（`.gitignore` 整体忽略）；W&B 只在内网 `dian.sea-group.org:9098`（`README.md:115` 与 `TESTING_STATUS.md:64`），本环境无法访问与核验。**若要升格"规模化被证明"，必须拿到 28B 长跑日志 + 质量评测 + 公开可复现入口。**
2. **28B 在线教师验证**：distill 配置自述 "Capacity tested with **local** top100 targets. Online Qwen availability and checkpoint resume need separate validation."（两个 28B 配置首 2 行）→ 28B 的**在线 Qwen 教师链路**与 28B checkpoint 续训均未验证。
3. **28B TP 数值分叉**：step26 grad-norm 相对差 28.42%，定位到第 0 层 Attention `linear_proj` 的 TP 部分和 BF16 差异，作者按用户决定暂不修复 → 规模化训练稳定性仍有已知风险（`TESTING_STATUS.md:39-48`）。
4. **wkvm p99 与单次运行**：作者 CLAIMS C3 明确 "Exclude reported p99"，M2/M3 全部是单次短跑（64 步/单次 demo），且未有第三方独立复现 → 若在方案/报告里引用性能，建议只用 p50 + 标注单次运行。
5. **wkvm LICENSE**：`LICENSE` 缺失 + 作者把 "resolve that inconsistency" 列为发布阻塞 → **法律上仍不可当作 Apache-2.0 使用**，需作者补 LICENSE 或书面澄清；m4 分支同样无 LICENSE。
6. **Helicopter 是否私有**：公开侧全 404，但无法排除 `rwkv-rs/Helicopter` 为私有仓库；`rwkv-skills` README 的指向没有 URL。若需定论，需要向仓库 owner 求证。
7. **Megatron §2 两个数字**：`26,892 tok/s`、`77 测试通过` 未在公开树找到；本次未运行任何测试（禁止安装依赖/GPU），无法复现"77 测试"。
8. **本核验的边界**：只做 clone + 静态分析 + 无配额网络检索；未执行 `tests/`、未跑 benchmark、未运行 28B/2.7B 训练；wkvm/Megatron 的运行时行为结论均来自其自带报告与代码阅读。

---

## 附录 A：证据文件索引

见 `reports/state/evidence/INDEX.md`。核心文件：
- `KEY-FACTS_20261105T201626Z.txt` —— 全部关键命令的原始输出汇总（含时间戳）
- `01_lsremote_*` / `02_atom_wkvm_*` / `23_megatron_atom_feeds_*` —— 分支与提交日期（无配额）
- `04_wkvm_structure_*` / `04b_wkvm_tracked_files_CLEAN_*` / `07_wkvm_README_full_*` —— wkvm 文件/License/README
- `06_wkvm_rwkv7_layout_bench_*` / `08_wkvm_rwkv_bench_artifacts_*` —— wkvm RWKV-7 状态布局与基准产物
- `09_wkvm_api_capabilities_*` / `11_wkvm_activity_license_migrate_*` —— wkvm API/活动/live-migrate
- `10_wkvm_branches_*` —— m4 分支实测与 diffstat
- `20_megatron_28b_head_*` / `22_megatron_28b_inventory_*` / `25_megatron_28b_configs_*` / `26_megatron_28b_artifacts_*` —— 28B 分支/配置/证据边界
- `27_megatron_other_branches_*` / `28_megatron_cp_testing_status_*` / `29_megatron_cp_28b_evidence_files_*` —— CP 分支 28B 证据与 1,041 文件
- `30_helicopter_probes_*` / `31…` / `32…` / `33…` / `34…` / `35…` —— Helicopter 全生态
- `36…` / `37…` / `38…` —— §7 许可证 + 文件树

## 附录 B：关键命令（可复查）

```bash
# 分支/日期（无 API 配额）
git ls-remote --heads https://github.com/xiaol/wkvm
git ls-remote --symref --heads https://github.com/TimeMobius/RWKV-Megatron HEAD
curl -sL https://github.com/xiaol/wkvm/commits/main.atom
curl -sL https://github.com/TimeMobius/RWKV-Megatron/commits/codex/qwen-rwkv28b-distill.atom
# wkvm LICENSE 双查
curl -s -o /dev/null -w '%{http_code}\n' https://raw.githubusercontent.com/xiaol/wkvm/main/LICENSE
git ls-files | grep -iE 'licen|copying|notice'
# Helicopter
curl -s -o /dev/null -w '%{http_code}\n' https://github.com/rwkv-rs/Helicopter
curl -s -o /dev/null -w '%{http_code}\n' https://raw.githubusercontent.com/rwkv-rs/Helicopter/main/README.md
curl -s 'https://api.github.com/repos/rwkv-rs/Helicopter' -o /dev/null -w '%{http_code}\n'  # 本次唯一 API 调用 → 404
# 28B 证据
git -C repos/RWKV-Megatron show origin/codex/qwen-rwkv28b-distill:configs/config-qwen-28b-distill-tp2-sp-pp4-balanced-smoke.yaml | head -4
git -C repos/RWKV-Megatron show origin/codex/rwkv7-cp:TESTING_STATUS.md | sed -n '17,37p'
git -C repos/RWKV-Megatron show origin/codex/rwkv7-cp:training-smoke/audit/28b-oom-20261022/tp4pp2cp1-no-offload-results.json
# 许可证
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://raw.githubusercontent.com/rwkv-rs/FlashRWKV2/main/LICENSE
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://codeberg.org/scarletwolf_ai/rwkv-toolcaller-bench/raw/branch/main/LICENSE
```

*报告完。所有结论均对应 `reports/state/evidence/` 中的原始命令输出（UTC 时间戳）；如需复核任一条，按附录 B 命令 + 对应证据文件即可。*
