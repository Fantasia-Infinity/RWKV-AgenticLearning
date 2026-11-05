# RWKV 生态增量/遗漏核验报告（task-3 / eco-delta）

- **核验员**：eco-delta（Team Lead 派出的核验员）
- **核验时间**：2026-11-05 20:08Z – 20:40Z（UTC）＝ 21:08–21:40 CET；环境：Snellius 登录节点（Snellius login node）
- **核验对象**：`rwkv-rs` GitHub 组织全量公开仓库 + `verl-rwkv` / `browsecomp-plus-eval` 等新信号 + 官方渠道（rwkv.cn / RWKV-LM / HF 官方模型卡）
- **基线文档**：内部交接 2026-11-05（未公开存档；公开综述见 `docs/ecosystem-review-2026-11-05.md`）（下称"交接"）
- **GitHub API 用量：0 次**（约束 ≤4 次）。全部证据走无配额路径：org 页面 HTML/embedded JSON、`raw.githubusercontent.com`、`commits.atom`、`git ls-remote`、`git clone --filter=blob:none`、HuggingFace API（非 GitHub）
- **产出**：本报告 + `reports/eco/evidence/`（证据原文与索引）+ `data/eco-org-repos.txt`（40 个仓库全量清单）

## 0. 一句话结论

**交接最大的系统性缺口不在"skyrl 之外没有 RL"，而在"rwkv-rs 组织级工程化已经跑起来、且 agentic 评测/Agent-SFT 已有公开资产"**：rwkv-rs 组织实际有 **40 个公开仓库**（交接完全未提其中 **30 个**）；`verl-rwkv` 是比 `skyrl-rwkv` 早 3 个月的真实 verl native RWKV 集成（43 个 RWKV 文件、18 个 PR，但 2026-08-02 起停更）；`browsecomp-plus-eval` 是 830 题 BrowseComp-Plus 的完整 RWKV agent 评测复现包（无公开分数、无 LICENSE）；生态外 `No-22-Github/RWKV-Agent` 已有**公开 568 题多步 agent 考卷 + 公开跑分**（官方 G1l 基模 187/568 = 32.9%，NoRA 适配器 320.5/568 = 56.4%）。同时 **2026-10-31 官方 G1l 发布 + 11-04 官方文档更新后，"官方主动不做 agentic"已不能原样引用**：官方 chat template 已支持 tool-call、官方模板与模型卡已明确给出 agentic 入口。**仍然成立的是：官方与社区都没有公开的"多轮 agentic RL 训练"配方与结果**（agent 能力目前靠 SFT/适配器 + 自建评测）。


> **公开版说明（2026-11-05）**：为符合公开发布政策，第三方全文/HTML/ATOM 已从本仓库移除（原始文件 sha256 见 `evidence/ARCHIVED.tsv` 与 `evidence/CITATIONS.md`，可按其中的 URL 重新抓取）。保留的命令输出与结构化数据可直接查看；正文引用中已移除的文件名仍保留，用于追溯当时证据。

---

## 1. 结论摘要：对交接 §0 / §1.2 / §5 / §8 的修订

### 1.1 逐条核验结果

| # | 交接原判断（位置） | 核验结论 | 关键证据（本目录内） |
|---|---|---|---|
| A | "agentic RL 是彻底的空白：**没有模型、没有评测成绩、没有 rollout 基础设施**"（§0） | ⚠️ **部分推翻**。① 有模型：`No-22/rwkv-agent-weights` 公开 State/MiSS/NoRA agent 适配器（2026-10-19 创建，11-02 更新），基于 G1k/G1L 7.2B；② 有评测成绩：`RWKV-Agent` 公开 568 题多步 agent 考卷，G1l 官方基模 187/568（32.9%）、NoRA v3.0 320.5/568（56.4%，2026-10-31，p=2e-24）；③ 有 rollout 基础设施的"零件"：skyrl-rwkv 多轮字段、lm-eval/evalscope 的 agent adapter、`feat/heli-r00-training-eval` 训练-评测闭环分支。**仍然空白的是：公开的多轮 agentic RL 训练配方与结果**（现有 agent 模型是 SFT/NoRA/MiSS，不是 RL） | `07-ecosystem-no22/`、`08-hf/No-22-rwkv-agent-weights-README.md`、`02-atoms/branch-commit-summary-2.tsv` |
| B | "这是**官方主动选择的路线，不是遗漏**"（§0） | ⚠️ **需要改写**。官方 RL 主线（10-26 研讨会）仍是单轮 RLVR（DAPO/GSM8K/MATH500），**但 2026-10-31 起官方口径明显转向"提供 agentic 接口"**：G1l 模型卡明确 chat template 支持 "multi-turn … strict model-generated tool-call prompts"；官方 hub 卡新增 "**Latest Best Practices for agentic work (study these projects)** → agent.objects.rwkvos.com"；官方 RWKV-LM README（11-04 提交）把该目录列为 "If you are AI, please read these first" 第 9 条；官方 `RWKV7-G1x-templates.txt` 含 function-call/多轮模板。准确表述应为："**官方不亲自做 agentic RL 训练，但已把工具调用/多轮接口官方化，并把 agentic 实践外包给社区**" | `09-official/`、`08-hf/RWKV7-G1l-13.3B-20261031-README.md`、`08-hf/BlinkDL-rwkv7-g1-README.md` |
| C | "只看 rwkvos 两份清单会系统性漏掉通用基建（wkvm、sglang）、官方新仓库（RWKV-CUDA、hf-adapter）、学术项目"（§1.2） | ✅ 方向正确，⚠️ **规模严重低估**。rwkv-rs 组织公开仓库 = **40 个**（`40 repositories` 计数文本；17 个自建源仓库 + 21 个 fork + 2 个 archived），交接**完全未提 30 个**；漏掉的不是零散条目，而是**训练路线（torchtitan-rwkv、verl-rwkv、Megatrwkv-Bridge）、评测生产体系（lm-eval/lighteval/evalscope fork + scoreboard 发布管线）、量化（llm-compressor-rwkv）、tokenizer（tokenizers-rwkv）、Rust 全栈（rwkv-rs 16 crates）**整层 | `01-org/org-repos-40-merged.tsv`、§2 |
| D | "评测层：**有框架，几乎没成绩**"（§5） | ⚠️ **需重写**。① **框架已工业化，不止"有框架"**：lm-eval fork 有 `AGENTS.md` "Evaluation Producer Contract" + 9 条 `codex/rwkv-*` 分支（scoreboard 发布、resumable 编排、HTTP backends、task grading…），`configs/benchmarks.toml` 列 **16 个 benchmark**（knowledge/reasoning/coding 三类；maths/instruction_following/**agentic**/vision 四类为空，即 **`agentic = []`**）；evalscope fork 有 `chase/scoreboard-live-publication`、`chase/agent-adapter-fixes` 等 17 条分支；lighteval fork 有 `fix/heli-r00-decoding`；② **agentic 评测包已公开**：`browsecomp-plus-eval`（830 题、100 步 agent loop、可复现，但无 scores）；③ **agentic 成绩已有公开的（生态外）**：No-22 568 题考卷 32.9%→56.4%。**仍然空白的是：标准公开 benchmark（BrowseComp-Plus 830 / τ-bench / BFCL 全量）的 RWKV 分数未发布**，且 `agentic = []` 类目在流水线里为空 | `06-eval-infra/`、`05-browsecomp/`、`07-ecosystem-no22/` |
| E | "skyrl-rwkv 是后训练的**最优基座**"（§3） | ⚠️ **降级为"当前最新活跃基座"**。`verl-rwkv`（fork verl-project/verl，branch `rwkv`）是更早（2026-05-21 创建）、更"正统 RL 框架"的 native 集成：`rwkv_lm` engine（EngineRegistry）、`verl/models/rwkv`、`verl/workers/engine/rwkv_lm`（43 个 RWKV 文件）、RWKV7 GRPO launcher、MaxRL 训练入口、每日 upstream rebase workflow、18 个 PR；但最后提交 **2026-08-02**，且上游 verl 至今 0 个 RWKV 文件。时间线（verl-rwkv 05-21 建 → 08-02 停；skyrl-rwkv 08-30 建 → 10-31 活跃，同一主力 `Cai-z-us`）说明 **skyrl 是"换乘"后的当前路径，不是唯一/最早的 RWKV RL 集成** | `04-verl-rwkv/`、`03-repo-pages/repo-created.tsv` |
| F | §8 完整栈五层 | ⚠️ **需补 3 个训练位 + 3 个基础设施位**：训练层 +`torchtitan-rwkv`（first-class RWKV-7，RWKVTrainer + FlashRWKV2，10-31 活跃）、+`verl-rwkv`（native rwkv_lm engine，08-02 停）、+`Megatrwkv-Bridge`（Megatron-Bridge fork，11-02 刚建、尚无 RWKV 代码）；算子/分词 +`fla-rwkv`（RWKV7 kernels）、+`tokenizers-rwkv`（Rust RWKV trie tokenizer）；Quantization 新层 `llm-compressor-rwkv`（RWKV7 量化分支）。Agent 运行时 `RWKV-LH` 的 main 停 10-08，但**侧分支活跃到 11-03**（SFT EOS / offline correction），交接的"10-08"过时 | `11-repos/trees/`、`02-atoms/branch-commit-summary-2.tsv` |
| G | "唯一支持**多轮**的 SFT 是 `howard-hou/RWKV-SFT`"（§7） | ❌ **被推翻（至少已不完整）**。No-22 用 8,846 行自建 Agent 轨迹（公开数据集 `No-22/rwkv-agent-distill`）+ `rwkv_lightning_cuda` 的 `rwkv_nora_tune_dp`（4 卡 DP）多轮 agent SFT 训出公开适配器；skyrl-rwkv 代码也有 `use_conversation_multi_turn`/loss_mask。多轮 SFT 已不止一个实现 | `08-hf/No-22-rwkv-agent-weights-README.md`、`07-ecosystem-no22/` |
| H | "没有模型"（§0 三连之一） | ❌ **部分推翻**：公开可下载的 RWKV agent 适配器（State/MiSS/NoRA）已存在并有跑分（见 A/G） | `08-hf/api/no22-agent-weights.json` |

