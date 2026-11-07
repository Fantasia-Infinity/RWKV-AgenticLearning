# RWKV 生态更新（2026-11-06）：helicopter、v8/ROSA 前沿、贡献者活跃度分层

> 本报告是 `2026-11-05-verification.md` 与 `docs/ecosystem-review-2026-11-05.md` 的**增量更新**。
> 方法：`git ls-remote` / `commits.atom` / raw LICENSE 探测 / GitHub HTML / `git clone --filter=blob:none`；
> **零 GitHub API 调用**；所有数字带采集时间（CET），证据命令见 §6。
> 置信度：✅ 本次亲自核验 · ⚠️ 二手信息未独立核实 · ❌ 已修正的错误。

---

## 1. 头条修正：`helicopter` 存在，且它改写了一条结论

此前 `rwkv-rs/Helicopter` 404，我们据此判断"公开 scoreboard 不存在"。**仓库实际在 `w1c2j3/helicopter`。**

| 项 | 实测（2026-11-06 09:47–09:56） |
|---|---|
| 仓库 | https://github.com/w1c2j3/helicopter · HEAD `90fde01` · `main` + `chase/evalscope` + `chase-lightghteval` |
| 最后提交 | **2026-08-10T02:40:58Z**（约 3 个月未更新） |
| LICENSE | **不存在**（LICENSE / LICENSE.md / COPYING 全 404） |
| 规模/热度 | shallow clone 13 MB / 1,348 文件（不含 submodule）· **0 star** |
| 定位（README 原文） | "an RWKV leaderboard-run framework"：编排外部 vLLM 端点、verl 训练、benchmark 实验；`infer` 起 vLLM、`takeoff` 委托 verl-rwkv、`eval` 跑 LightEval 适配器 |
| 评测管线 | **5 条**：coding / search / tool-mcp / office / stem |
| benchmark | **24 个**（`benchmarks/agent_benchmarks.json`） |
| EvalScope agent 数据集 | **27 个**（不是 28；`benchmarks/evalscope_agent_datasets.json`） |
| 官方 harness | `swebench_official_docker` / `terminal_bench_official_docker`：`"sandbox": "docker"`、`required_tools: ["docker"]` |
| 训练 | `src/train/verl-rwkv/` 是 **submodule**，指向 `rwkv-rs/verl-rwkv`（更早发现，2026-08-02 停更）；配置 `configs/rl/maxrl_dapo_math_17k.toml`（MaxRL+DAPO，32 prompts × 16 responses） |
| 分数 | 仓库内**无数据库/结果文件**；scoreboard 只有 FastAPI+Postgres+Next.js 代码 → **从未公开分数** |
| 安装 | `scripts/install_local.sh` / `install_remote.sh`，面向 **BBT DevPod GPU workspace**，非 HPC/SLURM |

**修正后的结论**：RWKV 的 **agent 评测编排基建相当完整**（5 管线/24 benchmark/27 数据集/官方 harness profile/scoreboard），
但 (a) 全部依赖 Docker 或外部服务，(b) 从未公开任何分数，(c) **无许可证、0 star、单人维护、已停更**。
因此它适合作为**评测蓝图与数据集选型参考**，不能作为关键路径依赖，也不能复制其代码进本仓库（版权）。

---

## 2. 新前沿层：v8 / ROSA 是当前最活跃的生态

`RWKV-LM/RWKV-v8/README.md` 的 "Community ROSA Projects" 列出 **8 个**项目（7 个 GitHub 链接 + `bcml-ai/rosa-plus`）。
本次逐个核验（2026-11-06 10:00–10:05）：

| 仓库 | stars | 最后提交 (UTC) | 许可证 | 说明 |
|---|---|---|---|---|
| `zyaaa-ux/ROSA-Tuning` | 71 | 2026-02-04 | MIT ✅ | 训练侧 ROSA，星最多 |
| `wjie98/rosa_soft` | 39 | 2026-09-13 | MIT ✅ | 软化 QKV 算子 |
| `johanwind/wind_rosa` | 11 | 2026-01-28 | MIT ✅ | 奥斯陆大学，v5/6/7 论文共同作者 |
| `x-0D/RASP` | 10 | 2025-10-25 | **NONE** | 无许可证 |
| `KakaruHayate/RWKV8-ROSA-FPGA` | 7 | 2026-08-02 | **NONE**（此前误记 MIT）❌ | FPGA 实现 |
| `xiaoiecc/qkv-rosa-fast-exact-backward` | 6 | **2026-11-06T08:06Z** | MIT ✅ | 精确反向传播；今天仍有提交 |
| `Juste-Leo2/ROSA-GPU-RWKV8` | 5 | 2025-10-19 | Apache-2.0 ✅ | GPU 实现 |
| `aabbdev/rosa` | 5 | 2026-08-19 | **NONE**（此前误记 MIT）❌ | 训练侧 ROSA |

