# 2026-11-20 漏库审计核验：评测/RL/推理/数据四层补课

> 核验时间：2026-11-20 18:15–19:00 CET。GitHub API / raw README 回源。
> 对应外部摘要：2026-11-20 "我们漏掉的库：统一补课"。

## 一、元数据核验（stars / 日期 / 许可）

| 仓库 | 外部摘要 | 实测 | 许可 |
|---|---|---|---|
| `No-22-Github/rwkv-harbor-scratch` | ★0，10-28 | ★0，created 2026-10-28，desc "Running RWKV on Harbor / Terminal-Bench 2.0" | **无 LICENSE** |
| `No-22-Github/RWKV-RL-Search-R1` | ★0，11-01 | ★0，created 2026-10-29，pushed 11-01，desc "RWKV-7 2.9B 在 Search-R1 上的 SFT + GRPO" | **无 LICENSE** |
| `Alic-Li/rwkv_lightning_grpo` | ★0，10-12 | ★0，created 2026-10-12，pushed 10-12 | **Apache-2.0** |
| `Alic-Li/rwkv_lightning_xdna` | ★0，10-04 | ★0，created 10-02，pushed 10-04 | **Apache-2.0** |
| `Alic-Li/Mini_RWKV_7` | ★95 | ★95，34.2M 参数 | **Apache-2.0** |
| `Alic-Li/rwkv-mobile` / `rwkvcn-docs` / `RWKV_Qbot` | ★0 | ★0 / ★0 / ★0 | 无 LICENSE |
| `rwkv-rs/rwkv-skills` | ★8，08-09 | ★8，pushed 2026-08-09 | **无 LICENSE** |
| `rwkv-rs/browsecomp-plus-eval` | ★1，07-21 | ★1，pushed 2026-07-21 | **无 LICENSE** |
| `rwkv-rs/RWKV-AUTODECO` | ★0，01-27 | ★0，pushed 2026-01-27 | **Apache-2.0** |
| `rwkv-rs/originium` / `rhine` / `rhine-schema-derive` | ★7 / ★0 / ★0 | 一致（originium pushed 2025-09-05；license：无 / GPL-3.0 / MIT） | — |
| `TimeMobius/QueQiao-Router` / `Infinite_Lake` | ★57 / ★52 | ★57 Apache-2.0 / ★52 无 LICENSE | — |
| `Beortext/RWKV-DeepEmbed-mmap` | ★3 | ★3，pushed 2025-09-02 | **Apache-2.0** |
| `No-22-Github/Preen` | ★6 | ★6，pushed 2026-10-09 | Apache-2.0 |
| `No-22-Github/RWKV-Agent` / `RWKV_Agent_Lite` | ★4 / ★1 | ★4 / ★1 | 无 LICENSE |
| `rwkv-rs/Albatross` | ★0 | ★0，pushed 2025-10-09 | Apache-2.0 |
| `Big-dreamer-creator/helicopter` | （摘要未单列） | ★0，created 2026-07-09，pushed 2026-08-10 | **无 LICENSE** |
| `Big-dreamer-creator/lm-evaluation-harness-rwkv` | （摘要称含 16 个 EvalScope coding 迁移） | ★0，created 2026-08-09；README 为上游 lm-eval 原版 | — |
| `123213213weqw` 账号 |

## 二、内容核验（README/结果原文）

### 1. `rwkv-harbor-scratch`：Terminal-Bench 2.0 唯一公开跑分（数字属实）
`docs/results/README.md` 原文（被测 `rwkv7-g1k-7.2b-20260930-ctx25600` + rwkv_lightning_cuda on W7900，
agent `RwkvTerminus` = terminus-2 + 续写后端，Docker x86 模拟 on Apple Silicon，2026-10-28）：

| 题集 | 得分 |
|---|---|
| hello-world | **1/1** |
| Terminal-Bench 2.0 简单题 | **0/4** |
| terminal-bench-sample@2.0 | **0/8**（有效 8/10；剔除判分环境损坏的 qemu-alpine-ssh、qemu-startup） |

