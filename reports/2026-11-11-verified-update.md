# 2026-11-11 生态核验更新（irwkv 两块能力 + FlashRWKV2 a19）

> 核验时间：2026-11-11 09:30–09:50 CET。方式：GitHub API 逐 PR / release 核对。
> 对应外部摘要：2026-11-11 日检。以下只记录本站回源确认的事实，并对措辞问题单列修正。

## 一、已核验事实

### 1. `rwkv-org/irwkv` PR #7 + PR #4 —— 同日合并（Cai-z-us）
| PR | 标题（原文） | 作者 | merged_at | 规模 |
|---|---|---|---|---|
| **#7** | **`[Perf][RWKV] Keep Rapid-Sampling CUDA graphs for structured output`** | w1c2j3 | **2026-11-10T23:58:41Z** | 4 commits，+144/−38，4 文件 |
| **#4** | **`[Feature][RWKV] Retain committed state for multi-turn continuation`** | w1c2j3 | **2026-11-10T23:58:41Z** | 4 commits，+222/−0，3 文件 |

**#7 实际内容（重要修正）**：这不是"新增语法约束解码能力"，而是**性能修复**——
RWKV 的 Rapid-Sampling CUDA graph 此前只要 batch 里出现一个 grammar 请求，整个 batch 就回退 eager；
该 PR 把图拆成 logits/sampling 两段共享内存池，在两个 replay 之间施加 grammar bitmask，
使结构化输出步骤继续走 graphed sampler。验证：7.2B、24/24 JSON-schema 输出合法、
58 个 grammar 步骤全部走图（greedy；含 17 个混合 partial prefill），输出与旧 head 逐字节一致；
普通 decode TPOT 变化 <0.2%。说明 **irwkv 此前已具备 grammar/structured output**（xgrammar/guidance）。

**#4 实际内容**：多轮续接的**已提交状态保留**（`RwkvStateManager`，RWKV-only）——
prefix caching 下，一轮结束/中断后保留最新 block 对齐 checkpoint，下一轮若客户端重发**完全相同的 token 历史**，
只重算未对齐尾部与最后采样 token。验证：7.2B、FP32/FP16 state、96 tokens 复用、
token-ID 与 logprob 与全量 prefill 完全一致。
**边界**：需要精确 token 前缀；chat 重新渲染历史会提前分叉（PR #8 另行处理 chat prompt boundary）。

### 2. `rwkv-rs/FlashRWKV2` v0.1.0a19 —— 训练正确性修复（比"补边角"更重要）
- 发布者 Cai-z-us；**published 2026-11-11T07:12:37Z**；tag `v0.1.0a19`；PyPI + wheels（sha256 已记录在 release）
- Release body 明确：**修复训练 RWKV7-G1k-1.5B 时观察到的两个失败**：
  1. **grouped weight-gradient pipeline epilogue 缺 CTA barrier** → **29-token 样本 padding 到 32 时出现 NaN**
  2. TokenShift / CMix 激活核的 dynamic row/tile counts 移到 CUDA `grid.x` → 支持 **66,880-token GSM8K 批次**（不撞 `grid.y` 上限）
- 两者保持既有 BF16 rounding / FP32 accumulation 顺序；验证含 RTX PRO 6000 + 4090、11 项回归、Compute Sanitizer 0 errors
- 来源 commit `449c170`；PR #25；PyPI `FlashRWKV2==0.1.0a19`

### 3. `Alic-Li/rwkv_lightning_cuda` —— 确为整理期
- 11-10 两个提交：`update benchmark`、`Update benchmark README & tidy test code`；11-09 PR #23 merge 后无功能变更 ✅

### 4. 其他（未回源/与主线无关）
- `x-harness-rs` 插件收敛、`NextTransformer` README/scaling 可视化整理：未回源核验（非 agent/RWKV 主线）
- `irwkv@mtp` 仍未并入 main；`any2rwkv` 仍 0 字节；`rwkv-agent-pipeline`、`w1c2j3/rwkv-pi` 仍私有（与 11-10 一致）

## 二、对日检摘要的修正

| 日检说法 | 修正 |
|---|---|
| "irwkv 拿到语法约束解码能力" | ⚠️ 语法约束（structured output）**此前已有**；#7 是把它从 eager 回退变成 graphed 采样（性能/吞吐修复），不是从无到有 |
| "Cai-z-us 于 11-10 23:56 合并" | ✅ 实质正确；精确时间为 **23:58:41Z**（两 PR 同一时刻） |
| "状态续接 = 多轮不需要重新 prefill" | ⚠️ 需限定：**只有精确 token 前缀**才能复用；chat 模板重新渲染的 follow-up 会在更早处分叉（PR #8 范畴），不是任意多轮对话都免 prefill |
| "FlashRWKV2 补大批量与动态 grid 的边角" | ✅ 但低估了：a19 另一个修复是 **29→32 padding 的 NaN bug**，属训练正确性问题，不是边角 |
| "只差真跑一轮并公布数字" | ❌ 已过时：**我们 2026-11-10 已公开 DAPO 单轮 RLVR 数字**（G1l-1.5B，GSM8K avg@4 21.0%→31.0%，p=6.6e-05，`reports/2026-11-10-dapo-gsm8k-rlvr.md`）。仍空的是**多轮 agentic RL 的正向结果** |

## 三、对我们项目的直接影响

1. **FlashRWKV2 a19 值得升级评估**：我们的 skyrl-rwkv / vLLM-RWKV 栈 pin 的是 **a17**；
   a17 可能带有 29→32 padding NaN 问题。我们 B1（DAPO 1000 步）未观察到 NaN，但未来换 batch/padding 长度
   或扩到 2.9B/7.2B 前，**建议升级 a18/a19 并重跑数值对齐/parity 测试**。
2. **irwkv 两 PR 是 serving 侧能力**：我们 RL 训练走 skyrl + vLLM-RWKV（不走 irwkv）；
   但 P4 若做异步评测/多轮 agent 部署：
   - grammar 硬约束可消除 fenced-JSON 软约束失败（我们 P3/P1.5 的格式失败是真实痛点）
   - state continuation 可降低多轮 rollout 的 prefill 成本（异步 RL 采样端）
3. **结论修订**：官方/社区流水线在 serving 侧继续补齐，但"公开 RL 数字"这一格**已由我们部分填上**（单轮数学）；
   多轮工具 RL 仍是公开空白，且我们的 P3 显示它是负结果——这反而是更有价值的公开信息。

## 四、引用

- irwkv #7: https://github.com/rwkv-org/irwkv/pull/7 （merged 2026-11-10T23:58:41Z，merge af080f41）
- irwkv #4: https://github.com/rwkv-org/irwkv/pull/4 （merged 2026-11-10T23:58:41Z，merge 69a36c83）
- FlashRWKV2 v0.1.0a19: https://github.com/rwkv-rs/FlashRWKV2/releases/tag/v0.1.0a19 （2026-11-11T07:12:37Z）
- rwkv_lightning_cuda commits: https://github.com/Alic-Li/rwkv_lightning_cuda/commits/main
- 我们的 DAPO 结果: reports/2026-11-10-dapo-gsm8k-rlvr.md（commit 3d01569）
