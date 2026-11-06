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

## 五、2026-11-06 新增（v8/ROSA 前沿 + 活跃度分层）

### 新信息源
| 源 | 地址 | 看什么 |
|---|---|---|
| RWKV-v8 README | https://github.com/BlinkDL/RWKV-LM/tree/main/RWKV-v8 | 官方 ROSA 说明 + 社区 ROSA 项目列表（8 个） |
| helicopter | https://github.com/w1c2j3/helicopter | 5 条 agent 管线 / 24 benchmark / 27 EvalScope 数据集；**无许可证、2026-08-10 停更、零公开分数** |
| rwkv_lightning_cuda | https://github.com/Alic-Li/rwkv_lightning_cuda | 官方教程推荐推理引擎；含 No-22 与 **Claude** 的提交 |
| ROSA 社区项目 | zyaaa-ux/ROSA-Tuning(MIT) · wjie98/rosa_soft(MIT) · johanwind/wind_rosa(MIT) · xiaoiecc/qkv-rosa-fast-exact-backward(MIT) · Juste-Leo2/ROSA-GPU-RWKV8(Apache) · x-0D/RASP(无) · KakaruHayate/RWKV8-ROSA-FPGA(无) · aabbdev/rosa(无) | 活跃度、许可证、是否出现 serving/RL 集成 |

### 第 9–11 项信号（追加）
9. **v8/ROSA**：官方是否发布 v8 HF 权重、主流 serving 是否支持 ROSA、BlinkDL 是否把 v8 设为主线。
10. **helicopter/scoreboard**：是否首次公开分数、是否补 LICENSE、是否恢复提交。
11. **AI 共同开发**：`Claude` 等 AI 作者提交是否出现在 RL/训练关键路径（影响数值可信度评估）。

### 活跃度分层（2026-11-06 快照）
- A 层（近 30 天）：Alic-Li、josStorer、Cai-z-us、No-22、HaloWang、Joluck、w1c2j3、xiaoiecc
- B 层（近半年）：wjie98、shiroko98、MollySophia、cryscan、顾真牛、johanwind
- C 层（已停更）：zhiyuan1i、yzhangcs、Blealtan、RyanLuohaha、w-zz-w-zz-w
- 结论：v7 引擎侧退潮；v8/ROSA 最活跃；v7 的 agent/RL 层靠少数单点维持 → 依赖必须 pin + 本地镜像。

## 六、2026-11-06 新增：官方项目目录（rwkv.cn）

| 项 | 内容 |
|---|---|
| 页面 | https://www.rwkv.cn/eco/projects |
| 数据 API | `https://www.rwkv.cn/eco/projects.json`（页面客户端 `fetch("/api/projects")` 同数据） |
| 规模 | **95 项**，`lastUpdated=2026-10-19`；8 个类别（推理 27 / 多模态 26 / 其他 13 / 训练 12 / Agent 7 / 聊天 API 5 / 基准 3 / 分词器 2） |
| 本地快照 | `data/rwkv-cn-eco-projects-2026-11-06.tsv` |
| 刷新命令 | `curl -s https://www.rwkv.cn/eco/projects.json \| python3 -c "import json,sys;d=json.load(sys.stdin);print(d['count'],d['lastUpdated'])"` |
| ⚠️ 坑 | **目录 `repo_updated_at` 不可信**（如 `RWKV/RWKV-infctx-trainer` 目录 2026-09-04，实际最后提交 2024-04-25）→ 活跃度必须用 `commits.atom` 实测；目录只作索引 |
| 官方 org | 除 `BlinkDL/RWKV-LM` 外还有 `RWKV/` org（如 `RWKV/RWKV-infctx-trainer`），加入跟踪源 |

### 第 12 项信号（追加）：`irwkv`（原生 RWKV-7 服务框架）
- 正式仓 https://github.com/rwkv-org/irwkv （Apache-2.0；13 commits；main 2026-11-02）
- 镜像 https://github.com/w1c2j3/irwkv （Chase 的 `chase/rwkv-state-continuation` / `prefix-cache` / `context-compaction` 分支）
- 看什么：state 续接 / prefix cache / tool calling / top-k logprobs / RL weight-update 接口是否稳定，
  以及是否与 skyrl-rwkv 集成（同源团队，可能性存在）。
- 归属注意：**irwkv 由张恺之（Cai-z-us）主导**，不是 Chase 独写；Chase 的贡献在分支。
