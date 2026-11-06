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