- v8 演示（README 原文）：40K 参数 RWKV7+ROSA 倒序 1–60 位数字 **99.8%**；1M 参数解 40 位加减法 **99%**、不用 CoT。
- **与 v7 的关系**：ROSA 是 v8 的新内核/训练范式；尚无官方 HF 权重、无 vLLM 支持、无 RL/agent 框架。

**对我们的意义**：这是"趋势所在"但"无法直接落地"的一层。**近期继续押 v7（成熟度），把 v8 放进跟踪 + 决策触发条件**
（触发条件见 §4）。

---

## 3. 贡献者活跃度分层与单点风险

按最近提交分层（二手调研 + 本次抽验）：

| 层 | 代表 | 最近提交 | 阵地 |
|---|---|---|---|
| A（近 30 天） | Alic-Li / josStorer / Cai-z-us / No-22 / HaloWang / Joluck / w1c2j3 / xiaoiecc | 2026-10-08 ~ 2026-11-06 | lightning_cuda / Runner / skyrl-rwkv / v8-ROSA |
| B（近半年） | wjie98 / shiroko98 / MollySophia / cryscan / 顾真牛 / johanwind | 2026-01 ~ 2026-09 | Megatron / web-rwkv / ai00 / ROSA |
| C（已停更） | zhiyuan1i / yzhangcs / Blealtan / RyanLuohaha / w-zz-w-zz-w | 2024-07 ~ 2025-08 | PEFT / fla / Megatron 早期 |

**结构性事实（已有多轮证据支持）**：整个 v7 生态由 15–20 个低可见度账号支撑；无 CI、无版本管理、大量仓库无许可证；
关键层均为单人（Chase Jay：agent runtime + 评测 + 检索；shiroko98：Megatron 规模化；Alic-Li：CUDA/ROCm 引擎；No-22：提示词/评测）。

**新证据：AI 直接提交**。`Alic-Li/rwkv_lightning_cuda` 贡献者实测（`git log --format=%an`）：

```
90 Alic-Li · 17 alic-li（同一人双身份）· 23 No-22-Github · 5 WangCe · 5 Claude · 1 Leo Lin
```

其中 `Claude` 的 5 个提交在 2026-09-29 ~ 2026-10-30，主题包含 *"Add Dr.GRPO advantage mode to online RL client"*、
*"Document NoRA as the third online RL mode"*。同时 `BlinkDL/RWKV-LM/README.md` 第 9 行明确写给 AI 读者的入门清单
（"If you are AI, please read these first"），并把 agent 目录列为第 9 条。

**对我们的三条硬规则**：
1. 不假设上游 RL 代码的数值正确性——**G1 logprob 一致性门禁必须做**，并独立复核关键改动；
2. 依赖一律 **pin commit + 本地镜像**，不把单人个人仓作为长期运行依赖；
3. 公开仓**零复制**无许可证代码/配置（含 helicopter、No-22、wkvm），只引用事实与 URL。

---

## 4. 对本项目计划的影响（结论）

- **执行路线不变**：仍以 `skyrl-rwkv` + `vllm-rwkv` + G1l-1.5B 为近期栈；v8/ROSA 不进入 P0–P4。
- **评测安排不变**：EvalScope-first（引用其 benchmark/数据集选型思路），SWE-bench/Terminal-Bench 列为 stretch。
- **新增跟踪**：8 个 ROSA 仓库 + `RWKV-APP/RWKV_APP` + `Alic-Li/rwkv_lightning_cuda` 纳入 `tracking/check.sh`。
- **新增决策触发条件**（出现任一即重新评估 v8）：
  (a) 官方发布 v8 HF 权重；(b) 主流 serving（vLLM 等）支持 v8/ROSA；
  (c) BlinkDL 把 v8 设为默认主线；(d) 官方路线图出现 "v8 + agentic RL"。