### 1.2 建议直接替换的表述

- **§0 新版本（建议）**：
  > RWKV 的**单轮 RLVR 已经成熟且有官方组织**；**多轮 agentic RL 训练仍是公开空白**（无公开配方、无公开训练结果、rollout 层仍靠自建）。但 **agentic 能力本身不再空白**：官方 G1l（2026-10-31）已官方化 tool-call/multi-turn 提示接口并把 agentic 实践入口指向社区；社区已有公开的 568 题多步 agent 考卷与跑分（No-22，G1l 基模 32.9% → NoRA 适配器 56.4%）、830 题 BrowseComp-Plus 评测复现包（无分数）。因此工作量重心从"从零建评测"下调为"**接公开评测 + 自建多轮 rollout/RL**"。
- **§5 新版本（建议）**：把"有框架，几乎没成绩"改为"**评测已工业化（生产级 scoreboard 发布管线 + 22 benchmark 计划 + 多框架分工），但公开的标准 agentic 成绩仍缺；agentic 类目在流水线中登记为空（`agentic = []`），现有 agentic 公开成绩来自自建 568 题考卷**"。
- **§3 新版本（建议）**：在 `skyrl-rwkv` 前补一段 **`verl-rwkv`**（"更早的 verl 原生集成，2026-08-02 停更，18 PR，43 文件"），并把 "最优基座" 改为 "**当前活跃/推荐基座**"。
- **§8 新版本**：训练层加 `torchtitan-rwkv`、`verl-rwkv`、`Megatrwkv-Bridge`；L1 加 `fla-rwkv`/`tokenizers-rwkv`；新增 Quantization 小层 `llm-compressor-rwkv`。

---

## 2. rwkv-rs 全量仓库表（40 个公开仓库）

**方法**：`https://github.com/orgs/rwkv-rs/repositories?page=1..3&type=all` 页面自带 `"40 repositories"` 计数与 embedded JSON（`isFork`/`description`/`license`/`starsCount`/`lastUpdated`），无需 GitHub API；`createdAt` 来自各仓库页 HTML；"最后提交"取各仓库默认分支 `commits.atom`（wx-cli 因 HTTP 451 缺）。原始证据见 `evidence/01-org/`、`evidence/02-atoms/`、`evidence/03-repo-pages/`。

**统计**：40 = 17 个源仓库 + 21 个 fork + 2 个 archived；**7 个无 license**；**13 个最后提交在 2026-10 之后**；**30 个交接完全未提**。

### 2.1 全量表格（按层分组）

#### 2.1.1 训练层（RL / 预训练 / PEFT / 量化）

| 仓库 | 一句话定位（fork 关系） | 最后提交 | license | 交接未提？ |
|---|---|---|---|---|
| `verl-rwkv` | verl fork：native `rwkv_lm` engine（EngineRegistry）+ GRPO/MaxRL 示例 + 每日 upstream rebase；创建 05-21、最后提交 08-02，18 PR | 2026-08-02 | Apache License 2.0 | **是（0 次）** |
| `skyrl-rwkv` | SkyRL fork：社区 RLVR 平台（5 条 launcher：antidoom/flashreinforce/opd/sao/sft；算法含 GRPO/DAPO/CISPO/SAO/OPD/Anti-Doom/FTPO）；分支 feat/heli-r00-training-eval（10-28） | 2026-10-31 | Apache License 2.0 | 否（出现 x14） |
| `torchtitan-rwkv` | pytorch/torchtitan fork：first-class RWKV-7 训练（`torchtitan/models/rwkv7/` RWKVTrainer + FlashRWKV2 prepare_tuning + `rwkv_state_tuning` 实验；19 个 RWKV 文件） | 2026-10-31 | BSD 3-Clause "New" or "Revised" License | **是（0 次）** |
| `torchtitan-rwkv-old` | 已归档：旧 torchtitan RWKV fork（08-28 最后提交） | 2026-08-28 | BSD 3-Clause "New" or "Revised" License | **是（0 次）** |
| `Megatrwkv-Bridge` | NVIDIA-NeMo/Megatron-Bridge fork：2026-11-02 新建，尚无 RWKV 代码提交（Megatron+RWKV 桥的孵化位） | 2026-11-02 | Apache License 2.0 | **是（0 次）** |
| `antidoom-rwkv` | fork of Liquid4All/antidoom：Antidoom/FTPO 去复读工具；分支 codex/antidoom-rwkv-adapter 做了 RWKV 适配（08-02） | 2026-07-07 | Apache License 2.0 | **是（0 次）** |
| `any2rwkv` | Qwen3.5-2B 文本骨干→RWKV-7 循环混合的架构转换研究（Cai-z-us 主导，5★） | 2026-10-31 | NONE | **是（0 次）** |
| `llm-compressor-rwkv` | vLLM llm-compressor fork：RWKV7 量化支持；RWKV 分支 codex/rwkv7-quantization-policy（08-02） | 2026-07-31 | Apache License 2.0 | **是（0 次）** |
| `rwkv-peft-simple` | 重构版 RWKV PEFT 训练框架（PyTorch Lightning，Apache-2.0，2025-07 停更） | 2025-07-09 | Apache License 2.0 | **是（0 次）** |
| `rwkv-rs` | 组织同名 Rust 工作区：16 个 crates（rwkv-agent/rwkv-bench/rwkv-eval/rwkv-train/rwkv-infer…）+ book，546 文件；README 仍是 "Coming soon!"；main 停 2026-04-14（dev 分支 06-10） | 2026-04-14 | Apache License 2.0 | 否（出现 x6） |
| `rwkv-rs-stable` | 已归档：rwkv-rs 的 fork，README 是 Rust 基础设施愿景文（"RWKV needs infrastructure, not more scripts"） | 2026-05-16 | Apache License 2.0 | **是（0 次）** |
| `rwkv-rs-test` | RWKV 推理/训练框架的单测+基准测试套件（C++，2026-04-27） | 2026-04-27 | MIT License | **是（0 次）** |
| `RWKV-AUTODECO` | RWKV-Vibe/RWKV-LM-V7 fork + AutoDeco 实验（Lightning 框架，2026-01 停更） | 2026-01-27 | Apache License 2.0 | **是（0 次）** |

### 2.1.2 评测层

