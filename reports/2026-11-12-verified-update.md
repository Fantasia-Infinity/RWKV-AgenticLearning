# 2026-11-12 生态核验更新：SFT 数据打分的 58.7，以及 eval harness 三条 open PR

> 核验时间：2026-11-12 14:00–14:40 CET。方式：GitHub API + raw 文件回源。
> 对应外部摘要：2026-11-12 两轮日检（13:45 前后）。

## 一、已核验事实

### 1. `rwkv-agent-eval` 的 `scores-20261111.md` / `loss-20261111.md`
两个文件实际位于 `docs/reports/`（不是仓库根），内容与日检数字一致：

- **基模是 `rwkv7-g1l-7.2b-20261031-ctx34304`（7.2B）**，旧 adapter 53.2，新 adapter `g1l-nora-r16-261111`
  （`mix-20261111`：Agent 1714 条 + 日常 2911 行）**58.7（+5.5 ±2.5 over 旧；+27.8 ±3.1 over 基模）**；
  12 个能力块 11 涨，terminal −3.3（误差内）。
- 涨点：edit-data +16.7±10.7、stat +11.3±10.1、web-local +7.0、search +6.1；web-code/read-code/code-fix 基本未动。
- **补测（rc.1 + 日期行）**：新 adapter 57.3，对比 58.7 为 **−1.5 ±2.1（区间跨 0）** → 换到"训练时环境"没有多拿分。
- 评测协议：1019 题 × 每题 2 次（合并补测后每题 4 次），超时算 0；本次两组均无超时/环境错误。
- **该仓库无 LICENSE**（GitHub API `license: null`）→ 数据/代码不可复用，只能引用数字。

### 2. `loss-20261111.md` 的失分拆解（比日检更细）
- 失败 428 题（新模型）；失败原因：**重复调用被强制收尾 23.8% + 用满 12 步 12.2% + 输出截断/格式坏 11.8%
  ≈ 47.8% 是"打转或失控"**；真正做完答错约 30%。
- **编辑工具错误率 27.7%**（`原文找不到` 506 次、新旧内容相同 132、原文不唯一 8）；19.6% 的失败轨迹里至少一次编辑报错。
- 打转集中的三块（web-code / code-fix / terminal）占全部失分 42%；terminal 是唯一退步块（训练集无此类题）。
- **hashline 零样本不会用**：基模 18.3 → 1.9 分，仅 3% 的编辑调用写了新参数（插件分支 `hashline-edit`）。
- **改提示词无效**：416 道编辑题上改工具描述/加系统规则，编辑失败率仍 27.5–28.5%（基线 28.1%）。
- **容错匹配离线重放**：1094 次可靠还原的"原文找不到"里，Aider 式整段缩进对齐能救回 148 次（13.5%）；
  其余约 72% 是内容本身抄错，只能换编辑方式或训练解决。

### 3. 配套基础设施（均已合并）
| PR | 仓库 | 合并时间 | 内容 |
|---|---|---|---|
| #16 | `rwkv-org/irwkv` | 2026-11-11T15:14:21Z | **Serve versioned LoRA/NoRA adapters**：运行时 load/unload、按模型名切换、batch 内同版本聚合、版本化 prefix-cache 身份（+1650/−63，52 文件） |
| #2 | `rwkv-rs/Megatrwkv-Bridge` | 2026-11-12T02:57:24Z | **export native LoRA/NoRA adapters**：RWKV7 Bridge 导出 PEFT 兼容 A/B 张量、NoRA 合并归一化（+322/−11，8 文件） |
| #24 | `Alic-Li/rwkv_lightning_cuda` | 2026-11-11T13:55:24Z | 修复 prefill 准入在 hard limit 以下永久挂起；benchmark 独立文档 + RTX 4060 Ti 参考成绩（+607/−37） |

### 4. `rwkv-agent-eval` 的 3 条 open PR（w1c2j3，2026-11-12T10:08:34–41Z 创建）
- **#1** `runner: report and diagnose runs from either harness (DSH or Pi)`：report/diagnose 读两套 harness；
  新增 `engine_error / max_tokens / aborted / loop_guard / truncated_call / unclosed_think / unknown_tool / context_overflow` 标签