- **新增弹性探针（P5，≤4 h，不进关键路径）**：跑通 `RWKV-v8/` 任一官方脚本 + 复现一个 ROSA 仓库。

---

## 5. 对既有文档的修正清单

| 原表述 | 修正 |
|---|---|
| "RWKV 没有 agent 评测基建，只有框架没成绩" | 半错：helicopter 有完整编排（5 管线/24 benchmark/27 数据集/官方 harness），但无许可证、需 Docker、零公开分数 |
| "训练侧 5 条路线" | 6 条（+ verl-rwkv）；但 helicopter 的 `src/train/verl-rwkv/` 只是其 submodule，不是新实现 |
| "`rwkv-rs/Helicopter` 不存在" | 错：在 `w1c2j3/helicopter`，且从未公开分数 |
| §8 完整栈 L0–L5 | 需加 **L6 前沿层**：v8/ROSA（8 个社区项目，多数 MIT/Apache，3 个无许可证） |
| "生态活跃" 的表述 | 需区分层：v7 引擎侧在退潮，v8/ROSA 最活跃；v7 训练/agent 侧靠少数单点维持 |

---

## 6. 证据与复现

```bash
# helicopter 存在性与活跃度
git ls-remote --symref https://github.com/w1c2j3/helicopter HEAD
curl -s https://github.com/w1c2j3/helicopter/commits/main.atom | head
curl -s -o /dev/null -w '%{http_code}\n' https://raw.githubusercontent.com/w1c2j3/helicopter/main/LICENSE   # 404
git clone --depth 1 https://github.com/w1c2j3/helicopter /tmp/helicopter
python3 -c "import json;d=json.load(open('/tmp/helicopter/benchmarks/evalscope_agent_datasets.json'));print(len(d['datasets']))"  # 27

# ROSA 仓库逐项
for r in zyaaa-ux/ROSA-Tuning wjie98/rosa_soft johanwind/wind_rosa x-0D/RASP KakaruHayate/RWKV8-ROSA-FPGA \
         xiaoiecc/qkv-rosa-fast-exact-backward Juste-Leo2/ROSA-GPU-RWKV8 aabbdev/rosa; do
  git ls-remote --symref "https://github.com/$r" HEAD | head -1
done

# AI 提交证据
git clone --filter=blob:none --no-checkout https://github.com/Alic-Li/rwkv_lightning_cuda /tmp/rlc
git -C /tmp/rlc log --format='%an' | sort | uniq -c | sort -rn | head
git -C /tmp/rlc log --author='Claude' --format='%h %ad %s' --date=short
```

> 采集时间：2026-11-06 09:47–10:05 CET。未消耗 GitHub API 配额。

---

## 7. 官方目录全量扫描：`rwkv.cn/eco/projects`（95 项）

数据源：`https://www.rwkv.cn/eco/projects.json`（页面通过客户端 `fetch("/api/projects")` 加载同一份数据），
`count=95`、`lastUpdated=2026-10-19`。全量条目已保存为
[`data/rwkv-cn-eco-projects-2026-11-06.tsv`](../data/rwkv-cn-eco-projects-2026-11-06.tsv)
（字段：owner / repo / name / category / created / updated / description）。

### 7.1 类别分布

| 类别 | 数量 |
|---|---|
| RWKV 推理框架 | 27 |
| 多模态项目 | 26 |
| 其他 RWKV 项目 | 13 |
| RWKV 微调/训练工具 | 12 |
| RWKV Agent 与运行时 | 7 |
| 聊天机器人/推理 API 服务器 | 5 |
| RWKV 基准测试 | 3 |
| 分词器 | 2 |

### 7.2 我们此前的覆盖

| 指标 | 数量 |
|---|---|
| 官方目录条目 | 95 |
| 已在 `tracking/repos.txt` 跟踪 | 12 |
| 在既有报告/文档中出现 | 16 |
| **两者都没有** | **79**（多模态 26 / 推理 23 / 其他 11 / 训练 7 / Agent 3 / 基准 3 / 聊天 API 4 / 分词器 2） |

多模态 26 项超出本项目范围（我们只做文本 agent/RL）；但**训练/Agent/基准层仍有 13 项缺口**，其中 6 项值得注意。