失败分析（原文）：自发 `<think>` 复读写满输出上限；失败命令照抄/打转（fix-git 同一命令执行 52 次）；
偏离目标/违反约束；简单题上下文仅 10k–24k → **问题在多步决策，不在接入**；调采样参数无效。
→ 这是目前**唯一公开的 RWKV agent 绝对跑分**，且是 0 分区间；7.2B + W7900 的配置也不能直接与我们的 1.5B/bf16 对比。

### 2. `rwkv-skills`：六域评测脚手架（属实）
README 原文：目标外部 vLLM-RWKV OpenAI 接口；`src/eval/tasks/` 含
**knowledge / maths / coding / instruction_following / function_calling / agent_bench** 六域；
GPU scheduler + PostgreSQL；**"公开榜在 Helicopter 仓库单独维护"** ✅

### 3. `RWKV-RL-Search-R1`：唯一公开 agentic RL 数字（属实）
README 表格：GRPO ≈0.40、Dr.GRPO 0.40、**RAFT 第一轮 0.407**（target 0.45 未达）；
另有 Search-R1 7B Base PPO 0.431 的参考行。训练管线：SFT warm start → GRPO → RAFT/DAPO 取舍。
→ 与我们的结论一致：**RL 有实现，但公开可比的 agentic RL 数字极少**。

### 4. `rwkv_lightning_grpo`：state-only 在线 GRPO（属实）
README：Online State-only GRPO；`Rollout → 远程 Qwen Judge → GRPO/Dr.GRPO → BPTT → 只更新 FP32 Initial WKV State`；
冻结的 BF16 backbone/embedding/head **不拷贝、不保存**（全参数梯度图不跨 24 层）。**Apache-2.0**。

### 5. `RWKV-AUTODECO`：15 分钟起训（属实）
README："start pre-training a fully aligned RWKV v7 model within 15 minutes"（191M–3B），
实际是 **RWKV-LM-V7 fork**（Lightning 框架）。**Apache-2.0**。

### 6. `rwkv_lightning_xdna` / `QueQiao-Router`（属实）
- xdna：C++17 → XRT → amdxdna → NPU 的 Ryzen AI NPU 后端（Apache-2.0）
- QueQiao-Router：Rust/Axum/Tokio，统一 OpenAI/Azure/Anthropic/DeepSeek/vLLM/Llama.cpp 后端、权重路由/故障转移、
  思考格式归一化、Prometheus、按月审计（Apache-2.0，★57）

### 7. `helicopter`：**社区 fork 现在公开存在**（对旧审计的修正）
- `Big-dreamer-creator/helicopter`（★0，created 2026-07-09，pushed 2026-08-10，**无 LICENSE**）
- 内容是 Helicopter 框架（`infer` vLLM / `takeoff` verl GRPO / `install` / CLI），
  `reports/` 只有 `rwkv-vllm-verl-performance-handoff.md`，**没有公开榜单分数**
- 旧结论"Helicopter 公开不存在"应修正为：**框架 fork 公开存在，但 scoreboard 数据未发布**；
  `rwkv-skills` README 也印证该设计意图。

## 三、需要修正/未核实的外部说法

