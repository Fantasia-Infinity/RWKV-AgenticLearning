# 2026-11-10 生态核验更新（含对日检摘要的修正）

> 核验时间：2026-11-10 10:00–10:30 CET。方式：GitHub API 逐 PR 核对（merged_at / state / author / body）+ 本地环境实测。
> 本文只记录**已回源确认**的事实；二手摘要中的措辞问题在「修正」小节单列。

## 一、已核验事实

### 1. `rwkv-rs/transformers-rwkv` PR #20 —— 工具调用历史的渲染修复
- 标题（原文）：**`fix(rwkv): render tool-call history in the instructed format`**
- 作者 `w1c2j3`；**merged 2026-11-10T07:48:36Z**，merge commit `6d0d57af`，+23/−3，2 文件
- 内容（PR body 原文要点）：
  1. **崩溃修复**：带工具调用历史 + system 消息 + **无 `tools`** 的对话会抛 `TypeError: 'NoneType' object is not iterable`；模板从 `tools | default([])` 改为 `tools or []`（vLLM / irwkv 会传 `tools=None`）
  2. **参数格式修复**：过去的工具调用原先渲染成缩进 JSON，且 OpenAI 风格字符串 `arguments` 被转义成 `"arguments": "{\"city\": ...}"`；现改为 system prompt 要求的一行格式：`{"name": "weather", "arguments": {"city": "Paris"}}`
- PR 明言：**不含工具调用的对话与 main 渲染字节级一致** → 这是对既有渲染的格式/崩溃修复，不是"首次支持"。
- 我们的现状：HF 导出 `weights/g1l-1.5b-hf/chat_template.jinja` 是 **pre-#20** 版本（实测：`payload | tojson(indent=2)` 渲染历史工具调用；`tools | default([])` 存在崩溃边）。我们渲染时都传了 `tools`，故未触发崩溃；但多轮工具历史是缩进 JSON，与 system prompt 要求的一行格式不一致。

### 2. `rwkv-rs/transformers-rwkv` PR #21 —— FlashRWKV2 0.1.0a18
- 作者 `Cai-z-us`；**merged 2026-11-10T08:28:33Z**，merge commit `46bb5d26`
- 内容：RWKV extra / weight-publisher 依赖升到 `FlashRWKV2 0.1.0a18`；移除生成与 benchmark 中已废弃的 `legacy_dir` 调优参数；运行时版本检查继续钉版本
- 我们的 stack 仍 pin **0.1.0a17**（skyrl-rwkv + vllm-rwkv），未跟随；升级需重跑 kernel/数值对齐验证，暂不动。

### 3. `rwkv-org/irwkv`（Apache-2.0）—— open PR 清单
- **open**：#7（`w1c2j3`，structured-output 保持 Rapid-Sampling CUDA graphs；11-10 07:01 有更新）、#12（`Triang-jyed-driung`，state LRU cache + 上下文 sha1；**11-07** 创建）、#14（`Cai-z-us`，原生 RWKV-7 checkpoint 权重热重载；**11-10 05:03** 创建）
- **#13**（`Cai-z-us`，"Expose the upstream router through irwkv"）：created 11-10 03:53，**closed 11-10 08:28 但 `merged_at = null`** → 关闭未合并
- `mtp`（Joluck 投机解码）分支仍未并入 `main`

### 4. `Interactive-Active-AI/NextTransformer`（MIT，400★）
- PR **#38** "Add Gated Attention (elementwise and headwise) with audited formal results"：**merged 2026-11-09T12:08:56Z**（不是 11-10），作者 `euyis1019`，+4794/−94，33 文件
  - 正式结果（update 46,875, seed 42）：Dense BPB 0.664460 / headwise 0.664678 / elementwise 0.666731 → **gated attention 未超 Dense**；CORE 增益主要来自 CommonsenseQA（其余 21 任务均值 34.43 / 34.28 / 33.73）
- RWKV 仍不在该架构擂台上

## 二、对日检摘要的修正