### 7.3 值得注意的新资产（均已单独核验）

| 仓库 | 最后提交 (UTC) | 许可证 | 是什么 / 对我们的意义 |
|---|---|---|---|
| `Nice0o0/stateswap` | 2026-10-25 | LICENSE ✅ | 把人格/任务模式训练成 MB 级初始状态 S0，冻结 RWKV-7 底座热切换；带状态混合、低秩/int8 压缩、多轮会话与评测工具 → **P1.5 适配方案候选**（state tuning，不是 RL） |
| `aierwiki/rwkvtune` | 2026-02-27 | LICENSE ✅ | 类 TRL 的 Trainer API（SFT + 偏好优化）→ SFT 预热接口参考；已停更 |
| `cgisky1980/rwkv-router` | 2026-10-12 | LICENSE ✅ | R0–R3 分层路由（本地 RWKV / 云端 API）→ 与训练无关 |
| `XingQiPan/rwkv-jev` | 2026-09-22 | LICENSE ✅ | 受限 softmax 的零生成决策引擎（Jev 式）→ agent 决策的替代思路 |
| `Jellyfish042/uncheatable_eval` | 2026-09-24 | **NONE** | 动态数据防泄漏评测 → 可参考指标，不能进公开仓 |
| `Jellyfish042/rwkv_mmlu` | 2025-11-27 | **NONE** | MMLU prompt 格式 → 无许可证 |
| `Ojiyumm/RULER_RWKV` | 2025-06-09 | **NONE** | RULER 长上下文 → 无许可证 |
| `RWKV/RWKV-infctx-trainer` | **2024-04-25** | LICENSE ✅ | 官方 org 的无限上下文训练器；**已严重过时** |

### 7.4 修正与审计发现

1. **owner 名纠正**：`Joluck/RWKV-PEFT` → **`JL-er/RWKV-PEFT`**（同一 HEAD `989d28dc6`，GitHub 重定向；官方目录用新名）。
2. **`Seikaijyu/RWKV-PEFT-Simple`**：无 LICENSE、最后提交 2025-05-30 → 不能作为 SFT 依赖。
3. **基准层 3/3 无许可证** → 与本文 §1 的"L5 许可断层"一致，且比此前描述的更糟。
4. **⚠️ 官方目录 `repo_updated_at` 不可信**：`RWKV/RWKV-infctx-trainer` 目录显示 `2026-09-04`，实际最后提交
   **2024-04-25**；`aierwiki/rwkvtune` 目录 `2026-08-28`，实际 `2026-02-27`。
   → **活跃度必须用 `commits.atom` 实测**，不能用目录字段；目录只作索引。
5. **官方组织不止 BlinkDL**：存在 `RWKV/` org（本目录收录其 infctx trainer）→ 应加入跟踪源。

### 7.5 对计划的结论

- **不改变执行路线**（仍 v7 + skyrl/vllm + G1l-1.5B）。
- **P1.5 增加一个候选**：若 LoRA/全参 SFT 预算不够，可试 `stateswap` 式 S0 state tuning（需自行复现，非 RL）。
- **评测清单缩窄**：3 个官方目录基准全部无许可证 → 仅本地参考；EvalScope-first 策略不变。
- **跟踪项**：`Nice0o0/stateswap`、`aierwiki/rwkvtune`、`RWKV/RWKV-infctx-trainer` 加入 `tracking/repos.txt`。

---

## 8. 补充核验：`irwkv`（原生 RWKV-7 服务框架）与 authorship 修正

> 采集时间 2026-11-06 10:58–11:02 CET。方法：`git ls-remote` / `commits.atom` / raw README/LICENSE / partial clone 作者统计 / `docs` grep。

### 8.1 事实

| 项 | 实测 |
|---|---|
| 仓库 | `w1c2j3/irwkv`（镜像）→ **`rwkv-org/irwkv`**（正式；13 commits；main 最后 **2026-11-02T08:36Z**） |
| 许可证 | **Apache-2.0** ✅ |
| 规模 | ~1,776 文件 / 30 MB（1,379 py + 268 rs），带 `tests/`、`docs/design`、`docs/usage` |
| 能力 | 原生 RWKV-7 循环推理 + 逐请求 state 管理 + chunked prefill + FlashRWKV2 融合算子 + CUDA Graph；OpenAI 兼容 API（Chat Completions + Responses）+ 结构化输出 + **tool calling**；单卡 / 两阶段流水线并行；可选 Rust 前端 |
| RL 接口 | `docs/design/model_runner_v2.md`：top-k / prompt logprobs 的省显存实现；`docs/usage/security.md`：RL weight updates / weight version 控制接口 |
| 分支活跃度 | `chase/rwkv-state-continuation` **2026-11-05T05:09Z**、`chase/rwkv-integration` 2026-11-05T03:24Z、`chase/prefix-cache` 10-30、`chase/context-compaction` 10-29 |