| 仓库 | 一句话定位（fork 关系） | 最后提交 | license | 交接未提？ |
|---|---|---|---|---|
| `lm-evaluation-harness-rwkv` | EleutherAI lm-eval fork：AGENTS.md 生产评测契约 + 9 条 codex/rwkv-* 分支（scoreboard 发布、resumable 编排、HTTP backends，10-29） | 2026-11-03 | MIT License | **是（0 次）** |
| `lighteval-rwkv` | HuggingFace LightEval fork：`src/rwkv_eval/` RWKV 评测（HTTP logprob/判分/FakeCoT）；分支 fix/heli-r00-decoding | 2026-11-03 | MIT License | **是（0 次）** |
| `evalscope-rwkv` | EvalScope fork：RWKV OpenAI 兼容评测 + scoreboard 迁移/发布；chase/* 分支含 agent adapter、durable resume（活跃至 11-02） | 2026-10-30 | Apache License 2.0 | **是（0 次）** |
| `browsecomp-plus-eval` | BrowseComp-Plus 830 题 RWKV agent 评测复现包（从 rwkv-skills 物理抽取、vendor vLLM-RWKV；无 scores、无根 LICENSE） | 2026-07-21 | NONE | **是（0 次）** |
| `rwkv-skills` | RWKV7 评测脚手架：BFCL v3/τ-bench/AgentBench/MCP-Bench/BrowseComp + agent loop + GPU 调度骨架（无 LICENSE；README 称公开成绩在 Helicopter） | 2026-08-09 | NONE | 否（出现 x2） |
| `chinese-babylm-eval-pipeline` | 2026 中文 BabyLM 评测流水线 fork（ZhoBLiMP/CLUE/Hanzi/Cog 三赛道） | 2026-05-18 | Apache License 2.0 | **是（0 次）** |

### 2.1.3 推理 / 算子 / 分词 / 服务

| 仓库 | 一句话定位（fork 关系） | 最后提交 | license | 交接未提？ |
|---|---|---|---|---|
| `vllm-rwkv` | vLLM fork：RWKV-7 serving 后端（`wkv_mode=fp32io16` 等；4★） | 2026-10-31 | Apache License 2.0 | 否（出现 x3） |
| `FlashRWKV2` | TileLang RWKV-7 算子库（BF16 训练/推理共用 forward、FP32 state；v0.1.0a18） | 2026-11-02 | MIT License | 否（出现 x4） |
| `hf-adapter` | RWKV-7 HuggingFace/Transformers 纯 PyTorch 可读参考实现（8★） | 2026-10-25 | MIT License | 否（出现 x1） |
| `transformers-rwkv` | HuggingFace transformers fork：RWKV-7 原生集成；分支 fix/rwkv-tool-call-history 渲染工具调用历史（10-31） | 2026-10-31 | Apache License 2.0 | 否（出现 x1） |
| `tokenizers-rwkv` | HuggingFace tokenizers fork：RWKV trie tokenizer + RWKV vocab 转换器（Rust） | 2026-10-31 | Apache License 2.0 | **是（0 次）** |
| `fla-rwkv` | flash-linear-attention fork：含 RWKV6/7 kernels 与 HF modeling（47 个 rwkv 文件） | 2026-08-06 | MIT License | **是（0 次）** |
| `rwkv7-ascend-npu` | RWKV-7 在 Ascend 910B3 NPU 的推理+serving（含 sglang port、AscendC、NPUGraph；7 条 wangyue/* 分支） | 2026-07-24 | NONE | **是（0 次）** |
| `Albatross` | BlinkDL 高效 RWKV 推理引擎的 fork（CUDA/CUDAGraph；RWKV7 7.2B fp16 10250 tok/s@5090） | 2025-10-09 | Apache License 2.0 | 否（出现 x2） |

### 2.1.4 Agent / 应用

| 仓库 | 一句话定位（fork 关系） | 最后提交 | license | 交接未提？ |
|---|---|---|---|---|
| `RWKV-LH` | 持久可验证长程编码 Agent/runtime（MIT，4★）；main 停 10-08，但分支活跃至 11-03（SFT EOS/offline correction/planner-executor 归档） | 2026-10-08 | MIT License | 否（出现 x2） |
| `RWKV-Scout` | 以 RWKV 为决策核心的联网检索 Agent（MIT，2★；单轮检索 Beta，非长程执行器） | 2026-08-21 | MIT License | 否（出现 x2） |
| `codex-compact-router` | 本地 OpenAI/Codex 请求路由器（让 context-compact 请求走快速通道，压缩失败自动换模型重试） | 2026-06-02 | MIT License | **是（0 次）** |

### 2.1.5 无关或弱相关的 fork / 杂项（同组织、非 RWKV 主线）

| 仓库 | 一句话定位（fork 关系） | 最后提交 | license | 交接未提？ |
|---|---|---|---|---|
| `burn` | Rust 深度学习框架 tracel-ai/burn 的 fork（无 RWKV 专属改动，Rust 栈早期依赖） | 2025-12-15 | Apache License 2.0 | **是（0 次）** |
| `cubecl` | Rust 多平台 GPU 计算语言 tracel-ai/cubecl 的 fork（无 RWKV 专属改动） | 2025-11-13 | Apache License 2.0 | **是（0 次）** |
| `MediaCrawler` | 自媒体平台爬虫 fork（与 RWKV 无直接关系，疑为数据采集工具） | 2025-07-16 | Other | **是（0 次）** |
| `originium` | Rust 异步数据处理框架（7★，无根 LICENSE 文件但 README 徽章写 MIT，2025-09 停更） | 2025-09-05 | NONE | **是（0 次）** |
| `rhine` | Rust LLM/agent 框架 "Rhine Lab" 的代码核心（含 chat_tool/tool_use 模块，GPL-3.0，2025-09 停更） | 2025-09-02 | GNU General Public License v3.0 | **是（0 次）** |
| `rhine-schema-derive` | RHINE LLM frame 的 proc-macro crate（MIT，2025-02） | 2025-02-18 | MIT License | **是（0 次）** |
| `rhi` | 空壳 Rust crate（仅 Cargo.toml+lib.rs，2024-11 后无更新） | 2024-11-07 | GNU General Public License v3.0 | **是（0 次）** |
| `rwkv-cc` | 线性 RNN 生化语言模型（2★，无许可证，2025-05 停更） | 2025-05-16 | NONE | **是（0 次）** |
| `wandb-rs` | NousResearch/wandb-rs fork：Rust wandb 客户端（2026-01 停更） | 2026-01-31 | NONE | **是（0 次）** |
| `wx-cli` | 微信本地数据 CLI（fork；本网络访问返回 HTTP 451，仅 org 元数据可见） | （HTTP 451 不可读） | Apache License 2.0 | **是（0 次）** |

### 2.2 交接遗漏清单：30 个"完全没有出现过"的仓库

按影响排序（★ = 直接冲击交接结论）：

| 类别 | 从未被交接提及的仓库 | 为什么重要 |
|---|---|---|
| RL / 训练路线 | **`verl-rwkv`★**、**`torchtitan-rwkv`★**、`torchtitan-rwkv-old`、**`Megatrwkv-Bridge`★**、`antidoom-rwkv`、`any2rwkv`、`llm-compressor-rwkv`、`RWKV-AUTODECO` | 交接 §2 说训练层"五条互不兼容的路线"，实际至少 **7 条**（+torchtitan、+verl）；量化（llm-compressor）整层缺失 |
| 评测 / 评测基建 | **`browsecomp-plus-eval`★**、**`lm-evaluation-harness-rwkv`★**、`lighteval-rwkv`、`evalscope-rwkv`、`chinese-babylm-eval-pipeline` | 交接 §5 只列 4 个评测，实际有"lm-eval + LightEval + EvalScope 三框架分工 + scoreboard 发布管线"的生产体系 |
| 推理 / 算子 / 分词 | `tokenizers-rwkv`、`fla-rwkv`、`rwkv7-ascend-npu` | Rust RWKV trie tokenizer（官方 G1l 内置）、FLA 的 RWKV7 kernels、Ascend NPU serving —— 交接 §8 L1 全缺 |
| Rust 全栈 | `rwkv-rs-stable`、`rwkv-rs-test`（组织同名仓库 `rwkv-rs` 虽以"组织名"出现 6 次但从未被描述，见下表） | 组织同名仓库本体是 546 文件的 Rust workspace（16 crates，含 `rwkv-agent`/`rwkv-bench`/`rwkv-eval`/`rwkv-train`），交接 §8 完全没有 Rust 栈 |
| Agent / 应用 | `codex-compact-router` | 与 RWKV 弱相关（Codex 请求路由），但属组织公开仓库 |
| 无关/弱相关的 fork 与杂项 | `burn`、`cubecl`、`MediaCrawler`、`originium`、`rhine`、`rhine-schema-derive`、`rhi`、`rwkv-cc`、`rwkv-peft-simple`、`wandb-rs`、`wx-cli` | 多为 Rust 生态依赖或个人项目；`rwkv-peft-simple`（PEFT 训练框架）与 `rwkv-cc`（生化 LM）有一定生态价值 |

**另有 5 个"提了但覆盖不足/状态过时"**：

| 仓库 | 交接写法 | 现状（2026-11-05） |
|---|---|---|
| `RWKV-LH` | 列在 §8 L4、§4.2；main 最后提交 10-08 | 侧分支活跃到 **11-03**：`single-model-agent`（RWKV_CORRECTION_20261103）、`archive/planner-executor-20261102`（SFT_EOS_20261102：transcript wire 的监督式 EOT）、`chase/frontend-executor-only` → **不是"10-08 就停了"** |
| `rwkv-rs` | 只作为 GitHub 组织名（skyrl-rwkv 等的 owner） | 仓库本体是 **Rust RWKV 全栈**（16 crates + book + agent/bench crate），main 停 04-14、dev 到 06-10；交接从未描述 |
| `hf-adapter` | §1.2 只举例"官方新仓库（RWKV-CUDA、hf-adapter）" | 8★、MIT、最后提交 10-25，是 G1l 官方 Transformers 集成的参考实现之一 |
| `skyrl-rwkv` | 只写 main 分支 | 新增侧分支 **`feat/heli-r00-training-eval`（10-28，Cai-z-us，"resume bounded training and evaluation phases"）**——训练-评测闭环（Helicopter round 0）证据 |
| `rwkv_lightning`（外部，非 rwkv-rs） | §4.2 当作活跃后端 | 官方 rwkv.cn 教程已标注 **"rwkv_lightning 已归档，推荐使用 rwkv_lightning_cuda"**（教程页 title/meta description 原文） |

### 2.3 表内数据的来源与口径

- **stars/license/description**：org 页面 embedded JSON（抓取 20:08Z）。`NONE` = GitHub 未识别到 license（不等于仓库必然无版权声明，例如 `originium` 无 LICENSE 文件但 README 徽章写 MIT）。
- **最后提交**：默认分支 `commits.atom` 第一条 `<updated>`。`wx-cli` 返回 **HTTP 451**（Unavailable For Legal Reasons；GitHub 对该仓库页面/atom/raw 均 451），本网络无法读取，只能保留 org 元数据（fork、Apache-2.0、description "WeChat local data CLI with daemon architecture"、org 页面 lastUpdated 2026-04-19）。
- **created**：仓库页 HTML 的 `"createdAt":"..."`（不是 GitHub API）。
- **archived**：org 页面 JSON `"type":"Public archive"`，共 2 个（`rwkv-rs-stable`、`torchtitan-rwkv-old`）。
- 每行一句话定位的原始 README/树证据：`evidence/11-repos/readmes/`、`evidence/11-repos/trees/`。

---

## 3. 重点仓库深挖

### 3.1 `rwkv-rs/verl-rwkv` —— verl（主流 RL 框架）的 RWKV 原生集成（交接 0 次提及）

**结论先说**：这不是空 fork，也不是"只同步上游"的镜像，而是一次**真实的、工程化的 verl × RWKV-7 集成**（native `rwkv_lm` engine + GRPO/MaxRL 训练入口 + 每日 upstream rebase），**创建于 2026-05-21，比 skyrl-rwkv（2026-08-30）早 101 天**，最后提交 **2026-08-02**；随后主力（`Cai-z-us`，同时也是 skyrl-rwkv 主力）转向 SkyRL。**它直接冲击交接 §3 "skyrl-rwkv 是后训练的最优基座/唯一 RL 基座" 的表述**——更准确的说法是：verl 集成先做、8 月初停更；skyrl 是 8 月底起接班的当前活跃路径。

| 项 | 值 | 证据 |
|---|---|---|
| 身份 | fork of `verl-project/verl`（Apache-2.0），0★；**无 `main` 分支，默认分支 = `rwkv`** | `03-repo-pages/verl-rwkv.html`、`04-verl-rwkv/refs-heads.txt` |
| created | 2026-05-21 | `03-repo-pages/repo-created.tsv` |
| 最后提交 | `b564e2f`，2026-08-02T00:01Z，`Caizus <…>`，"fix(eval): bind external metrics to runtime lineage" | `04-verl-rwkv/head-commit.txt`、`02-atoms/verl-rwkv.xml` |
| PR 数 | **18 个**（`refs/pull/1..18`）；另有 2 条侧分支（07-28 / 08-02） | `04-verl-rwkv/refs-heads.txt` |
| RWKV 专属文件 | **43 个**（`grep -ic rwkv`）；上游 verl `main`（HEAD `e41dd69`，2026-11-05）**0 个** | `04-verl-rwkv/rwkv-files.txt`、`10-checks/verl-upstream-rwkv-count.txt` |
| 主要贡献者 | `Cai-z-us`（与 skyrl-rwkv 同一主力） | `02-atoms/verl-rwkv.xml` |

**它到底集成了什么**（从 fork 树 + 文档核实）：

1. **native `rwkv_lm` 训练引擎**：`verl/workers/engine/rwkv_lm/`（`args.py` / `batch_bridge.py` / `checkpoint.py` / `env.py` / `loss_bridge.py` / `native_runner.py` / `tokenizer_bridge.py` / `weight_bridge.py` / `weight_mapping.py` …），通过 `EngineRegistry` 注册为 `rwkv_lm` 后端；官方 README 明确设计原则："**preserve rwkv-lm's native behavior: Lightning/DeepSpeed entrypoints, `.pth` checkpoints, CUDA extension env vars, precision flags … It should not turn RWKV into a fake HuggingFace/FSDP model just to fit the existing transformer engine path.**"（`04-verl-rwkv/engine-rwkv_lm-README.md`）
2. **模型边界层**：`verl/models/rwkv/`（config / tokenizer / native imports / weight mapping），`04-verl-rwkv/models-rwkv-README.md` 写明这是 "rwkv-lm 训练适配器与 verl canonical vLLM rollout 路径共享的边界"。
3. **示例/配方**：`examples/rwkv_trainer/run_rwkv7_grpo_rwkv_lm.sh` —— RWKV7 `g1g-1.5b-…-ctx8192` + GSM8K GRPO（7 train GPU + 1 vLLM-RWKV rollout GPU，`VLLM_RWKV7_WKV_MODE=fp32io16`，`chunk_ctx`、动态 bsz 等），`math_verify_reward.py`/`math_dapo_reward.py`；配置位 `verl/trainer/config/{actor,engine,model,optim,ref}/rwkv_lm.yaml`。
4. **MaxRL 训练入口**：`verl/trainer/maxrl.py`（"RWKV MaxRL's public configuration and training entry point"，TOMl 配置、DAPO Math-17k、32 prompts×16 responses/step、**外部评测生命周期：训练中写 `global_step_<N>/actor/rwkv_lm.pth` 后调用 `helicopter eval --config configs/eval/maxrl_math.toml`，用退出码/JSON metrics 回填**）。见 `04-verl-rwkv/examples-rwkv_trainer-config-README.md`。
5. **工程可持续性**：`.github/workflows/rebase-rwkv.yml` —— **每日 cron 自动把 RWKV commits rebase 到上游 verl main**，并有 CPU 测试 `tests/tools/test_rwkv_rebase_workflow_on_cpu.py`；但（与 skyrl 一样）CPU CI 未把 `tests/workers/engine/rwkv_lm/` 挂进 workflow（`cpu_unit_tests.yml` grep 不到 rwkv）。
6. **多轮/agent 能力**：fork 完整保留了上游 verl 的多轮 agent 基础设施 —— `verl/experimental/agent_loop/agent_loop.py`、`single_turn_agent_loop.py`、`docs/advance/agent_loop.rst`、`examples/tutorial/agent_loop_get_started/`、multi-turn 数据预处理与 tool 测试；**但 RWKV 侧只有单轮 GSM8K GRPO 配方，没有 RWKV 多轮 agent 配方或验证**（证据：`04-verl-rwkv/rwkv-files.txt` 与 `examples/rwkv_trainer/` 只有 1 个 launcher）。结论：**"支持多轮/agent 的代码底座"成立，"RWKV agent 已训过"不成立**。

**为什么停更 / 与 skyrl 的关系（时间线）**：

```
2026-05-21  verl-rwkv 创建
2026-07-28  chore(rwkv): remove obsolete numerical probes（侧分支）
2026-08-01  rwkv 分支最后一批 RWKV 提交（separate RWKV config ownership / bucketed weight reload / external eval runtime）
2026-08-02  最后提交（fix(eval): bind external metrics to runtime lineage）
2026-08-30  skyrl-rwkv 创建（同一主力 Cai-z-us）
2026-10-28  skyrl-rwkv 侧分支 feat/heli-r00-training-eval（训练-评测闭环）
2026-10-31  skyrl-rwkv main 最后提交
```

**对交接的影响（建议修订 §3）**：§3 的 "这是后训练的最优基座" 应改为 "**当前活跃/推荐的 RL 基座**"；并补一句历史事实："社区先在 verl 上做了 RWKV-7 原生集成（2026-05→08，43 文件、18 PR、GRPO/MaxRL launcher、每日 rebase），2026-08 后主力切换到 SkyRL fork（skyrl-rwkv），verl-rwkv 不再更新"。若目标是 **agentic RL**，verl 生态（上游 agent_loop、uni-agent 等 2026-05 新闻）在"多轮 rollout 基础设施"上其实比 skyrl 更成熟，值得作为 P3 的备选基座重新评估（见 §5 未决 2）。

**证据**：`evidence/04-verl-rwkv/`（树、43 文件清单、上游 0 文件计数、三个 README、launcher、rebase workflow、maxrl.py、HEAD commit、refs）；`evidence/03-repo-pages/verl-rwkv.html`。

---

### 3.2 `rwkv-rs/browsecomp-plus-eval` —— 830 题 BrowseComp-Plus 的 RWKV agent 评测复现包（交接 0 次提及）

**结论先说**：这是**真实的多步 agentic 搜索评测框架**（不是玩具）：830 道官方 BrowseComp-Plus 问题、`search(top5)/get_document/final_answer` 工具循环、3 路并行候选路由、vendored vLLM-RWKV、BM25+PostgreSQL、官方 judge 导出。**但没有公开分数，也没有 LICENSE**。它证明"agentic 评测框架"不等于空白；但"标准 agentic 公开成绩"依然缺。

| 项 | 值 | 证据 |
|---|---|---|
| 身份 | 非 fork 源仓库，1★，无描述补充/无根 LICENSE | `01-org/org-repos-40-merged.tsv` |
| created = 最后提交 | **2026-07-21**（2 个 commit，作者 `Chase Jay (email redacted)`，即 org 里的 `w1c2j3`） | `03-repo-pages/repo-created.tsv`、`05-browsecomp/git-log.txt` |
| 大小 | 6,772 文件 / 164 MB，其中 `vendor/` 6,064 文件（vLLM-RWKV 源码快照） | `05-browsecomp/file-count.txt`、`05-browsecomp/top-level-counts.txt` |
| 来源链（关键） | **从 `rwkv-skills` 的 `upload/g1h-eval-runtime-20260720` 分支 @ `54639619f859` 物理抽取**（2026-07-21）；`rwkv-skills` 当前公开 heads 只有 `main/eval/old/vllm-rwkv/perf/*`，**该 upload 分支已不在公开 heads** → 导出自一个已删除/非公开分支 | `05-browsecomp/MANIFEST.md`、`10-checks/rwkv-skills-branches.txt` |
| license | **无根 LICENSE**；`THIRD_PARTY_NOTICES.md` 自述："The source checkout used to assemble this package did not contain a top-level license file for the RWKV evaluation harness. Confirm and add the intended license before publishing this package as a public GitHub repository."；vendored vLLM-RWKV 为 Apache-2.0（保留 LICENSE） | `05-browsecomp/THIRD_PARTY_NOTICES.md`、`05-browsecomp/root-license-check.txt` |

**它跑什么（README 原文要点）**：

- 数据：**830 道官方 BrowseComp-Plus 问题**（`texttron/BrowseComp-Plus` 资产需自备，含 2GB+ corpus、BM25 index、qrels）。
- Agent loop：`src/eval/tasks/function_calling/browsecomp_plus.py`（**2,544 行**）—— `DEFAULT_BROWSECOMP_PLUS_MAX_STEPS = 100`，工具 `search`(top 5) / `get_document` / `final_answer`（带 cited explanation + answer + confidence 0-100）；历史预算 24,000 字符、总 prompt 预算 28,000。
- 并行候选：`parallel_candidate_router`（3 shards/candidates，16-candidate batch，8,000 context chars，每个 candidate 192 tokens；aggregation 选 grounded call 或 final answer）。
- 推理：**vendored vLLM-RWKV**（`VLLM_USE_V2_MODEL_RUNNER=1`、10240 ctx、32768 batched tokens、1024 seqs），OpenAI 兼容 `/v1/completions`；RWKV flower JSON prompt（`rwkv_flower_json`）+ `rwkv-json` 工具调用 IO。
- 评测：inline/defer/judge 三种 judge 模式（judge 一般 Qwen3-32B via vLLM）+ 官方 one-JSON-per-query 导出 + 官方 evaluator；指标 `avg@1/success_rate`、`Recall`（检索覆盖）、confidence 校准、audit 完整性（830 唯一 keys、无 judge_pending）。
- **是否跑过**：README 写 "The **captured full-run profile** is: … 100 agent steps … 16 concurrent episodes"、"Defaults mirror the **evaluated setup**"，并规定"正式结果必须有全部 830 唯一 attempt keys" → **有一次完整 run 的配置档案，说明跑过**；但包内**不含任何 scores/DB 行/logs**（README 开头与 MANIFEST 明确 excluded）。

**与 G1h 的关系（交接完全没提 G1h）**：`configs/g1h/_templates.toml` 是 **G1h 专用提示覆盖**："G1h CoT uses the official form: `User✿<Q>✿` then `Bot✿<think>`；token 10060 是 RKWV 词表的 ✿ token"；`scripts/experiments/run_parallel_candidate_router_experiment.py` 的 `DEFAULT_MODELS` 是 **`rwkv7-g1f-2.9b-20260420-ctx8192`、`rwkv7-g1g-13.3b-20260523-ctx8192`、`rwkv7-g1g-2.9b-20260526-ctx8192`** → 该评测路径在 **G1f/G1g/G1h** 上工作过，而交接只讨论 G1g/G1k/G1l。

**超出 BrowseComp 的内容**：这个包是从 `rwkv-skills` 的 `src/` 整体抽出的，因此还带 **τ-bench v1/v2/v3-official（含 user simulator）、BFCL v3/v4、AgentBench、MCP-Bench、ComplexFuncBench、BrowseComp、LongBench、API-Bank、ToolAlpaca 等 function_calling 任务（32 个文件）+ agent_bench（13 个文件）**；`scripts/experiments/` 还有 τ-bench 的 parallel-candidate 实验。也就是说：**交接 §5 说“rwkv-skills 有框架但零成绩”时，其 framework 的 agentic 部分已经是可运行的完整实现，并被公开导出了一份 BrowseComp-Plus 复现包**。

**对交接的影响（建议修订 §5）**：把"agentic 评测空白"降级为"**有可复现的 830 题 BrowseComp-Plus agentic 评测包（rwkv-skills 派生，无公开分数/无 LICENSE），标准公开分数仍未发布**"；同时注意该包的 **license 风险**（无根 LICENSE，vendored 部分 Apache-2.0）——不能直接商用/再分发。

**证据**：`evidence/05-browsecomp/`（README、MANIFEST、THIRD_PARTY_NOTICES、.env.example、g1h 模板、router 实验脚本、git log、文件统计、agent-loop grep、LICENSE 检查）。

---

### 3.3 其余新仓库速览（只列会改变生态图的）

| 仓库 | 定位 | 活跃度 / 关键证据 |
|---|---|---|
| **`torchtitan-rwkv`**★ | pytorch/torchtitan fork，**first-class RWKV-7 训练**：`torchtitan/models/rwkv7/`（model/parallelize/trainer/state_dict_adapter/provider/checkpoint/config_registry）+ `torchtitan/experiments/rwkv_state_tuning/`（state tuning artifact/converter）+ `tests/unit_tests/cpu/test_rwkv7*.py`；README 增补 "RWKV-7 training"（`RWKVTrainer` 首步跑 FlashRWKV2 `prepare_tuning`，之后 CUDA Graph capture；`FlashRWKV2==0.1.0a17`）；另有 10-26 "prepare FlashRWKV2 training profiles" 提交 | created 2026-08-28，最后提交 **2026-10-31**（`02-atoms/torchtitan-rwkv.xml`；commit `850b558`（首版）、`b05910a`（FlashRWKV2 profiles）的完整 diff 见 `06-eval-infra/torchtitan_first_class_rwkv7.diff`、`06-eval-infra/torchtitan_flashrwkv_profiles.diff`）→ **交接 §2 的训练五路线应为七路线** |
| **`Megatrwkv-Bridge`** | NVIDIA-NeMo/Megatron-Bridge fork，**2026-11-02 刚建**；最新 20 条提交全部是上游 NVIDIA 同步（AUT-*），树里 **0 个 rwkv 命名文件** → 目前只是"Megatron+RWKV 桥"的孵化位，尚未有 RWKV 代码 | `02-atoms/Megatrwkv-Bridge.xml`、`11-repos/trees/Megatrwkv-Bridge.txt` |
| **`lm-evaluation-harness-rwkv`**★ | EleutherAI lm-eval fork；**main 上有 `AGENTS.md` 生产评测契约**（"Evaluation Producer Contract"：logprob vs generative 模式校验、1.5B/2.9B smoke、截断语义、scoreboard 发布边界……）；**9 条 `codex/rwkv-*` 分支**（scoreboard-publishing、eval-orchestration、http-backends、task-grading、campaign-configs…，10-29 由 `Big-dreamer-creator` 提交）：其中 `codex/rwkv-scoreboard-publishing` 新增 `configs/benchmarks.toml`（**16 个 benchmark：wmdp、babilong、drop、ruler、infinitebench…；`agentic = []`**）+ `lm_eval/_cli/publish.py` + `lm_eval/loggers/scoreboard.py` + 4 个测试 | 最后提交 **2026-11-03**（main，Cai-z-us）；证据 `06-eval-infra/` |
| **`evalscope-rwkv`** | ModelScope EvalScope fork；**17 条 `chase/*` 分支**（agent-adapter-fixes、v2-agent-adapter-fixes、scoreboard-live-publication、scoreboard-migration-pr3、bound-scoreboard-evidence、durable-eval-resume、coding-scorer-fixes…），最近提交 2026-11-02（"refactor(agent): share OpenAI request helpers and tidy BFCL/ResearchR…"）；main 只到 10-30（上游同步） | 分支证据 `02-atoms/branch-commit-summary*.tsv`、`06-eval-infra/evalscope_agent_adapter.diff` → **有 agent adapter（BFCL/Research）+ scoreboard 发布**的实做 |
| **`lighteval-rwkv`** | HF LightEval fork；`src/rwkv_eval/`（rwkv_model.py、answer_extract、add_benchmarks、upload…）；侧分支 **`fix/heli-r00-decoding`（10-28，"update approved CoT decoding defaults"）** | 最后提交 2026-11-03（main）；`02-atoms/lighteval-rwkv.xml`、branch summary |
| **`llm-compressor-rwkv`** | vLLM llm-compressor fork；侧分支 **`codex/rwkv7-quantization-policy`**（08-02，"fix(quantization): pin rank-aware Transformers"）→ RWKV7 量化（INT4/FP8 方向）在推进 | created 2026-08-02；`02-atoms/llm-compressor-rwkv.xml`、`more-branch-commits.tsv` |
| **`tokenizers-rwkv`** | HF tokenizers fork：**Rust RWKV trie tokenizer**（`tokenizers/tk-encode/src/models/rwkv_trie/mod.rs`）+ `temp/convert_rwkv_vocab.py`；官方 G1l 模型卡宣称的 "exact linear-time tokenizer / bundled RWKV trie" 与此对应 | 最后提交 2026-10-31；`11-repos/trees/tokenizers-rwkv.txt` |
| **`fla-rwkv`** | `fla-org/flash-linear-attention` fork，含 `fla/layers/rwkv6.py`、`rwkv7.py`、`fla/ops/rwkv4/6/7/*`（含 TileLang/FlashRWKV backend）、`fla/models/rwkv6/7` HF modeling；47 个 rwkv 文件 | 最后提交 2026-08-06；`11-repos/trees/fla-rwkv.txt` |
| **`any2rwkv`** | Qwen3.5-2B 文本骨干→RWKV 循环混合的**架构转换研究**（GDN→RWKV-7 WKV、GQA→positive-feature state），5★ | 最后提交 2026-10-31，Cai-z-us 16/20 提交 |
| **`rwkv7-ascend-npu`** | RWKV-7 在 Ascend 910B3 NPU 的推理/serving（serving framework + sglang port + AscendC + NPUGraph/state-slot 实测 1509~1537 tok/s@0.1B shape），7 条 `wangyue/*` 分支 | 最后提交 2026-07-24；`11-repos/readmes/rwkv7-ascend-npu.readme` |
| **`rwkv-rs`（Rust 工作区）** | 组织同名仓库：**16 个 crates**（rwkv、rwkv-agent、rwkv-bench、rwkv-config、rwkv-data、rwkv-derive、rwkv-eval、rwkv-export、rwkv-infer、rwkv-lm、rwkv-lm-eval、rwkv-nn、rwkv-prompt、rwkv-trace、rwkv-train…）+ `rwkv-rs-book/` + `note_for_agents/` + CI（benchmark/coverage gates）；但 **README 仍是 "Coming soon!"** | main 最后提交 **2026-04-14**（dev 分支 06-10）→ 项目 dormant，交接完全没描述 Rust 栈 |
| **`antidoom-rwkv`** | fork of **`Liquid4All/antidoom`**（Liquid AI 的 Antidoom/FTPO 工具）；侧分支 `codex/antidoom-rwkv-adapter`（08-02，"harden generation and resume preflight"）→ RWKV 的 Anti-Doom/FTPO 工具链 | 21 文件、2 commits（mlabonne/nathanrchn 上游）；`02-atoms/antidoom-rwkv.xml` |
| `chinese-babylm-eval-pipeline` | 2026 中文 BabyLM 评测流水线 fork（NLU/Hanzi/Cog 三赛道：ZhoBLiMP、CLUE、fMRI） | 最后提交 2026-05-18 |
| `codex-compact-router` | 本地 OpenAI/Codex 请求路由器（compact 请求快速通道 + 失败换模型重试），MIT | 最后提交 2026-06-02 |

### 3.4 生态外反证（非 rwkv-rs 组织）：`No-22-Github/RWKV-Agent` 已有公开的 568 题多步 agent 考卷与跑分

这是**对交接 §0/§5 最直接的反证**，且交接并非完全不知道这个仓库（§4.2 把它当 `rwkv_lightning` 的后端用户、§11 链接其 G1l 提示词评测报告），但**没有记录它的 agent 评测体系与成绩**。

1. **公开 agent 考卷数据集**：`No-22/rwkv-agent-exam`（HF 数据集，created **2026-10-30**，lastModified 11-02，**2,321 文件**，下载 1,510）——`exam/SUITES.md` 定义 **`agent-exam-v1.2`：568 题**（快测 `agent-exam-quick-v1.2`：76 题；15 个场景：hybrid 78 / tabular 62 / notool 59 / docs 57 / config 51 / logs 50 / web 39 / filesystem 30 / script 27 / bashprobe 26 / bfcl irrelevance 20 / **bfcl 多轮 20** / code 15 / weatherprobe 14 / bfcl missing 20），每题带 `case.json` + `verify.py` + `NOTES.md`，有版本/hash 表（v1.0→v1.2）。
2. **公开跑分报告**（仓库 `docs/evaluations/`）：**2026-10-31 同端点同口径**：
   | 模型 | 考卷 strict | 说明 |
   |---|---|---|
   | `rwkv7-g1l-7.2b-20261031` 官方基模 | **194 / 180（均值 187.0，32.9%）** | 两遍 568 题，invalid 0 |
   | 同基模 + NoRA r16 适配器（think-sft-mix final） | **315 / 322（strict；超时重跑后 316/325 = 320.5，56.4%）** | 逐题 +191/−41，p=2e-24 |
   | 参考：temp-3797 + checkpoint-5004 | 280/273 | 旧基模 |
   - 其他指标：带历史步骤空思考 84.3%/85.0% → **0%**；零调用题第一步直答 12/13 → 37/36；bfcl 多轮 **20/20**；IFEval 英文 59.4→69.4；GSM8K 77.2→92.2。
   - 每题模型调用 **4.98–6.43 次**（多步证据，非单轮）。
3. **公开适配器权重**：`No-22/rwkv-agent-weights`（HF，created **2026-10-19**，lastModified **11-02**，tags: agent/tool-use/state-tuning/miss/nora）——State（16MB/7.2B）、MiSS r16（~36MB）、NoRA r16（~72MB，v3.0 推荐）；训练器 `rwkv_lightning_cuda` 的 `rwkv_nora_tune_dp`（4 卡 DP），训练数据 8,846 行 agent 轨迹（公开数据集 `No-22/rwkv-agent-distill`，2026-10-19 创建，含 teacher 轨迹/QC ledger）。
4. **评测工程**：`RWKV-Agent` 内置 `agent-eval`（Go 写的 `rwkv-cli agent-eval`，harness `rwkv-agent-eval-v23`；`benchmark-protocol.md` 规定格式/采样/预算/题库 hash/闸门：16 步、4096 max tokens、2048 decision tokens、30min case timeout、agent-wire-think-v2.0、agent-tool-v3.2、96 并发）。

**意义**：交接 §0 的"没有模型、没有评测成绩"在 **agentic 能力（SFT 路线）** 上已被推翻；§5.1 的"多步对所有模型 0/2"只适用于 **Scarlet Wolf 的单轮 toolcaller-bench harness**（其 README 自述"harness 按构造就是单轮"），不能外推到整个生态。**仍然成立的空白**：没有公开的"多轮 agentic **RL**"训练配方/结果；No-22 的适配器是 SFT/state-tuning/NoRA。

**局限（必须写进结论）**：① 考卷是**自建**的，非标准公开 benchmark（不等价于 BrowseComp-Plus/τ-bench/BFCL 全量）；② 仓库与数据/权重**无 LICENSE**（RFW-Agent README："公开分发前需确认上游授权并选定项目许可证"），不可直接商用；③ 报告列的 raw run 数据在 `local/runs/`（gitignore），未公开；④ 单次跑分波动大（文档自述同配置两次有 21% 翻转），看"能力面板"而非总分。

### 3.5 贯穿多个仓库的隐藏主线：`Helicopter`（私有评测/scoreboard 系统）

交接 §5 已经注意到 `rwkv-skills` README 说"公开成绩在 Helicopter 仓库"且该仓库 404。本次核验发现 **Helicopter 不是单点，而是整套评测/scoreboard 系统的代号**，被至少 5 个仓库引用：

- `verl-rwkv` 的 MaxRL 配置：`[evaluation]` 生命周期调用 `helicopter eval --config configs/eval/maxrl_math.toml`，用 `MAXRL_EVAL_WEIGHT`/`MAXRL_EVAL_RESULT_PATH` 回填 metrics（`04-verl-rwkv/examples-rwkv_trainer-config-README.md`）；
- `lighteval-rwkv` 分支 **`fix/heli-r00-decoding`**（2026-10-28，"update approved CoT decoding defaults"）；
- `skyrl-rwkv` 分支 **`feat/heli-r00-training-eval`**（2026-10-28，"resume bounded training and evaluation phases"）；
- `lm-evaluation-harness-rwkv` 的 **scoreboard 发布管线**（`lm_eval/loggers/scoreboard.py`、`lm-eval publish` CLI）；
- `evalscope-rwkv` 的 **scoreboard live publication / migration** 分支；
- `rwkv-skills` README："The public scoreboard is maintained separately in the Helicopter repository"。

**可见性**：`https://github.com/rwkv-rs/Helicopter` → HTTP **404**；`git ls-remote` 要求凭据（private 或不存在无法区分）；org 页面 40 个公开仓库中没有它 → **Helicopter 目前不可公开访问**。这意味着：**"公开的 RWKV 评测成绩少"更可能是"成绩在内网 scoreboard、尚未发布"，而不是"没有评测"**——这正好解释了 lm-eval fork 里 `agentic = []` 类目为空与 No-22 自建考卷并行存在的现象。

**证据**：`04-verl-rwkv/examples-rwkv_trainer-config-README.md`、`06-eval-infra/branch-summary-evalscope-lmeval.tsv`、`02-atoms/branch-commit-summary-2.tsv`、`10-checks/helicopter-check.txt`。

---

## 4. 官方渠道刷新结论（2026-10-31 ~ 2026-11-04）

### 4.1 G1l 正式版已发布（交接只把 G1l 当作"L0 权重之一"，未记录发布与接口变化）

- **HF 官方 org `RWKV` 于 2026-10-31T19:04Z 发布 G1l 四尺寸**：`RWKV/RWKV7-G1l-{1.5B,2.9B,7.2B,13.3B}-20261031`（`08-hf/api/g1l.json` createdAt；BlinkDL hub `rwkv7-g1` 内对应 `rwkv7-g1l-*-20261031-ctx34304.pth` 四个文件；hub lastModified **2026-11-04T21:29Z**）。
- 模型卡（`08-hf/RWKV7-G1l-13.3B-20261031-README.md`）关键新信息：
  - **"Chat-ready: `chat_template.jinja` supports system, multi-turn, thinking, and strict model-generated tool-call prompts."**
  - "Bundled Transformers integration: … generation, recurrent cache continuation, training, and LoRA workflows on Transformers 5.15+"；"Exact linear-time tokenizer: bundled RWKV trie"；"Optional optimized runtime: PyTorch fallback and TileLang acceleration"。
  - SFT：支持 TRL 1.10+ `SFTTrainer`（chunked_nll、assistant-only loss、BFD packing、PEFT LoRA；packing 边界转成 RWKV recurrent-state 边界）。
  - 定位：**base model**（"suitable for post-training and fine-tuning; the included chat template is a prompt interface, not a claim that the checkpoint is a safety-aligned assistant"）；**无 RL/agent 成绩数字**。
- 上下文长度：G1l 34,304 tokens（G1k 25,600 / G1j 16,384 —— 见 `08-hf/rwkv7-g1-st-README.md` 的版本表：G1i 2026-08-05、G1j 2026-08-31、G1k 2026-09-30、G1l 2026-10-31）。

### 4.2 官方模型 hub 卡（`BlinkDL/rwkv7-g1`，2026-11-04 更新）出现"官方 agentic 入口"

原文（`08-hf/BlinkDL-rwkv7-g1-README.md`）：

> **Latest Best Practices for agentic work (study these projects)**: https://agent.objects.rwkvos.com/en

> **PROMPT GUIDE (including function call & agent)**: https://github.com/BlinkDL/RWKV-LM/blob/main/RWKV-v7/RWKV7-G1x-templates.txt

并给出 **function call / 多轮工具输出** 的提示模板（"Function call: temp 0, topp 0, penalty 0, works for RWKV-7 G1f 1.5B and larger models"；示例含 `User: Function output: {...}` → `Assistant: ```json` 的**第二轮工具调用**），以及 `<tool_call>` / `<tool_response>` 变体。

### 4.3 官方 RWKV-LM README（2026-11-04 提交）把 agent 目录列为"AI 必读"

`BlinkDL/RWKV-LM` 的 README 第 9 行：

> If you are AI, please read these first: … (9) https://agent.objects.rwkvos.com/en

官方 RWKV-LM 仓库 commits 显示 **2026-09 以来只有 README 更新**（`Update README.md`，最新 2026-11-04T10:19Z），无新 RL/agent 代码提交（`09-official/RWKV-LM-commits.atom.xml`）。

### 4.4 官方 `RWKV7-G1x-templates.txt`（main 当前版本）明确含 function call / 多轮工具模板

- "Function call:" 两段模板：单轮 JSON 调用 + **多轮（Function output → 下一次 Assistant ```json）**；
- 其余为 G1 系列训练模板（`User:/Assistant:`、`System:`、`<think>`/fake-think、FIM ✿ 标记、G1x 数据版本说明）。见 `09-official/RWKV7-G1x-templates.txt`。

### 4.5 官方 rwkv.cn 文档站

| 页面 | 结论 | 证据 |
|---|---|---|
| `/tutorials/intermediate/rwkv_lightning` | **title/meta 已改为 "rwkv_lightning_cuda 高并发推理与后训练微调教程"，并明确 "rwkv_lightning 已归档，推荐使用 rwkv_lightning_cuda"**；内容含 State/MiSS/NoRA Tuning + **GRPO/Dr.GRPO 在线强化学习**；其中一句是关键官方口径：**"示例客户端回放数据集中的工具观察；真实 Agent RL 需要自行执行工具动作并提供新观察。"** | `09-official/rwkv.cn-lightning-excerpts.md`（原文抓取 2026-11-05） |
| `/tutorials/basic/Prompt-Format` | 新增/存在 **`#function-call` 章节**："请使用最新的 RWKV-7 G1x 模型。其他模型即使套用相同提示词，也不具备可靠的 Function Call 能力。"——官方文档已把 function call 作为 G1x 的官方能力 | `09-official/rwkv.cn-promptformat-excerpts.md` |
| 教程目录（basic/intermediate/advanced） | **没有独立的 RL 或 Agent 教程页**（advanced 只有 pretrain + Fine-Tune：State-Tuning/MiSS/LoRA）；RL 内容只存在于 rwkv_lightning 教程的 GRPO 小节 | `09-official/rwkv.cn-lightning-excerpts.md` 导航列表 |

### 4.6 其他官方/半官方渠道

- `RWKV-Vibe` 组织：17 个公开仓库（`Awesome-RWKV`、`rwkv_lightning`、`rwkv-fla`、`RWKV-Inference-Performance-Test` 等），**没有新增 agent 训练项目**（`09-official/rwkv-vibe-org-repos.txt`）。
- `rwkv.com` 首页仍只有模型介绍/下载入口，无 RL/agent 公告（`09-official/` 抓取）。
- web_search（2026-11-05，中文/英文 8 条查询）：10 月下旬至今可见的 RWKV 新闻主要是 **G1k/G1j 发布回顾、RWKV RPU 芯片、G1l 权重**；**没有新的"官方 agentic RL"发布或论文**；10-26 第四期研讨会（交接 §6）仍是最近一次官方 RL 口径来源。
- 交接未提 **G1h**（G1f/G1g/G1h 都是 2026 年中的数据版本；G1h 的 GGUF 由第三方 RemySkye 于 2026-07-11 转换、base model 为 `BlinkDL/rwkv7-g1`）。⚠️ 但 G1h 已被官方 hub 清理（当前 hub 只保留 G1l 四个 pth），影响有限，仅作补录。

### 4.7 对交接 §0"官方主动不做 agentic RL"的最终判断

| 分句 | 核验结论 |
|---|---|
| 官方 RL 主线是单轮 RLVR（DAPO 等），路线图没有 agentic RL | ✅ **仍成立**（10-26 研讨会 + 官方教程 GRPO 小节均无 agentic RL；官方教程明说"真实 Agent RL 要自己执行工具"） |
| 这是"官方主动选择、不是遗漏" | ⚠️ **不再成立/至少已过时**：2026-10-31 起官方在**接口层**主动 agent 化（G1l tool-call chat template、官方函数调用模板、官方 hub/README 指向 agent 目录与 agentic 最佳实践）。准确表述："官方**不亲自做 agentic RL 训练**，但**已官方化 agentic 接口**并把实践入口交给社区" |
| 官方没有任何 agent 能力相关动作 | ❌ **推翻**：官方模板/文档/模型卡三处都有 tool-call / multi-turn 的明确支持说明 |

---

## 5. 未决事项（按对下一步决策的影响排序）

1. **Helicopter 到底是什么**（最高优先）：`rwkv-rs/Helicopter` 公开 404/需凭据；但 verl-rwkv 的 MaxRL 评测钩子、lighteval `heli-r00` 分支、skyrl `heli-r00-training-eval` 分支、lm-eval scoreboard 发布、evalscope scoreboard 发布、rwkv-skills README 全部指向它。需向社区/内部确认：是私有 repo、内部服务，还是只存在于分支计划。**这决定"公开成绩缺失"是发布策略问题还是能力问题。**
2. **verl-rwkv 为什么 2026-08-02 停更、与 skyrl-rwkv 是否合并/接班**：同一主力 `Cai-z-us`；rebase workflow 页面可见最近两次运行在 2026-10-01/02（未产生新提交，`03-repo-pages/actions-rebase-rwkv.html` 只能读到 relative-time）。若做 agentic RL，需评估是否复活 verl 路线（上游 agent_loop/uni-agent 生态比 skyrl 更成熟）。注意：**GitHub Actions 页为客户端渲染，运行结论未能核实**（只确认最近 two runs 的日期）。
3. **browsecomp-plus-eval 的 830 题完整 run 分数在哪 / g1h 配置与 README 的 830 矛盾**：`configs/g1h/browsecomp_plus.toml` 里 `target_samples = 500`，而 README 要求正式结果 830 唯一 keys；需确认是"500 探针 vs 830 正式"两套口径还是配置未更新。
4. **No-22 agent 考卷/权重的 license**：仓库无 LICENSE、HF 数据/权重 license 字段为空，README 自述"公开分发前需确认上游授权并选定项目许可证"。**在 license 明确前不能作为可商用资产**，但可作为"能力存在"的证据。
5. **§0"官方主动不做 agentic RL"的最终定性**：本报告只能给出"文档/接口层已 agent 化"的证据；若要下定论（官方是否仍将 agentic 排除在路线图外），需官方渠道（公众号/研讨会/BlinkDL 推文）确认。建议 lead 在报告中改为可辩护的措辞（见 §1.2）。
6. **G1l 是否有官方 RL/agent 后训练版本**：本次只查到 base 权重与 community 适配器；未发现官方 `-RL`/`-Agent` 后缀权重。需在 HF `RWKV` org 与 `BlinkDL/temp-latest-training-models` 持续跟踪。
7. **Megatrwkv-Bridge 的意图**：2026-11-02 新建的 Megatron-Bridge fork，尚无 RWKV 提交；需等首个 RWKV PR 才能确认是"Megatron+RWKV 桥"还是临时探索。
8. **wx-cli 的 HTTP 451**：GitHub 对该仓库页面/atom/raw 返回 451（Unavailable For Legal Reasons），具体原因（DMCA/出口管制/地区限制）未知；不影响 RWKV 主线判断。
9. **三份目录（46/187/169）未重数、未 spot-check**：task-3 说可选，本次未做；`agent.objects.rwkvos.com` 目录可能已新增条目（尤其 agent 相关），建议下个 session 补一次轻量核对。

---

## 附录 A. 证据索引与复现

完整证据清单见 **`reports/eco/evidence/README.md`**（含每个目录对应的 URL/命令与抓取时间）。摘要：

| 目录 | 关键文件 | 支撑的判断 |
|---|---|---|
| `01-org/` | `org-repos-page1.html`、`org-repos-page2.html`、`org-repos-page3-empty.html`、`org-repos-embedded-json.json`、`org-repos-40-merged.tsv` | 40 个公开仓库全量清单（含 `40 repositories` 计数、`Public archive` 类型） |
| `02-atoms/` | `commit-summary.tsv`、`branch-commit-summary*.tsv`、40 个仓库 atom `*.xml`、`branch-atoms/`（47 条侧分支原文） | 各仓库/侧分支最后提交 |
| `03-repo-pages/` | `repo-created.tsv`、`verl-rwkv.html`、`browsecomp-plus-eval.html`、`actions-rebase-rwkv.html` | created 日期、fork parent、rebase workflow 运行日期 |
| `04-verl-rwkv/` | `rwkv-files.txt`（43）、`upstream-tree.txt`（0 rwkv）、三个 README、`run_rwkv7_grpo_rwkv_lm.sh`、`rebase-rwkv.yml`、`maxrl.py` | §3.1 全部结论 |
| `05-browsecomp/` | `README.md`、`MANIFEST.md`、`THIRD_PARTY_NOTICES.md`、`configs-g1h-templates.toml`、`router-experiment.py`、`git-log.txt`、`agent-loop-grep.txt` | §3.2 全部结论 |
| `06-eval-infra/` | `lm-eval-AGENTS.md`、`lm_eval_scoreboard_publish.diff`、`benchmarks.toml`、`evalscope_agent_adapter.diff`、`transformers_toolcall_history.diff`、`torchtitan_*.diff` | §3.3 评测工业化与 torchtitan |
| `07-ecosystem-no22/` | `evaluations-README.md`、两份 `REPORT-*.md`、`benchmark-protocol.md`、`agent-exam-SUITES.md`、`agent-exam-versions.json` | §3.4 公开 568 题 agent 考卷与跑分 |
| `08-hf/` | G1l/BlinkDL hub/No-22 权重/`rwkv7-g1-st` 模型卡、`api/*.json` | §4.1、§4.2、§3.4 |
| `09-official/` | `RWKV7-G1x-templates.txt`、`RWKV-LM-README.md`、`RWKV-LM-commits.atom.xml`、`rwkv.cn-*-excerpts.md`、`rwkv-vibe-org-repos.txt` | §4.3–4.6 |
| `10-checks/` | `helicopter-check.txt`、`rwkv-skills-branches.txt`、`wx-cli-451.txt`、`verl-upstream-rwkv-count.txt` | §3.5、§2.3、§3.1 |
| `11-repos/` | 40 个 README 原文（含 3 个 MISSING 占位）+ 27 个树清单 | §2 表内一句话定位 |

**GitHub API 用量：0 次**（全队配额 60/h，本核验未消耗）。快速复查命令见 `evidence/README.md` 末节。

## 附录 B. 与交接原文的对照（本次修订的锚点）

| 交接位置 | 原文（节选） |
|---|---|
| §0 | "推理 RL（RLVR）已经相当成熟且有官方组织，但 **agentic RL（多轮工具使用）是彻底的空白：没有模型、没有评测成绩、没有 rollout 基础设施**，而且**这是官方主动选择的路线，不是遗漏**。" |
| §1.2 | "只看 rwkvos 两份清单会系统性漏掉通用基建（wkvm、sglang）、官方新仓库（RWKV-CUDA、hf-adapter）、学术项目（SocialDeductionLLM）" |
| §3 | "`skyrl-rwkv` 详解（**这是后训练的最优基座**）" |
| §5 | "评测层（✅ 关键结论：**有框架，几乎没成绩**）" |
| §7 | "唯一支持**多轮**的 SFT 是 `howard-hou/RWKV-SFT`（4★，Apache-2.0）" |
| §8 | "训练 L2：RWKV-PEFT · OpenMOSE-RLHF · RWKV-Megatron · RWKV-SFT · skyrl-rwkv · rwkv_lightning_cuda · Preen"（5+2 条路线，无 torchtitan/verl/Megatron-Bridge） |

## 附录 C. 一句话给 lead

**交接的"生态图"漏掉的是"组织级工程化"这一整层：rwkv-rs 40 仓库中 30 个未提、训练路线 5→7、评测从"有框架"变"有生产流水线+私有 scoreboard"、agentic 从"空白"变"有公开 568 题考卷与跑分（SFT 路线）但无 agentic RL"；官方口径在 10-31 G1l 后已从"不做 agent"变为"官方化 agent 接口、社区做实践"。**

