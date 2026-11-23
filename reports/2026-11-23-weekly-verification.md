# 2026-11-23 周检核验：8 项信号全未新增触发，但 6 条新变化在清单之外

> 核验时间：2026-11-23 16:30–17:20 CET。GitHub API / raw / atom / HuggingFace API 回源。
> 对应外部摘要：2026-11-23 周检。

## 一、8 项信号逐条核验

| # | 信号 | 核验结果 |
|---|---|---|
| 1 | 标准 agent benchmark 有分数 | ✅ **部分**：Terminal-Bench 2.0 公开 **0/8**（No-22，有效 8/10）；τ-bench / BFCL / AgentBench / SWE-bench 我们未见到公开分数 |
| 2 | `skyrl-rwkv` 多轮工具环境 | ✅ **未触发**：官方 run.sh 里 `env_class` 实测只有 **gsm8k / ultradata / aime**（全单轮）；仓库树中 **TLPO 0 命中** |
| 3 | 28B 文档化训练 | ❌ 未触发（本周无新证据） |
| 4 | `wkvm` 补 LICENSE | ✅ **未触发**：`xiaol/wkvm` ★359，**无 LICENSE**，最后 push **2026-09-10** |
| 5 | 多轮轨迹 SFT 进官方 PEFT | ✅ **未触发**：`Joluck/RWKV-PEFT`（现重定向 `JL-er/RWKV-PEFT`）★187，最后 push **2026-10-22** |
| 6 | G1 进 OpenMOSE | ✅ **未触发**：HF `OpenMOSE` **58 个模型**，**无 G1**（最新含 RWKV7-MTP-Exp / x070-2B9-CJE） |
| 7 | TLPO 进 `skyrl-rwkv` | ✅ **未触发**（0 命中） |
| 8 | G1 之后的新架构代际 | ✅ **未触发**：`BlinkDL/RWKV-LM` 近 20 次提交全是 "Update README.md"（最后 2026-11-04） |

## 二、清单之外的新变化（已逐条核验）

### 1. `rwkv_lightning_cuda` PR #27（2026-11-23T03:18:13Z 合并）
- 标题：`feat(training): packed BF16/NoRA optimizations, multi-turn end_target, elastic NCCL DP, and DP tune servers`
- body 原文确认：
  - **多轮 segment `end_target: 0`**：支持 `labels` 与 `tokens` 分离，在非空 `train: true` segment 上把 EOS(`0`) 作为 label，
    **不插 `<EOD>` 进前向 token 流、不污染 RWKV 递归 state**；同时严格拒绝超长行（不再静默截断）
  - **弹性/多机 NCCL DP**、NCCL DP 在线 RL tune servers
  - packed BF16/NoRA 吞吐与显存优化（监督行压紧、layer-0 输入伴随量可选裁剪、virtual-stream `doc_start` 打包、自适应 VRAM window）
- #26（packed BF16 旧版）**closed 未合并**，被 #27 取代

### 2. 顾真牛 "深度循环 post-hoc No-Go"（2026-11-20/21，`cgisky1980/rwkv-rsv`）
- commit：`feat(eval): add post-hoc recurrent-depth experiment harness and report`（2026-11-20）
- 文档：`参考/2026-11-21-RWKV深度循环post-hoc实验-实施记录.md` + `examples/recurrent_depth_eval.rs`
- 关键数字（CPU fp32，0.4B，768 个评分位置）：
  - baseline PPL **42.07**；最优臂 **S2_L2 PPL 47.98（+14.0%）**；S1_L2 +78.2%、S3_L2 +110.0%、S2_L4 +100.9% → **post-hoc 全面变差**
  - **state 字节数所有臂恒为 6,488,064 B，与 L 完全无关**（24 层 × (2C + H·N²) × 4；临时快照 3.24MB 每轮复用不累积）
  - 吞吐：L=1→2→4 的 ms/tok 42→49→63（×1.17 / ×1.50）
- 结论原文：**post-hoc 方案 No-Go，关闭该分支**；训练版（随机 L 采样）仍待验证；S2 first-commit 应提为默认消融位