| 日检说法 | 核对结果 |
|---|---|
| "PR #20 是 w1c2j3 的工具调用历史渲染" | ✅ 作者/主题正确；但应表述为**格式修复 + tools=None 崩溃修复**，"HF 集成层终于开始正确渲染多轮工具调用"是夸大（此前已渲染，只是格式不对） |
| "同日 Cai-z-us 还有 PR #21（FlashRWKV2 0.1.0a18）" | ✅ 正确（08:28:33Z 合并） |
| "irwkv 出现 3 个 open PR（#12/#13/#14）" | ❌ **#13 已关闭未合并**；实际 open 是 **#7 / #12 / #14**；且 #12 是 11-07 创建，不是今天新增 |
| "#12 社区新面孔 Triang-jyed-driung" | ✅ 作者正确 |
| "NextTransformer PR #38 已合" | ✅ 已合，但合入时间是 **11-09 12:08Z**（非 11-10） |
| "基线文件积压 8 处过期" | 属日检自身文档卫生问题，与公开事实无关；本仓库 tracking 基线（2026-11-09 报告）另行刷新 |
| "六层里五层就位，唯一空着的是真训一轮 RL 并出分" | ⚠️ 需限定：评测层数据/代码**无 LICENSE**（不可复用，只能引用数字）；mtp 未并入 main、router PR 未合并；公开可复现链仍缺（训练数据私有、adapter 无公开权重、evaluator 无 LICENSE）。"出分"缺口限定在**多轮 agentic RL**；单轮数学 RL 我们正在出分（见下） |

## 三、我们的对应动作

1. **模板**：P4 多轮数据重渲染前，从 `rwkv-rs/transformers-rwkv` main 取 post-#20 `chat_template.jinja` 覆盖 HF 导出模板；补 tests：tools=None + 工具历史 + system 的渲染回归。
2. **训练数据**：已有 P1.5/P3 数据是 pre-#20 模板渲染（历史工具调用缩进 JSON），保留作历史；新数据用新模板。
3. **B1（DAPO 1000 步，单轮 GSM8K RLVR）**：step100/200/300/400 avg@4 = 21.5 / 25.6 / 27.9 / **30.25%**（base 21.0%）→ 正在填"真实训 RL 并公开出分"的空缺（单轮；多轮 agentic RL 仍是空白）。
4. **公开交付**：继续坚持 license-clean：只引用 `rwkv-agent-eval` 数字，不复制其数据/代码；adapter 无权重的情况在报告中注明。

## 四、引用

- transformers-rwkv #20: https://github.com/rwkv-rs/transformers-rwkv/pull/20 （merged 2026-11-10T07:48:36Z）
- transformers-rwkv #21: https://github.com/rwkv-rs/transformers-rwkv/pull/21 （merged 2026-11-10T08:28:33Z）
- irwkv PR #7/#12/#13/#14: https://github.com/rwkv-org/irwkv/pulls
- NextTransformer #38: https://github.com/Interactive-Active-AI/NextTransformer/pull/38 （merged 2026-11-09T12:08:56Z）

---

# 14:00 批次核验（当日第二轮）

> 核验时间：2026-11-10 14:10–14:25 CET。GitHub API 逐条核对。

## 五、已核验事实（14:00 日检）

### 1. `No-22-Github/dsh-rwkv-plugin` PR #1 —— 请求级 adapter 恢复 + AdapterPicker
- 作者 `Alic-Li`，**merged 2026-11-10T08:30:36Z**（由 `No-22-Github` 合并），+1218/−396，14 文件
- 正文覆盖：LightningClient 恢复 `adapter_id`（`/v1/batch/completions`）与 `listAdapters / uploadAdapter / deleteAdapter`（`/v1/adapters`）、Host 恢复 `/api/rwkv/adapters` 中继、Settings UI 在 StatePicker 下新增 AdapterPicker（自动拉取/手填 ID/上传 `.pth`）、"Task-specific contract" 文本域、`--adapter` 脚本参数与单测
- 判断：**属实**。注意标题是 "Restore"，即恢复此前被移除的能力；插件本体 MIT，但底层 `rwkv_lightning_cuda` 仍无 LICENSE

