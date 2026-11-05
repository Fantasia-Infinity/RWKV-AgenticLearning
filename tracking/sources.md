# RWKV 生态跟踪源清单（三层信息源 / 8 项信号 / 失真登记）

> 重建于 2026-11-05（基于 `内部交接 2026-11-05（未公开存档）` §11 线索 + 本日实测）。
> 用途：每轮复查按「三层 + 8 信号」走一遍，避免只看 rwkvos 目录造成系统性漏项。

## 一、三层信息源

### L1 一手事实源（必须回源核验，优先级最高）
| 源 | 地址 | 看什么 |
|---|---|---|
| rwkv-rs 组织 | https://github.com/orgs/rwkv-rs/repositories?type=all | 新仓库（**交接漏了 10+ 个**，见 `reports/eco/`）、各仓活跃度 |
| skyrl-rwkv | https://github.com/rwkv-rs/skyrl-rwkv | RL 训练基座：分支/提交/lau ncher/多轮配置 |
| vllm-rwkv | https://github.com/rwkv-rs/vllm-rwkv | skyrl 绑定 pin 的上游；commit 活跃度 |
| wkvm | https://github.com/xiaol/wkvm | state slot 原语；LICENSE（缺失中）；最后提交 2026-08-02 |
| RWKV-Megatron | https://github.com/TimeMobius/RWKV-Megatron | 默认分支 `muon`；`codex/qwen-rwkv28b-distill`（28B 线索） |
| RWKV-PEFT | https://github.com/Joluck/RWKV-PEFT | 官方 PEFT（LoRA/MiSS/State/MTP） |
| RWKV-LM-RLHF | https://github.com/OpenMOSE/RWKV-LM-RLHF | DPO/ORPO/SIMPO/WPO/GRPO（2025-07 后停） |
| FlashRWKV2 | https://github.com/rwkv-rs/FlashRWKV2 | **已从 BlinkDL/ 迁至 rwkv-rs/**，MIT；kernel 层 |
| 官方文档/教程 | https://www.rwkv.cn/tutorials/ | 官方口径（有无 agent/RL 新内容） |
| 官方 HF 模型 | https://huggingface.co/RWKV | 新权重（G1 系列 / 是否出现 agent 后训练权重） |

### L2 社区目录（线索索引，不能当事实）
| 源 | 地址 | 备注 |
|---|---|---|
| Agent 目录 | https://agent.objects.rwkvos.com/zh | 46 条；数据质量问题见交接 §1.4 |
| 生态目录 | https://agent.objects.rwkvos.com/zh/resources | 187 条 |
| Awesome-RWKV | https://github.com/RWKV-Vibe/Awesome-RWKV | 169 条，广谱 |

### L3 二手/成绩源（结论唯一出处，需标注日期）
| 源 | 地址 | 备注 |
|---|---|---|
| Scarlet Wolf 博客 | https://scarletwolf.ai/blog/rwkv-state-tuning-parite-qwen / https://scarletwolf.ai/blog/rwkv-mur-des-60 | 唯一有可复现 agent 成绩的公开来源 |
| toolcaller-bench | https://codeberg.org/scarletwolf_ai/rwkv-toolcaller-bench | 82 题 × 231 工具；Apache-2.0 |
| 官方公众号「RWKV元始智能」 | 微信 | 研讨会/路线图口径（2026-10-26 第四期） |

## 二、8 项信号（每轮必查，出现即记 delta）

1. **skyrl-rwkv 仓库**：新分支 / 提交频率 / `max_turns` 是否被设置 / `skyrl-agent` 是否接 RWKV / TLPO 是否合入。
2. **vllm-rwkv**：提交活跃度；skyrl 的 pin 是否前移或改回公开版本。
3. **wkvm**：LICENSE 是否补上；RWKV-7 durable-state 路径是否出现 benchmark/成绩；chat API 是否补 tools/logprobs/stop。
4. **Helicopter / scoreboard**：`rwkv-rs/Helicopter` 是否出现（当前 404）；是否以别的名字存在（`browsecomp-plus-eval`、`feat/heli-r00-training-eval` 等）。
5. **RWKV-Megatron**：`codex/qwen-rwkv28b-distill` 是否有真实 28B 训练证据（配置/脚本/日志/权重）。
6. **评测成绩**：toolcaller-bench / τ-bench / BFCL / AgentBench / BrowseComp 是否出现新的 RWKV 数字（尤其多步类别）。
7. **官方口径**：rwkv.cn / 公众号是否把 agentic RL 写进路线图；是否发布 agent 相关权重/工具。
8. **Agent 目录**：46/187 条目的增删、新增 project、许可证与活跃度变化。

## 三、失真登记（已知坑，别重复踩）

| 类型 | 案例 | 处理 |
|---|---|---|
| 目录标错许可 | `123123213weqw/rwkv-agent` 目录 MIT 实为 AGPL-3.0 | 关键决策前回源读 LICENSE |
| 目录未标归档 | `1cyberlangke1/rwkv-jev-like` 已 archived | 查 `archived` / 最后推送 |
| 名不副实 | `xiaol/WuNeng` 零行 RWKV 代码；`Ai00-X/ai00_server` 无 agent 能力 | 读代码再下结论 |
| 仓库迁移 | `FlashRWKV2` 从 BlinkDL/ 迁到 rwkv-rs/（2026-11-05 实测 BlinkDL 路径 404） | 用 org 清单校准 owner |
| 分支名记错 | 交接写 `codex/rwkv28b-distill`，实为 `codex/qwen-rwkv28b-distill` | 用 `git ls-remote --heads` 为准 |
| GitHub size 失真 | `RWKV-LH` GitHub size 含已清理历史（948MB vs 发布树 5.2MB） | 以 clone 后实际为准 |
| API 配额 | 未认证 60/h，全队共享 | 优先 ls-remote / atom / raw；API 仅必要时 |

## 四、每轮复查命令

```bash
cd ~/AlchemyRepos/RWKV-AgenticLearning
bash tracking/check.sh                 # 全量快照 → tracking/runs/<ts>.md
bash tracking/check.sh --diff          # 与上一轮对比，只打印变化
```

脚本零 GitHub API 调用：用 `git ls-remote`（HEAD/分支）、`commits/<branch>.atom`（最后提交时间）、`raw.githubusercontent.com`（LICENSE 探测）。