### 8.2 ⚠️ authorship 修正：irwkv 不是 Chase Jay 独写

部分流传的叙述把 `irwkv` 归为 "Chase Jay 一个人造" 的产品线之一。**实测提交记录不支持**：

| 仓库 | 作者统计 |
|---|---|
| `w1c2j3/irwkv`（镜像，5 commits） | J.L(Joluck) 2 · Cai-z-us/Caizus 3 · **Chase Jay 0** |
| `rwkv-org/irwkv`（正式，13 commits） | **Caizus 6 · Cai-z-us 4** · J.L 2 · Chase Jay 1 |

- 初始提交 `42cf7e2` 与主体实现 `dd82d66` 均由 **Cai-z-us / Caizus（张恺之，RL 负责人）** 提交。
- **Chase Jay 的实际贡献在分支**：`chase/rwkv-state-continuation`、`chase/prefix-cache`、`chase/context-compaction`——
  正是多轮 rollout 最需要的 state 续接/前缀缓存/上下文压缩，且 2026-11-05 仍在提交。
- 结论：**irwkv = 张恺之主导 + Joluck/Chase 协作**，与 `skyrl-rwkv` 同源团队；"四层基建全由 Chase 一人交付"的说法应修正为
  "**agent 运行时（RWKV-LH 323/323）与评测（helicopter 324/373）由 Chase 主导；推理/RL 由张恺之主导**"。

### 8.3 对计划的含义

1. **P3 推理侧出现真实候选**：irwkv 的 state continuation / prefix cache / logprob / weight-update 接口，正对"多轮 rollout 焊缝"的推理侧；
   但**与 skyrl 训练器的 weight sync、batch 语义、token-in-token-out 契约未验证** → 不是 drop-in。
2. **新增 P5 评估项（≤6 h）**：irwkv vs vllm-rwkv 对照；若通过，Plan B"最小 RL loop"的推理端优先用 irwkv。
3. **P0–P2 不变**：权重打通仍以 vllm-rwkv 为主（skyrl 已集成），irwkv 并行评估。
4. **bus factor 修正**：RL+推理层有张恺之/Joluck/Chase 三人；**agent/评测层仍是 Chase 单点**
   （helicopter 373 commits 中 324 为其独写；RWKV-LH 323/323 全为其独写——本次已复核）。

### 8.4 仍未验证

- irwkv 的 logprob 与 vllm-rwkv 是否数值一致（logprob parity）；
- irwkv 的 weight-update 是"权重版本热切换"还是"训练器增量同步"；
- `rwkv-org/irwkv` 与 `skyrl-rwkv` 的集成是否已有计划（两者同源团队，可能性不低，但没有公开证据）。

---

## 9. 补充核验：`rwkv-agent-eval` / `dsh-rwkv-plugin` —— 公开结果显示前的最后一块拼图

> 采集时间 2026-11-06 11:52–11:58 CET；方法同前（`git ls-remote`、`commits.atom`、raw LICENSE、shallow clone、README/grep）。

### 9.1 事实

| 项 | 实测 |
|---|---|
| `rwkv-org` 组织 | 新建（2026-10-27），公开仓库仅 **2 个**：`irwkv`、`rwkv-agent-eval` |
| `rwkv-org/rwkv-agent-eval` | HEAD `0e79fa4`；最后提交 **2026-11-06T08:34:41Z（当天）**；**无 LICENSE**；541 文件 / 17 MB |
| 评测形态 | Harbor + **Docker** task 目录；自有题 **3 个**；开源题 `datasets.lock.toml`；`bank/` 含题库转换/判分/自造题校验；逐 trial provenance（模型、插件、DSH 版本、task checksum、未提交 diff、每请求提示与输出） |
| 训练来源 | **私有** `rwkv-agent-pipeline` 的 `mix-20261106`（GitHub 404 核实）；依赖**未发布** DSH commit `dsh-8bd07339` |
| `No-22-Github/dsh-rwkv-plugin` | HEAD `0095c85`；最后提交 **2026-11-06T07:20:33Z**；**无 LICENSE**；55 文件；注册 RWKV-7 G1 为 DSH 模型提供方；后端 rwkv_lightning CUDA + iRWKV 续写接口；agent loop 移植自 RWKV-Agent Go harness（**XML 信封、8 个工具**、默认开思考、agent-fast 采样） |
| 可运行性 | Harbor + Docker；无 apptainer/singularity 支持；依赖未发布 DSH 源码 commit |