### 3. 本周其余变化（此前已核验）
- 11-19 官方「RWKV Agent 专场」公告（11-26 19:30，三位算法专家）✅
- 11-20 Terminal-Bench **0/8**、Search-R1 **0.407**（目标 0.45 未达）✅
- 11-18 `any2rwkv` 首个外部 PR（EntropyPhoton，GQA priming）✅
- 11-18 Cai-z-us 19 PR 合入（四仓 open 归零；FlashRWKV2 0.2.0a1 上 PyPI）✅

## 三、对周检判断的评估

| 周检判断 | 评估 |
|---|---|
| "8 项信号一项未触发" | ✅ 属实（逐条核验） |
| "多轮训练缺 label 侧方案 → 推翻（end_target 已实现）" | ✅ 属实；但注意 **advantage 侧**：官方 `skyrl-rwkv` 的 rwkv 配方仍无工具 env，advantage/多轮工具训练链仍是外部自建（我们的 P3 即自建），所以"两侧补齐"目前只对 **label 侧（lightning）** 成立 |
| "没有 agentic 基准数字 → 部分推翻" | ✅ Terminal-Bench 0/8 + Search-R1 0.407；**但 τ-bench/BFCL/SWE-bench 仍无**，绝对覆盖仍空白 |
| "看 skyrl-rwkv 就知道官方 RL 进度 → 失效" | ✅ 同意：落点至少在 skyrl-rwkv（算法）、lightning_cuda（引擎/标签/在线 RL）、lightning_grpo（state-only）、RL-Search-R1（agentic RL）、helicopter（评测框架）五处 |
| "信号清单应改为对照六条独立线" | ✅ 建议采纳；我们已经把跟踪基线扩到 88 条仓库，但"信号"维度仍默认从 skyrl 出发，需要显式拆线 |

## 四、更新后的"七条独立线"（建议写进 tracking）

1. **算法/框架线**：`skyrl-rwkv`（GRPO/DAPO/SAO/OPD/Anti-Doom；**无多轮工具 env / 无 TLPO**）
2. **引擎/在线 RL 线**：`rwkv_lightning_cuda`（推理 perf、**多轮 end_target: 0**、elastic NCCL DP、在线 RL servers）
3. **state-only RL 线**：`rwkv_lightning_grpo`（只更新初始 WKV state）
4. **agentic RL 线**：`RWKV-RL-Search-R1`（唯一公开 agentic RL 分数 0.407）
5. **评测/榜单线**：`rwkv-skills` + `rwkv-harbor-scratch`（Terminal-Bench 0/8）+ `browsecomp-plus-eval` + 三框架 fork
6. **数据/训练基础设施线**：`RWKV-AUTODECO`、`originium/rhine`、`MediaCrawler`、`Infinite_Lake`
7. **推理/部署线**：`rwkv-rsv`（MIT，含深度循环实验）、`Albatross`、`irwkv`/`vllm-rwkv`、`rwkv_lightning_xdna`

## 五、对我们的影响

1. **我们的公开结论需要保持 scope**：README 已写"public agent data is mostly SFT"，但需补充两个例外
   （Terminal-Bench 0/8、Search-R1 0.407），并明确"标准 agent benchmark 的绝对覆盖仍缺"。
2. **end_target: 0 是"标签侧"的补齐**，解决的是"多轮训练时 EOS/state 污染"；它不等于多轮工具 RL 的 advantage 方案，
   我们 P3 的负结果（answer-only 奖励导致 tool-call shortcut）仍然成立，仍是公开多轮工具 RL 的唯一证据。
3. **深度循环 No-Go** 与我们的"下一阶段不盲目加架构"判断一致；其 state 字节与 L 无关的结构性结论值得记入知识库。
4. **11-26 直播**（3 天后）是决定性信息源：重点听 chase 的"弯路"和 No.22 的 DSH 闭环细节。

## 六、引用

- lightning #27: https://github.com/Alic-Li/rwkv_lightning_cuda/pull/27
- 深度循环报告（raw）: https://github.com/cgisky1980/rwkv-rsv/blob/master/参考/2026-11-21-RWKV深度循环post-hoc实验-实施记录.md
- rwkv-rsv: https://github.com/cgisky1980/rwkv-rsv
- skyrl-rwkv run.sh: https://github.com/rwkv-rs/skyrl-rwkv/blob/main/examples/train/rwkv/train/
- wkvm: https://github.com/xiaol/wkvm
- RWKV-PEFT: https://github.com/Joluck/RWKV-PEFT
- OpenMOSE: https://huggingface.co/OpenMOSE
