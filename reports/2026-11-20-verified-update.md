# 2026-11-20 生态核验更新：官方 RWKV Agent 专场（11-26）+ FlashRWKV2 0.2.0a1 一夜迁移

> 核验时间：2026-11-20 17:55–18:30 CET。来源：rwkv.cn news API、PyPI JSON、GitHub PR/contents API。
> 对应外部摘要：2026-11-20 日检。

## 一、官方公告（已回源）

`rwkv.cn/news` 条目 **#23423445**（2026-11-19，作者「RWKV元始智能」）：
**《【直播预告】RWKV Agent专场》**

- 时间：**2026-11-26（星期四）19:30–21:00**，平台：微信视频号「RWKV元始智能」
- 三位嘉宾，官方统一称谓 **「RWKV 算法专家」**：
  1. **顾真牛** — 《基于 RWKV 的混合推理 Agent 系统》（Ai00-X）
  2. **chase** — 《RWKV Agent 的构建——从检索到执行》
  3. **No.22** — 《从续写到干活：RWKV Agent 的训练、推理与评测闭环》
- 公告导语明确写：**"接入 DeepSeek Harness，通过 Harness 和微调增强模型能力，以及与大模型的协作"** ——官方口径第一次把 DSH 写进 Agent 实践主线。

### 公告中的数字（原文已核对）
| 嘉宾 | 内容 |
|---|---|
| 顾真牛 | 自研运行时 **rwkv-rsv**（纯 Rust + Vulkan/CUDA，已开源）：3B 模型 **3.2 GB** 显存；单张 **RTX 2080 Ti** B=128 稳态 **1039 tok/s**，256 槽批量 **4264 tok/s**；160 题长对话：纯本地 **58** / 混合 **94** / 纯远端全量直灌 **103**；混合单跳 1,862 token p50 **0.95s**、双跳 3,839 token p50 **2.3s**，相对 23,683 token 全量直灌省 **84%–92%** |
| chase | RWKV 原生接入通用编程 Agent 框架 **Pi**；推理/训练逐字节一致协议、工具容错、针对循环状态的长程上下文压缩；**7.2B 与 13.3B 两种规模任务完成率均提升到原来的 3 倍以上**；将讲"走过的弯路与放弃的方案" |
| No.22 | 端侧纯本地 **7B**、**W8A16 / W4A16** 量化；从早期自研框架**全面转向 DSH 插件化路线**；依托 **rwkv_lightning_cuda**；打通 DSH 插件 + 轨迹蒸馏 + 沙箱评测闭环；**7B 实际任务完成率较基模数倍提升** |

### 身份/定级修正（重要）
- 官方确认为 **"RWKV 算法专家"** 三人 → 此前我们标为"独立开发者/疑内部/外部"的定性需要升级为**官方认证专家**。
- 但**公告没有直接写 GitHub 账号映射**：
  - 顾真牛 ↔ `cgisky1980`：**推断**（Ai00-X / rwkv-rsv 作者）
  - chase ↔ `w1c2j3`：强推断（rwkv-pi 与 eval Pi backend 作者、插件/irwkv PR 作者）
  - No.22 ↔ `No-22-Github`：强推断（dsh-rwkv-plugin 作者）
  记录时应标"官方称谓已确认；账号映射为推断"。

### 四条旧判断的更新
| 旧判断 | 更新 |
|---|---|
| "RWKV 没有官方 Agent 路线" | ❌ 需修正：官方首次办 **Agent 专场**并称三人都为算法专家；但**仍是研讨会披露，不等于官方产品/路线图**，且无绝对分数 |
| "DSH 只是社区选择" | ❌ 修正：官方公告把 DSH 写入 Agent 实践导语；No.22 也明确"全面转向 DSH 插件化" |
| "没有 agent 能力数字" | 🟡 部分修正：首次给出**相对数字**（3×+、数倍、58/94/103、省 84–92% token），但**仍无绝对分数与标准 benchmark** |
| "顾真牛是独立开发者" | ❌ 修正：官方称其为 **RWKV 算法专家** |