- **#2** `backends/pi: Pi + rwkv-pi Harbor agent (PiRwkv)`：第二套 harness，转 Pi session log 为 DSH `events.jsonl` 格式
- **#3** `DSH: engine credential and container URL; BACKEND=dsh|pi`：`scripts/backend.sh` 提供 `BACKEND=dsh|pi`；
  **依赖 dsh-rwkv-plugin 的本地分支 `headless-api-key-env`（尚未提交 PR）**
- 三条均未合并；仓库无 LICENSE。

### 5. 其他
- `experiments/edit-prompt/` 存在：`hashline.json` 内容为 `{"editTool":"hashline"}`，含 `run-hashline.sh` 等 7 个文件 ✅
- `123213213weqw` 在 llama.cpp 的 3 个已合并 RWKV7 CUDA PR：**未回源**（GitHub search API 触发限流），标记待核验

## 二、对日检摘要的修正

| 日检说法 | 修正 |
|---|---|
| "58.7，突破 53" | ✅ 数字正确；但这是 **7.2B 基模 + NoRA r16 + SFT 数据**，不是 1.5B，也不是 RL；日检自己也在判定里承认"SFT 而非 RL" |
| "涨幅 +5.5 ±2.5，区间不跨 0" | ✅ 正确（配对 95% CI） |
| "+16.7 edit-data / +11.3 stat 是归因→数据闭环的证据" | ⚠️ 方向对，但这两项 CI 很宽（±10.7 / ±10.1），11/12 块上涨是更可靠的证据；"闭环"目前是单轮、单 seed |
| "48% 失败是打转/失控" | ✅ 23.8+12.2+11.8≈47.8% |
| "20% 失败轨迹里有编辑报错" | ✅ 19.6% |
| "hashline 是对 20% 编辑失败的直接手术" | ❌ **目前证据是负面的**：零样本 hashline 18.3→1.9、仅 3% 调用使用新参数；改提示词也无效；只能靠数据/训练或换编辑接口，且缩进对齐只能救回 13.5% |
| "SFT 还有空间，RL 时机要等" | ⚠️ 只对 agentic/7.2B 场景成立；我们 1.5B GSM8K 上 SFT 已接近饱和、RL（DAPO/SAO）仍能 +10~11pp —— 两者不矛盾，取决于任务与规模 |
| "SHA 只变 1 个，变化在 PR 上" | ✅ 方法论正确；`git ls-remote` 看不到 open PR，需要补 PR 列表检查（我们已更新 tracking 约定） |

## 三、对我们项目的影响

1. **失败分类高度一致**：他们的"重复调用/用满步数/截断"正是我们 P3 多轮工具 RL 里观察到的打转与格式退化；
   说明答案级奖励不足以修复行为层，需要**硬约束（grammar/重复门）+ 接口设计（hashline 类）**配合训练数据。
2. **hashline 的零样本失败**给我们一个警示：新工具接口必须配训练轨迹（同我们在 PR #20 模板迁移上的教训），
   不能指望"改接口就自动变好"。
3. **版本化 adapter 服务 + Megatron 原生 adapter 导出**补齐了多 adapter 评测/异步 RL 的工程基础；
   我们的 skyrl+vLLM 栈仍 pin FlashRWKV2 a17，升级 a19 前需做 parity（已列入 P4）。
4. **评测仓库无 LICENSE、部分功能依赖未提交分支** → 公开交付继续只引用数字，不复制其代码/数据。

## 四、引用

- scores: https://github.com/rwkv-org/rwkv-agent-eval/blob/main/docs/reports/scores-20261111.md
- loss: https://github.com/rwkv-org/rwkv-agent-eval/blob/main/docs/reports/loss-20261111.md
- eval PRs: https://github.com/rwkv-org/rwkv-agent-eval/pulls （#1/#2/#3, open）
- irwkv #16: https://github.com/rwkv-org/irwkv/pull/16 （merged 2026-11-11T15:14:21Z）
- Megatrwkv-Bridge #2: https://github.com/rwkv-rs/Megatrwkv-Bridge/pull/2 （merged 2026-11-12T02:57:24Z）
- rwkv_lightning_cuda #24: https://github.com/Alic-Li/rwkv_lightning_cuda/pull/24 （merged 2026-11-11T13:55:24Z）
- hashline 实验文件: https://github.com/rwkv-org/rwkv-agent-eval/tree/main/experiments/edit-prompt