### 9.2 结论更新（重要）

此前本仓库的判断是"**agentic RL 训练仍是公开空白**"。现在需要更精确：

> **RWKV 的 agentic RL 训练管线已经在私有侧运行**（`rwkv-agent-pipeline` + `mix-20261106` 训练数据），
> 公开的评测框架（`rwkv-agent-eval`）当天仍在提交，**公开结果尚未发布**。
> **2026-11-07 更新：首批公开结果已发布（SFT/NoRA，非 RL）——见 §11。**
> 因此"空白"应限定为"**公开可复现的配方与结果**"，而不是"没人做"。

### 9.3 对计划的含义

1. **P0 不取消**：评测 ≠ 权重打通 + 训练环境 + RL 闭环；且无许可证、Docker 依赖、自有题仅 3 个、绑定私有数据与未发布 DSH commit。
2. **P4 采用"Harbor 兼容设计 + 自建题"**：借鉴 task 目录结构、主/子 Agent 角色、heldout/seen/自造划分与 provenance 记账；**不复制其题目内容**。
3. **P3 采纳其工具/提示格式作为参考**：8 个工具名、XML 信封、兜底策略，有利于未来与公开结果做"同格式对照"。
4. **跟踪**：`rwkv-org/rwkv-agent-eval`、`No-22-Github/dsh-rwkv-plugin` 加入每日跟踪；监控 `rwkv-agent-pipeline` 公开（重大信号）。
5. **风险 R12**：其评测依赖未发布 DSH commit `dsh-8bd07339` + 私有仓库 → 不可复现，我们不得依赖。

### 9.4 未验证 / 二手信息

- `dsh-rwkv-plugin` 的"8 个工具"仅从 README 确认，未逐行核对代码。
- Joluck 的 RLVR×PEFT 论文结论（DoRA/AdaLoRA/MiSS 优于标准 LoRA、PiSSA 谱坍塌）为二手信息，未独立核实；
  我们用全参 FSDP，不直接受影响。
- `mix-20261106` 数据规模/来源不可见（私有）。

---

## 10. 2026-11-07 追加核验：社区 state-native Agent runtime `rwkv-agent`（重要更新）

> 采集时间 2026-11-07 01:10 CET；来源 GitHub API + raw README（对外部内容只做事实摘录）。

### 10.1 事实

| 项 | 实测 |
|---|---|
| `123123213weqw/rwkv-agent` | 2026-07-19 创建；最后推送 **2026-11-01**；Python + Rust；**9★ / 3 forks**；**AGPL-3.0-or-later** |
| 自我描述 | **"RWKV State Agent — A local, state-native Agent runtime for RWKV models"**：跨轮复用 RWKV 循环状态、严格工具调用、**一个 GPU 调度器推进大量隔离 agent 状态**、bubblewrap 沙箱、HTTP/NDJSON API（`owner_id`/`session_id`/state 生命周期） |
| README 报告的数字（**作者自报，未独立复现**） | 单会话状态 **34,078,724 B（≈32.5 MiB）**，与历史长度无关；**31 会话 = 0.98 GiB，可放进 24 GB 卡**（同构 attention 约 31 GiB）；state 拷贝 3.8 ms；快照恒定 32.63 MiB；18K tokens 时 restore 比重算快 11.9×；100 会话下推理状态内存省 4.3×（对照 attention：49.5 MiB 固定 + 32 MiB/1K tokens） |
| 模型/后端 | RWKV-7 7.2B（HF recurrent sidecar）；NVIDIA CUDA / AMD ROCm；**没有 RL/训练接口**（无 logprobs 训练契约、无 weight sync、无 GRPO） |
| 关联仓库 | `123123213weqw/x-harness-rs`：跨平台 agent harness（Rust，durable loop/原生工具/沙箱/Tauri+Web），16★，**Apache-2.0**；`rwkv-rs/hf-adapter`：MIT，2026-07-06 创建（与作者 GitHub 账号同日），组织内仓库 |

