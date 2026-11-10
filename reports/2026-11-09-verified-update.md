# 2026-11-09 核验：`rwkv_lightning_cuda` 在线 RL server 与生态空白修正

核验日期 2026-11-09。核验方式：GitHub 仓库页 + `docs/online-rl.zh-CN.md`（HTTP 200）+ 根 `LICENSE`（HTTP 404）。

## 1. 事实（文档可查）

`Alic-Li/rwkv_lightning_cuda` 不只是推理引擎，自 2026-10-23 起包含三个常驻在线 RL server：

| 模式 | server | 训练参数 | 冻结 |
|---|---|---|---|
| MiSS | `rwkv_miss_tune_server` | MiSS 的 `D` | 初始 State |
| State | `rwkv_state_tune_server` | 初始 `time_state` | Adapter |
| NoRA | `rwkv_nora_tune_server` | NoRA 的 A/B | 初始 State |

已文档化的能力：GRPO / Dr.GRPO（客户端算 advantage）、actor+learner 共享 BF16 backbone、`--keep-versions` 快照、CPU Radix+LRU 前缀缓存、token 级 `loss_mask`、`/v1/logprobs` 教师强制 + reference KL、`policy_version`/`expected_step` CAS、多轮 tool 客户端示例（**server 不执行工具**）、temperature 后采样 logprob（无 top-k/top-p，避免截断采样与 CE 不一致）。

限制：纯 on-policy REINFORCE（无 PPO clipping/内置 KL）、单 GPU worker 串行、**PEFT-only**、C++/CUDA 无 PyTorch、**无 LICENSE**。

## 2. 判断修正

| 判断 | 状态 |
|---|---|
| 没有 agent 评测成绩 | ❌ 已推翻（此前已确认） |
| **没有 agentic RL 基建** | ❌ **本次推翻**（2026-10-23 起已有，但无许可证） |
| 没有 agentic RL **公开成绩** | ✅ 仍成立 |
| 缺许可证 | ✅ 仍成立（根 LICENSE 404） |

## 3. 我们的位置

- 继续 **skyrl-rwkv（Apache-2.0）** 路线：可公开、可复现、支持全参 FSDP + vLLM，工具环境与多轮已跑通
- 不采用/不复制 `rwkv_lightning_cuda`（无 LICENSE；PEFT-only；C++/CUDA 维护成本高），仅作设计参考
- 借鉴其正确做法：**采样温度与 CE/logprob 一致性**（我们训练采样 temp=1.0/top-p=1/top-k=-1，天然一致；若以后改截断采样必须同步修 CE）、**token-id 历史拼接**、**turn 级 loss_mask**
- 我们的公开空白因此更明确：**① 公开的多轮工具 RL 训练结果；② 许可证干净的可复现 recipe**

参考：
- https://github.com/Alic-Li/rwkv_lightning_cuda
- https://github.com/Alic-Li/rwkv_lightning_cuda/blob/main/docs/online-rl.zh-CN.md