### 新发现仓库：`cgisky1980/rwkv-rsv`（此前未追踪）
- GitHub API 实测：**★4**，created **2026-08-07T02:30:33Z**，last push 2026-11-09，**MIT License**
- 描述："RWKV-7 inference engine in Rust (Vulkan compute shaders) with fp16/any4/int8 quantization paths"
- 与公告中的 rwkv-rsv 对应 → **license-clean（MIT）的 Rust/Vulkan 推理运行时**，值得纳入跟踪

## 二、FlashRWKV2 0.2.0a1 迁移（一夜合并，已核验）

- **PyPI**：`FlashRWKV2 0.2.0a1` **已发布**（upload 2026-11-19T20:42:56Z，MIT，`torch>=2.11,<2.15`、`tilelang==0.1.15`）；
  README 明确：serving 在 SM89/SM120 建议 FP16 recurrent state；**训练 / RL rollout / eval 与采样搜索用 FP32 state 以复现 learner logprobs**
- **open PR 数（2026-11-20 实测）**：`irwkv` **0**、`vllm-rwkv` **0**、`transformers-rwkv` **0**、`FlashRWKV2` **0**
- 关键合并：
  | PR | 标题 | merged |
  |---|---|---|
  | irwkv **#28** | `[Core][RWKV] Default serving WKV state to FP16`（supersedes #25，基于已合并 #27） | 2026-11-19T21:21:35Z |
  | irwkv **#29** | `[Perf][RWKV] Bound overlapping state-pool transfers`（supersedes #21） | 2026-11-19T22:09:25Z |
  | transformers-rwkv **#25** | `chore: sync Transformers v5.23.0 into RWKV fork` | 2026-11-20T02:04:28Z |
  | FlashRWKV2 **#32** | `feat(mtp): add verifier checkpoints and offline draft dispatch` | 2026-11-19T21:53:50Z |
  | Megatrwkv-Bridge **#4** | `perf(model): use FlashRWKV2 token cross entropy for RWKV7 training` | 2026-11-19T21:33:23Z |
- 我们栈仍 pin **FlashRWKV2 0.1.0a17 / vLLM-RWKV 旧 pin**；0.2.0a1 是否升级需先做 parity（这次 API 变化较大：去 runtime tuning、MTP、FP16 state 默认）

## 三、未变项（复核）
- `rwkv-agent-eval` 三个 Pi PR **仍 open（第 9 天）** ✅
- `rwkv-org/F-rwkv` 仍只有 LICENSE（11,357B）✅
- `any2rwkv` MLA/KDA 四个文件仍 **0 字节** ✅
- `rwkv-rs` org public repo 仍 **39** ✅
- `rwkv-agent-pipeline` 未公开、JD/news 未变（按上次核验）

## 四、对我们的影响

1. **11-26 直播是下一个关键信息源**：三条路线（本地混合推理 / Pi 执行 / DSH 闭环）正好覆盖我们 P4/P5 的候选方向；
   chase 的"逐字节一致协议 + 长程上下文压缩"和 No.22 的"DSH + 轨迹蒸馏 + 沙箱评测闭环"与我们多轮 agentic RL 的空缺直接相关。
2. **官方口径把 DSH 纳入 Agent 主线**后，我们此前"DSH 是社区选择"的判断需要更新；但**仍无公开绝对 benchmark 分数**，我们的公开评测结果依然稀缺。
3. **FlashRWKV2 0.2.0a1（MIT）**落地：去 runtime tuning 对可复现性有利；FP16 serving / FP32 rollout 的分层与我们已知的 raw-logprob 约束一致。
   升级前需 parity；不急于改我们 pin 的 a17。
4. **rwkv-rsv（MIT）**是少数 license-clean 的推理运行时，适合公开可复现实验参考（lightning 无 LICENSE，不能直接用）。

## 五、引用

- 公告: https://www.rwkv.cn/news/read/23423445 （API `/api/news/23423445`）
- rwkv-rsv: https://github.com/cgisky1980/rwkv-rsv
- FlashRWKV2 0.2.0a1: https://pypi.org/project/FlashRWKV2/0.2.0a1/
- irwkv #28/#29: https://github.com/rwkv-org/irwkv/pulls
- transformers-rwkv #25: https://github.com/rwkv-rs/transformers-rwkv/pull/25
- FlashRWKV2 #32: https://github.com/rwkv-rs/FlashRWKV2/pull/32
- Megatrwkv-Bridge #4: https://github.com/rwkv-rs/Megatrwkv-Bridge/pull/4