### 10.2 对既有判断的修正

1. **此前**：本仓库 §9 判断"agentic RL 训练管线在私有侧"；并在早期笔记里说"缺少能消费 state-native 引擎的多 agent rollout 层"。
2. **修正**：**面向推理的 state-native 多会话 agent runtime 已经公开存在**（`rwkv-agent`），且给出了量化的状态内存优势。仍然缺失的是
   **把它接进 RL 训练回路**的那一层：逐轮 loss mask / per-token logprob / 权重同步 / GRPO-DAPO 批语义。
   `skyrl-rwkv` 已覆盖 HF+vLLM 路径；`rwkv-agent` 是**服务侧**参考，不是训练侧 drop-in。
3. 因此"空白"的准确表述应为：**公开可复现的、带训练回路的 RWKV agentic RL 配方与结果**。

### 10.3 对计划的影响（详见 `private/plan-research/PLAN-v8-addendum-2026-11-07.md`）

- **P0/P1/P2：不变**（环境、权重、单轮 RL 门禁与它无关）。
- **P3：参考实现增至 4 个**：irwkv、Chase 的 RWKV-LH、No-22 的 dsh-rwkv-plugin、**rwkv-agent（新增，最贴近多会话 rollout 需求）**。
  可借鉴的设计（只借思路）：state pool + 统一 ready 队列、state 快照/恢复做分支与断点、严格单信封工具协议 + 控制器校验、
  `owner/session/state` 三级生命周期。
- **P4：新增 Apache-2.0 设计参考** `x-harness-rs`（工具循环/沙箱/持久化），我们自建，不复制。
- **P5：可新增一项"状态内存扩展性"对照**（会话数 vs 显存），引用其公开数字时明确标注"作者自报"。
- **许可证红线**：`rwkv-agent` 为 **AGPL-3.0-or-later** → **只做设计参考，不拷贝代码、不链接**；`x-harness-rs` 为 Apache-2.0，如需拷贝须保留 NOTICE。

### 10.4 未验证 / 风险

- README 数字未独立复现（无第三方引用、无 benchmark 日志可核）；引用一律标注 author-reported。
- 作者身份/组织关系（与元始智能、rwkv-rs 的关系）**仅有公开提交痕迹**，不做事实断言；本仓库不收录个人身份推测。

---

## 11. 2026-11-07 首批公开多轮 agent 评测结果（`rwkv-org/rwkv-agent-eval`）

> 采集 2026-11-07 10:40 CET；来源：`docs/reports/attribution-20261107.md`（raw，14 KB）+ 仓库 API。以下数字均引自该公开报告，**非本仓库复现**。

### 11.1 事实

| 项 | 值 |
|---|---|
| 基模 | `rwkv7-g1l-7.2b-20261031-ctx34304` |
| adapter | `g1l-nora-r16-lr2e-5-e2`：**NoRA r16，lr 2e-5，2 epochs，在 `mix-20261106` 上 SFT**（**不是 RL**） |
| 题库 | **1019 题** = 首版 435 + 留出补 135 + 第二轮自造 449；每题每模型 2 次；同题配对差 ±95% CI |
| **总分** | **30.9% → 52.8%，+21.9 ±3.2 pp**；**12 个能力块全部上涨** |
| 最大涨幅 | 网页+本地 **+56.2**（3.5→59.7）、代码修复 **+36.3**（15.3→51.6）、网页+代码 **+24.0**、搜索问答 +16.8、查找阅读·本地 +20.0 |
| 泛化 | 留出 951 题 **+22.1±3.3**；已训回测 28 题 +28.6±21.6；开源 humanevalfix 40 题 +12.5 → 不是记题 |
| 涨分机制 | **"学会按题面调对工具"，不是更会推理**：网页题打开网页比例 **~35%→~99%**；代码修复不调工具 **19%→0%**；工具报错率 **22%→8%**；改测试文件 39→8 次 |
| 剩余失败 | 绝大多数是"做了但做错"（测试没过/答案错），这一类基本没减少 |
| 数据量 vs 涨幅 | 26 个领域 Spearman ρ≈0.40（中等相关）；数据少的领域也普遍涨 → 工具习惯可跨领域迁移 |
| 三个新坏习惯 | ① 改完文件重复 read 核对 → 撞插件重复调用保护 → "没能整理成答案"收尾（245 次收尾中 104 次）；② 在 `<think>` 里逐行抄日志手工计数（单步 7000–9000 字符，统计块 19 次超时）；③ 能答就不搜（搜索失败 69% 未调 `web_search`） |
| 难题分析 | 两边都 0 分的 327 题：Codex 评难度 easy 243 / medium 84 / hard 1 → **题不难，是习惯不对** |
| 最大单一问题 | **插件侧**：`dsh-rwkv-plugin` 的 `gateToolCall` 重复调用保护在文件被 edit/write 后不重置，拦掉了 472 次合理的"改完复检" |
| 工程口径 | adapter 推理慢约 4.5×，评测用 5 倍时限；单轮评测 4–5 小时；环境报错重跑成功 |

