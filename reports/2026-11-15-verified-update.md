# 2026-11-15 生态核验更新：量化重构、torchtitan 退役与 39 仓清单

> 核验时间：2026-11-15 15:00–15:40 CET。方式：GitHub org API、commit patch、git ls-remote、
> raw 文件。对应外部摘要：2026-11-15 14:20 日检。

## 一、已核验事实

### 1. `Alic-Li/rwkv_lightning_cuda` 量化重构（提交 `323de53`）
- 提交标题：**`refactor(quant): 收敛量化方案至 W8A16 与 SB6 W4/W6`**，时间 **2026-11-14T08:37:29Z**，
  94 个文件变更
- 提交信息（原文要点）：
  - 保留原始 **W8A16**，集成 **SB6 W4/W6** 位平面 CUDA 内核 + AW 校准导出
  - **移除**旧对称 W4、SB6 W5、**Autopick**、**GPTQ**，明确拒绝退役格式
  - 同步归档读写/运行时/构建目标/Launcher UI+API；新增统一性能+精度评测工具，含 **7.2B 相对 FP16 实测**
  - **SB6 = SuperBlock**：每超块 256 个权重分 8 组，每组 scale/offset 各 6 bit，叠加共享 FP16 基准还原
  - 验证：CUDA 构建、量化回归、memcheck/racecheck、MiSS 兼容性、Launcher 测试通过；**HIP 仅保留 W8，本轮未测**

### 2. `torchtitan-rwkv` → `torchtitan-rwkv-old`
- `rwkv-rs/torchtitan-rwkv` 已不存在（git ls-remote 404/需认证），`rwkv-rs/torchtitan-rwkv-old` 存在
  （BSD-3-Clause，最后推送 **2026-08-28**）
- `rwkv-rs` 组织 **public repo 数 = 39**（org API 实测，与日检 40→39 一致）
- 判断：更名/退役信息属实；但该 repo 自 8 月起已无推送，"规模化主线转向 Megatron"是**推断**，
  直接证据是 `Megatrwkv-Bridge` PR #1/#2 连续合入

### 3. 39 仓清单与"未追踪仓库"的修正
org API 拉取全部 39 个 repo，与我们的 `tracking/repos.txt` 对比：

| 判断 | 结果 |
|---|---|
| 日检列的 `browsecomp-plus-eval` / `codex-compact-router` / `chinese-babylm-eval-pipeline` / `RWKV-AUTODECO` / `wandb-rs` / `wx-cli` | **我们早已追踪**（不是"从未追踪"） |
| 确实未追踪 | `rhi`、`rhine`、`rhine-schema-derive`、`originium`、`rwkv-cc`、`rwkv-peft-simple`、`MediaCrawler` |
| 日检**漏掉**的 | **`rwkv7-ascend-npu`**（无 LICENSE，Ascend 910B3 推理/serving）、**`llm-compressor-rwkv`**（Apache-2.0） |
| 其他未列 org 仓 | `Albatross`（Apache-2.0 推理引擎）、`burn`/`cubecl`（Apache-2.0，Rust DL 栈） |

各新仓库身份（org API 元数据）：
- `browsecomp-plus-eval`：**BrowseComp-Plus 可复现评测包**（parallel-candidate routing），**无 LICENSE**，最后推送 2026-07-21
  → 不是新仓，是既有评测仓
- `rwkv-cc`：**Linear-RNN based biological/chemical language model**（不是"cc"之谜），无 LICENSE
- `MediaCrawler`：小红书/抖音/快手/B站/微博/贴吧/知乎爬虫（第三方项目，`NOASSERTION`）
- `rwkv-peft-simple`：Apache-2.0；`rhine`/`rhi`：GPL-3.0；`rhine-schema-derive`：MIT；`originium`/`wandb-rs`：无 LICENSE
- `wx-cli`：Apache-2.0（WeChat local data CLI）

### 4. 其他核验
- `rwkv-agent-eval` 三个 Pi PR **仍 open**（#1/#2/#3，均 2026-11-12 创建，第 4 天未合并）✅
- `irwkv` open PR **#8**（state before chat generation，10-31）与 **#12**（better state management，11-07）✅
- `rwkv-org/F-rwkv` **只剩 LICENSE**（11357 bytes），与"第 3 天只有 LICENSE"一致 ✅
- `any2rwkv` 的 MLA/KDA 四个文件 **均 0 字节**（docs/kda2rwkv.md、docs/mla2rwkv.md、src/.../kda2rwkv.py、mla2rwkv.py）✅
- `dsh-rwkv-plugin` 确有 2026-11-14 的 `usage: report exact RWKV token counts, not a characters/3 estimate` 提交 ✅
- `123213213weqw` 的 Venturi 分支：未回源（与 RWKV 无关，跳过）

## 二、对日检摘要的修正（重要）

| 日检说法 | 修正 |
|---|---|
| "量化重构是**评测变快的真正原因**，把 11-06/07 超时 3.9→8.0、11-11 无超时串起来" | ❌ **时间顺序不成立**：11-11 的 58.7 评测报告明确写推理服务是 **11-09 编译**（含 adapter 修复和 PR #23），而 SB6/W4/W6 重构是 **11-14** 才提交 → 该次评测不可能用上 SB6。超时消失更可能来自 adapter 修复 + PR #23 性能优化（报告原文归因）；量化重构是**之后**的独立变化 |
| "评测分数是在量化后的引擎上跑出来的（4/6-bit 会影响分数）" | ⚠️ 部分成立但需限定：11-09 build 可能已用 W8A16（重构前就存在），但 **W4/W6 SB6 不适用**于 58.7 那次；未来若在 SB6 W4 上跑分，精度才是新的混淆变量 |
| "这批仓库从未追踪过" | ⚠️ 6 个我们已追踪；漏了 `rwkv7-ascend-npu`、`llm-compressor-rwkv` |
| "torchtitan 路线正式退役" | ✅ 更名属实；补充：该仓 8 月起已停滞，"退役"是行政动作，训练主线证据在 Megatron-Bridge |

## 三、对我们的影响

1. **量化/精度将成为评测混淆变量**：未来 RWKV 官方 agent 分数若使用 SB6 W4/W6，必须同时报告精度守护指标（CE/top-1 一致率），否则 58.7 这类数字不可跨版本比较。我们自己的评测（skyrl+vLLM bf16）无此问题。
2. **仓库面扩张**：`rwkv7-ascend-npu`（NPU serving）与 `llm-compressor-rwkv`（压缩）是比 Rust 周边更有信息量的新增；`browsecomp-plus-eval` 早已存在但**无 LICENSE**。
3. **RL 结果仍无**：本轮变化仍是 serving/训练基础设施，无新 RL 分数；此前 58.7 是 SFT。
4. 许可证持续分化：GPL（rhine/rhi）、无 LICENSE（originium/wandb-rs/rwkv-cc/browsecomp-plus-eval/rwkv7-ascend-npu）、Apache（rwkv-peft-simple/Albatross/llm-compressor-rwkv）——公开交付继续只用 Apache/MIT。

## 四、引用

- 量化重构提交: https://github.com/Alic-Li/rwkv_lightning_cuda/commit/323de533cce2e67bb92d8aa92a7d3533eb246c7b
- `torchtitan-rwkv-old`: https://github.com/rwkv-rs/torchtitan-rwkv-old
- org 仓清单: https://github.com/orgs/rwkv-rs/repositories
- eval PRs: https://github.com/rwkv-org/rwkv-agent-eval/pulls
- irwkv PRs: https://github.com/rwkv-org/irwkv/pulls
- F-rwkv: https://github.com/rwkv-org/F-rwkv