### 2. `rwkv-rs/transformers-rwkv` 后续提交 `c62a794` —— "update sampling defaults and agent guidance"
- 作者 `Cai-z-us`，direct commit **2026-11-10T09:01:41Z**，+55/−30，6 文件
- 实际改动（API 文件清单）：
  1. `.ai/AGENTS.md`（+36/−24）：仓库开发指引翻译/补充（含 non-pollution principle）——**是"给 AI coding agent 的仓库开发规范"，不是 RWKV 模型 agent 使用指南**
  2. `temp/rwkv_pth2st.py`：`generation_config.json` 默认值改为 temperature 0.96 / top_p **0.90**（原 0.76）/ top_k **-1**（原 32）/ frequency_penalty **0.09**（原 0.1）/ penalty_decay **0.994**（原 0.988）
  3. `src/transformers/models/rwkv/generation_rwkv.py`：`top_k == -1` 规范化 + logits processor 校验
  4. 两个测试文件同步更新
- **修正日检**："HF 集成开始带 agent 专用采样默认值"不准确：改的是**对话通用** `generation_config.json`；**agent/工具用的 `tools_generation_config.json` 未变**（仍 0.96 / 0.76 / 32 / 0 / 0 / 0.996）

### 3. `Interactive-Active-AI/NextTransformer` PR #41 —— Dense 200B scaling 参考跑
- 作者 `Enderfga`，**merged 2026-11-10T12:49:07Z**，5 commits，+1710/−1，17 文件
- 内容：40 层 / width 2560 / 200B tokens / 4k ctx（协议 `nextt-scale-200b-4k-v1`）；**final val BPB 0.5748，CORE 0.4618（22 任务）**；checkpoint 发在 HF（`Enderfga/nextt-scaling-dense-200b-4k`）
- 明言：**不属于 49B frozen 对比协议、不是 leaderboard 条目**（scaling 参考）；
- 判断：**属实**。RWKV 仍不在 NextTransformer 候选集中

### 4. `x-harness-rs` WordCraft 插件
- 未回源核验（与 agent/RWKV 主线无关，日检自己也标注"关系不大"）

## 六、对 14:00 判定的修正

| 日检说法 | 修正 |
|---|---|
| "多 adapter 合批 rollout 闭环打通" | ✅ 代码层面属实（请求级 adapter + UI + 上传），是异步 RL/多 checkpoint 评测的**使能件**；但**不是单策略 RL 的前置条件**（我们的 P2/P3/B1 全程单 policy+ref，无需 per-request adapter） |
| "所有零件都造好了，只等一个人接起来跑一轮并公布数字" | ⚠️ 过于乐观。真实剩余：(a) **算力**——官方 1000 步 DAPO 若按上游默认 batch（1024 prompts×5 samples）≈ 5.12M rollouts，是我们缩小版 B1（1000 步×16 rollouts=16k）的 **320 倍**；(b) **多轮 agentic RL 的正向结果**仍空白（我们 P3 是负结果）；(c) **许可**：训练数据私有、`rwkv-agent-eval` 无 LICENSE、adapter 无公开权重 |
| "下一轮盯 rwkv-agent-eval 出现 RL 训练 adapter" | ✅ 方向对；但即使出现，无 LICENSE → 我们只能引用数字、不能复用数据/代码 |

## 七、我们自己的对照进展（同时段）

- B1（DAPO 1000 步，单轮 GSM8K RLVR）step 703/1000；avg@4：100→21.5 / 200→25.6 / 300→27.9 / **400→30.25** / 500→25.25（base 21.0）——小批量 DAPO 有 ±5pp 振荡；step600/700 评测已提交
- 我们已有 **多轮工具 RL 的公开负结果**（P3：tool RL 后 held-out tool-name 98.9%→82.2%，GSM8K-calc 38.55% < SFT 42%），这是目前唯一公开的 RWKV 多轮 agentic RL 证据

## 八、引用

- dsh-rwkv-plugin #1: https://github.com/No-22-Github/dsh-rwkv-plugin/pull/1 （merged 2026-11-10T08:30:36Z）
- transformers-rwkv c62a794: https://github.com/rwkv-rs/transformers-rwkv/commit/c62a794e9f03e5ac7d6d5cc43d3dfacee6df0374
- NextTransformer #41: https://github.com/Interactive-Active-AI/NextTransformer/pull/41 （merged 2026-11-10T12:49:07Z）