### 11.2 对既有判断的修正

| 原判断 | 现状 |
|---|---|
| "RWKV 没有 agent 评测成绩" | ❌ **推翻**：1019 题、配对 ±95% CI、+21.9pp 的公开成绩 |
| "多轮 agent 能力没有模型证据" | ❌ **推翻**：7.2B + NoRA SFT 达到 52.8% |
| "没有 agentic RL" | ✅ **仍成立**：公开成绩全部来自 SFT（teacher 轨迹），无 RL 阶段结果 |

### 11.3 方法与可复现性评价

- 方法明显高于多数工业界 agent eval 报告：同题配对差 + 95% CI、留出/已训/开源三档泛化、12 能力块拆分、Codex 逐题归因（17 批 × 16 归因码）、机械 trace 统计、判据自审（R2/R3/R4 偏差方向与影响）、超时口径披露。
- **可复现性仍受限**：仓库**无 LICENSE**；评测依赖 Harbor + Docker；adapter 与 `mix-20261106` 数据在私有 `rwkv-agent-pipeline`，**不可下载**。→ 只能作为"公开证据"引用，不能作为可复现基线。
- 我们的 P4 应**借鉴方法而非复制内容**：配对差 + CI、三档泛化、能力块、trace 机械统计、归因码、判据自审；题库自建（Harbor 兼容格式）。

> 方法与失败模式的详细评述见 [`reports/2026-11-07-agent-eval-methodology-review.md`](2026-11-07-agent-eval-methodology-review.md)。

### 11.4 对本仓库计划的影响（详见 `private/plan-research/PLAN-v8-addendum-2026-11-07.md`）

1. **P1.5（SFT 基座）证据强化 → 建议前移**：外部结果说明 agent 能力主要来自 **SFT 阶段学会调工具**（RL 未参与）。我们应把 P1.5（SFT/NoRA 基座）放在 P2 多轮 RL 之前，而不是之后。
2. **P3 环境设计加入 5 条硬约束**（来自其失败数据）：改后复检要允许（重复调用保护在 write 后重置）；思考长度预算 + 强制用工具计数；题面要求搜必搜（+ 不该搜的对照样本）；"做不到"零工具直答（+ 需先查的对照）；不改测试文件。另需为 `web_search`/终端/browser 类工具准备训练样本。
3. **NoRA 选项**：其 adapter 用 NoRA r16，显存/优化器压力小（也缓解我们 `wake_up` OOM）；skyrl-rwkv 已支持 `USE_NORA=true`，可作为快速实验配置。
4. **P4/G7 报告模板**：采用其配对差 + CI + 三档泛化 + 能力块 + trace 统计的格式。
5. **P5 定位更新**：现有公开成绩是 SFT/7.2B/私有数据；我们的差异化是 **公开可复现的 RL（GRPO/FlashREINFORCE）配方与结果（1.5B，~140 A100 小时）**，并报告 SFT vs SFT+RL 对照。
6. **P0–P2 与预算不变**；门禁不变；下一个观察点 = 是否出现 RL 阶段成绩。

### 11.5 未验证

- 报告数字未由本仓库独立复现；判据实现（`bank/judge.py`）未审阅。
- 作者/团队与 `mix-20261106` 数据来源不可见。