| 外部说法 | 核验结果 |
|---|---|
| "这些库从未追踪" | ⚠️ 部分错误：我们已追踪 `rwkv-skills`、`browsecomp-plus-eval`、`RWKV-AUTODECO`、`lm-evaluation-harness-rwkv`（rwkv-rs 版）等；确实漏的是 No-22/Alic-Li/TimeMobius/Big-dreamer 的个人仓库 |
| "lm-evaluation-harness-rwkv 里 w1c2j3 移植 16 个 EvalScope coding benchmark（含 SWE-bench Lite/Verified）" | ⚠️ **未核实**：`Big-dreamer-creator` 的 fork 树中未见 `swebench`/`livecodebench`/`bigcodebench`/`bird` 任务目录；可能在其他分支/未合并提交 |
| "llm-compressor-rwkv 有 8000 行 NVFP4 + 保护清单（w0/x_*/k_k/v_first 不可量化），因缺 Blackwell 停更 3.5 个月" | ⚠️ **部分**：仓库是 llm-compressor fork（Apache-2.0，pushed 2026-08-02，≈3.6 个月未更新），树中有 nvfp4 文档/示例，但未见 RWKV 专属保护清单；需看分支/PR 才能核实 |
| "RL 共 7 处实现，只有 1 处有分数" | ⚠️ 口径问题：`llm-compressor-rwkv` 是**量化压缩**不是 RL；准确说是 6 处 RL 实现（skyrl-rwkv、lightning_cuda 在线 RL、lightning_grpo、verl-rwkv、antidoom-rwkv、RL-Search-R1）+ 1 处量化。另：**我们自己的 DAPO/SAO 也是公开 RL 数字**（数学，非 agentic） |
| "123213213weqw 的 Venturi / rwkv-agent ★9" | ⚠️ **无法核实**：该账号 2026-11-20 起公开 GitHub 404（此前 XHarness 同样 404）；相关仓库可能转私有/删号 |
| "36 个跟踪 → 加 4 个到 40" | 这是外部文档口径；我们的 `tracking/repos.txt` 已有 70 条（39 个 rwkv-rs org 仓 + 外部仓），新增后约 85 条，仍在可维护范围 |

## 四、建议加入我们基线的清单

| 优先级 | 仓库 | 理由 |
|---|---|---|
| **P1** | `No-22-Github/rwkv-harbor-scratch` | 唯一公开 Terminal-Bench 绝对跑分（0 分区间），是"agent 能力差距"的硬证据 |
| **P1** | `No-22-Github/RWKV-RL-Search-R1` | 唯一公开 agentic RL 数字（0.407），可作我们 RL 对照 |
| **P1** | `Big-dreamer-creator/helicopter` | Helicopter 框架公开（无榜单数据），验证"榜单曾计划"的判断 |
| P2 | `Alic-Li/rwkv_lightning_grpo` | state-only GRPO，成本极低的 RL 路线参考 |
| P2 | `Alic-Li/rwkv_lightning_xdna` | NPU 后端（端侧推理） |
| P2 | `TimeMobius/QueQiao-Router` | 生产部署/路由层（★57，Apache-2.0） |
| P3 | `Alic-Li/Mini_RWKV_7`（★95）、`No-22-Github/Preen`、`Beortext/RWKV-DeepEmbed-mmap`、`No-22-Github/RWKV-Agent(_Lite)`、`rwkv-tokenizer-go`、`TimeMobius/Infinite_Lake` | 社区/领域/数据侧参考 |

**许可注意**：harbor-scratch / RL-Search-R1 / rwkv-skills / helicopter / rwkv-cc / Infinite_Lake / 123213213weqw 系
均**无 LICENSE**（只能引用，不可复用）；`rwkv_lightning_grpo`、`xdna`、`Mini_RWKV_7`、`DeepEmbed`、`QueQiao`、
`AUTODECO`、`Albatross` 为 Apache-2.0（可参考复用，仍需遵守署名）。

## 五、引用

- harbor-scratch: https://github.com/No-22-Github/rwkv-harbor-scratch （results: docs/results/README.md）
- rwkv-skills: https://github.com/rwkv-rs/rwkv-skills
- RWKV-RL-Search-R1: https://github.com/No-22-Github/RWKV-RL-Search-R1
- rwkv_lightning_grpo / xdna: https://github.com/Alic-Li/rwkv_lightning_grpo / `rwkv_lightning_xdna`
- RWKV-AUTODECO: https://github.com/rwkv-rs/RWKV-AUTODECO
- helicopter fork: https://github.com/Big-dreamer-creator/helicopter
- QueQiao-Router: https://github.com/TimeMobius/QueQiao-Router
- Mini_RWKV_7: https://github.com/Alic-Li/Mini_RWKV_7
