# RWKV 生态核验报告（2026-11-05 接续 session）

> 任务：接续 `内部交接 2026-11-05（未公开存档）` 的「生态核验 / 跟踪」线，复核交接中的未验证项与事实、产出可引用的 delta。
> 方法：3 名 teammate 并行深挖（`reports/skyrl/`、`reports/state/`、`reports/eco/`）+ Lead 抽验承重事实。
> 证据：每个结论都可在同目录报告 / `reports/*/evidence/` / `tracking/runs/` 中回查；时间均为 2026-11-05（CET/UTC 标注）。
> 公开版政策：第三方全文/HTML/ATOM 已移除，保留报告 + 命令输出 + 结构化数据；被移除原件以 sha256 记录（`reports/EVIDENCE.md`）。
> GitHub API 用量：全队合计 **2 次**（60/h 限额内的 3%）；其余全部走零配额路径（`git ls-remote` / `commits.atom` / `raw.githubusercontent.com` / org HTML embedded JSON / HF API）。

---

## 0. 一句话结论（相对交接的 delta）

**交接的核心判断「单轮 RLVR 成熟、多轮 agentic RL 是空白」仍然成立，但它的三条支撑事实需要大幅修订**：
1. **生态图严重不全**：`rwkv-rs` 组织实为 **40 个公开仓库**，交接完全未提 **30 个** —— 漏掉的是整层（verl 原生 RL 集成、torchtitan 训练栈、评测生产体系、量化、Rust 全栈）。
2. **「没有模型、没有评测成绩」已被部分推翻**：生态外 `No-22-Github/RWKV-Agent` 有公开 568 题多步 agent 考卷 + 公开跑分（G1l 基模 187/568=32.9%，NoRA 适配器 320.5/568=56.4%）；`rwkv-rs/browsecomp-plus-eval` 是 830 题 BrowseComp-Plus 的完整评测复现包（无分数）。
3. **「官方主动不做 agentic」的表述已过时**：G1l（2026-10-31）官方 chat template 已支持 tool-call/multi-turn，官方文档与 README 主动指向 agent 目录 —— 准确说法是「**官方不做 agentic RL 训练，但已把 agentic 接口官方化、把实践外包给社区**」。

**仍然为真的空白**：公开的**多轮 agentic RL 训练配方与结果**（现有 agent 模型全是 SFT/NoRA/MiSS 适配器，不是 RL）；标准 benchmark（BrowseComp-Plus 830 / τ-bench / BFCL）的 RWKV 公开分数；state-native 多轮 rollout 层。

**交接文档里 6 处事实错误已定位并修正**（§10.1 五项全部有裁定，见 §1/§2）；剩余真正未验证的只有「真机 8 卡跑通」与「28B 长跑/收敛」两项。

---

## 1. §10.1 五项未验证事项 —— 逐条裁定

| # | 交接原文 | 裁定 | 事实 | 证据 |
|---|---|---|---|---|
| 1 | `skyrl-rwkv` 在真实 8 卡上能否跑通（依赖 pin 死的**私有** vLLM fork；无 CI） | ⚠️ **仍未实测；且"原样跑不通"由静态证据确认** | ① pin 不在私有 fork：实际 `rwkv-rs/vllm-rwkv@2852a7b1d`（`pyproject.toml:584`、`uv.lock:10591`），是公开仓库、HEAD `7a6adcc6` 的祖先（落后 2 提交）；交接的 `67f0c599` 是 2026-08-04 旧提交、**不在** rwkv 分支历史。② CI 缺失属实，但根因是 fork 继承的 **16/16 个 workflow 全部**带 `github.repository == 'NovaSky-AI/SkyRL'` 门禁 → fork 内无任何 CI（不只是 RWKV 单测）。③ 软件可装证据充分（依赖全公开、5 条 launcher 都有 `--test_mode`）；但默认配方是**单节点 8×96GB Pro6000**，`examples/train/rwkv/eval/run.sh:11-12` 硬性 `NUM_GPUS==8` → Snellius 单节点只有 4×A100 80GB / 4×H100，**不能原样跑**；集群 CUDA module 最高 12.9.1 vs 仓库 cu130，FlashRWKV2 预编译需真机验证 | `reports/skyrl/REPORT.md` §2.1–2.7；Lead 抽验：`pyproject.toml:584`、`grep -l` 16/16、`eval/run.sh:11` |
| 2 | `wkvm` 的 RWKV-7 durable-state 引擎真实性能（"README 只给了 Gemma 路径的完整数字"） | ❌ **交接说法错误** | RWKV-7 数字在仓库里是完整的：`experiments/results/m2_engine_bench.md`（1.5B **8,077 tok/s @B256**；191M 38,856 tok/s）、`m3_results.md`（2,000 会话 / 2.29 MiB / p50 8.2ms / 64-way fork / 16-16 续接）、`bench_albatross_2.9b.log`；`paper/CLAIMS.md` 是 claim-SHA256-commit 台账。**需加限定**：p99 9.5ms 被作者 claim 台账明确排除（单次运行、KO 页缓存未清）；8,077 tok/s 是单次 64-step 计时；缺的是**独立复现**，不是数字。另：**`live-migrate` 并未实现**（`wkvm/server.py` 只有 `/v1/states` create/get/fork/mutate/persist/delete + `/v1/generate`；ROADMAP 把 migration 列入 *Deferred*)；main 冻结于论文发布（2026-08-02），但 `m4-qwen35-hybrid` 分支活到 **2026-09-10** | `reports/state/REPORT.md` §1 任务 1；Lead 抽验：`wkvm/server.py:1-14` 端点清单、`docs/ANGLE.md:142` 仅有 roadmap 措辞、`experiments/results/` 文件存在 |
| 3 | `RWKV-Megatron` 的 `codex/rwkv28b-distill` 是否有 28B 真实训练 | ⚠️ **存在（部分被证明），但不是"被证明"** | 分支真名 **`codex/qwen-rwkv28b-distill`**（交接名字错），HEAD 2026-10-30。有 28B 证据：3 个 28B 蒸馏配置（88 层/hidden 5120/80 heads）+ capacity probe（自述 30 步、峰值 75,063 MiB、2.513 s/step）；更硬的在 `codex/rwkv7-cp` 分支：**4 种 28B 布局 × 30 步 + 固定验证**的机器可读 JSON（TP4/PP2/CP1：75,829 MiB、2.0712 s/step、final val CE **7.497223**、无 NaN/skip/OOM）。但：probe 脚本自述 "does not save checkpoints or certify model quality"；distill 分支 `docs/`/`training-smoke/` 被 `.gitignore`（0 文件入库）；组织内唯一 12h 长跑是 **2.7B，不是 28B**；28B TP grad-norm 分叉 28.42% 未修。→ **规模化路径：存在 ✅ + 工程可行性部分证明 ⚠️；训练有效性/收敛 ❌ 无证据** | `reports/state/REPORT.md` §1 任务 2；Lead 抽验：分支列表、28B 配置/证据文件存在 |
| 4 | `rwkv-rs/Helicopter`（scoreboard 仓库）是否存在（当前 404） | ✅ **公开不存在（维持原判）**；⚠️ **但它是"未公开的内部项目"，不是"不存在的东西"** | 多路复验全 404：repo 页、`.atom`、raw README、未认证 API、org 30 仓列表、Codeberg、HuggingFace 均无。但公开代码里已有它的契约：① `rwkv-skills` README 第 8 行 "The public scoreboard is maintained separately in the **Helicopter** repository"；② `skyrl-rwkv` 分支 `feat/heli-r00-training-eval`（8 commits，2026-10-24→28，"+516/−48"）的 README 有 **`python -m helicopter checkpoint-result <spec> train`** 回调；③ `rwkv-skills` 仓库内有 dashboard 前后端代码与 `SCOREBOARD_API_BASE_URL`。→ 结论：Helicopter 是内部/私有 scoreboard，公开仓库不存在，但**训练→评测回调契约已进入公开分支**；公开侧仍无成绩数据 | `reports/state/REPORT.md` §1 任务 3；`reports/skyrl/REPORT.md` §2.6；Lead 抽验：heli 分支 README 第 79 行 `python -m helicopter checkpoint-result` |
| 5 | 官方是否会把 DAPO 之外的新算法（TLPO）并入 `skyrl-rwkv` | ⚠️ **未并入（0 命中），但"算法文件数"口径不可复现；官方路径另有动作** | `skyrl-rwkv` main 中 `tlpo` 0 命中；Anti-Doom/FTPO 在（`antidoom` 14 文件）。交接的"算法文件数"（grpo 191 / dapo 87 / cispo 17 …）用常规口径无法复现（实测 221/104/20/21/20/34/14/9/0）。**更重要的是**：生态中已出现独立 `antidoom-rwkv` 仓库（Antidoom/FTPO 去复读工具，2026-07-07 后停），且 `verl-rwkv` 早已实现 RWKV7 GRPO/MaxRL —— 算法生态不是"只有 skyrl 一条线" | `reports/skyrl/REPORT.md` §2.5；`reports/eco/REPORT.md` §2 |

---

## 2. 交接文档需要修订的 12 处（可直接照改）

| # | 位置 | 交接原文 | 应改为（2026-11-05 实测） | 证据 |
|---|---|---|---|---|
| 1 | §0 | "没有模型、没有评测成绩、没有 rollout 基础设施" | **部分推翻**：有公开 agent 适配器模型（State/MiSS/NoRA）与公开跑分（No-22 568 题考卷，32.9%→56.4%）；有评测包（browsecomp-plus-eval 830 题）与 scoreboard 管线；**仍空白的是**多轮 agentic RL 训练配方/结果 + 标准 benchmark 公开分数 + state-native rollout 层 | `reports/eco/REPORT.md` §1 A/H |
| 2 | §0 | "这是官方主动选择的路线，不是遗漏" | 改为：**官方不做 agentic RL 训练，但已把 agentic 接口官方化**（G1l 2026-10-31：chat template 多轮 + strict tool-call；官方模板含 function-call；官方 README/hub 卡指向 agent 目录）；rwkv_lightning 教程明确说"真实 Agent RL 要自己执行工具" | `reports/eco/REPORT.md` §1 B；Lead 抽验：`reports/eco/evidence/09-official/rwkv.cn-promptformat-excerpts.md` |
| 3 | §1.2 | 两目录 + Awesome 三份清单，漏项是"零散条目的通用基建" | **规模低估**：rwkv-rs 组织 = **40 个公开仓库**（17 源 + 21 fork + 2 archived），交接未提 **30 个**；漏的是整层（训练/评测/量化/Rust 全栈） | `reports/eco/REPORT.md` §2；`data/eco-org-repos.txt` |
| 4 | §2/§3 | 训练层"五条路线"，`skyrl-rwkv` 是唯一/最优 RL 基座 | 训练路线不止五条，且 RL 基座有 **两代**：`verl-rwkv`（fork verl，native `rwkv_lm` engine + GRPO/MaxRL，43 RWKV 文件/18 PR，2026-05-21 建、**2026-08-02 停更**）→ `skyrl-rwkv`（2026-08-30 建、10-31 活跃，同一主力 `Cai-z-us`）；`skyrl` 是"当前活跃/推荐基座"而非"唯一/最优" | `reports/eco/REPORT.md` §1 E；`reports/skyrl/REPORT.md` §2.8 |
| 5 | §3 | 绑私有 vLLM fork `rwkv-rs/vllm-rwkv@67f0c599` | pin 实为 **`2852a7b1d`**（公开仓库、HEAD 祖先、落后 2 提交）；`67f0c599` 是 2026-08-04 旧提交不在历史 | `reports/skyrl/REPORT.md` §2.2 |
| 6 | §3 | "3,354 行 RWKV 单测存在但不在 CI" | 行数对（790+788+1087+689），但根因是 **fork 继承的 16/16 workflow 全带上游 repo 门禁** → fork 内整体无 CI | `reports/skyrl/REPORT.md` §2.3 |
| 7 | §3 | "8 卡可跑（缺 CI/pin 私有）" | 软件**可装**（依赖全公开），但默认配方 = **单节点 8×96GB Pro6000**；`eval/run.sh:11-12` 硬性 `NUM_GPUS==8`；Snellius 单节点仅 4×A100/H100 → **原样不能跑**；CUDA cu130 vs 集群 module 12.9.1 需真机验证 | `reports/skyrl/REPORT.md` §2.7 |
| 8 | §4.1 | `wkvm` 支持 live-migrate | **未实现**（server 无 migrate 端点；ROADMAP 列为 Deferred/refused） | `reports/state/REPORT.md` §1.6 |
| 9 | §10.1#2 | wkvm README 只给了 Gemma 数字 | RWKV-7 数字完整（m2/m3/CLAIMS.md）；但需引用限定（p99 被作者排除、单次计时、无独立复现） | `reports/state/REPORT.md` §1.4 |
| 10 | §10.1#3 / §2 | Megatron 分支名 `codex/rwkv28b-distill` | 真名 `codex/qwen-rwkv28b-distill`；28B = 短跑容量验证，非收敛证明；默认分支已变 `muon`（2026-07-06 停），`codex/rwkv7-cp` 活跃到 10-22 | `reports/state/REPORT.md` §1 任务 2 |
| 11 | §7 | "唯一支持多轮的 SFT 是 howard-hou/RWKV-SFT" | **已不完整**：No-22 用自建 8,846 行 agent 轨迹 + `rwkv_lightning_cuda` 的 NoRA 多轮 SFT 训出公开适配器；skyrl 代码本身支持多轮 | `reports/eco/REPORT.md` §1 G |
| 12 | §7/§8 | `FlashRWKV2` 归属 BlinkDL；`RWKV-LH` 停 10-08 等 | FlashRWKV2 已迁 **`rwkv-rs/FlashRWKV2`**（MIT，BlinkDL 路径 404）；`RWKV-LH` main 停 10-08 但侧分支活跃到 11-03；`RWKV-Megatron` 默认分支 `muon`；`wx-cli` 列在 org 但 repo 404 | `reports/eco/REPORT.md` §2；`tracking/runs/2026-11-05T200900Z.md` |

---

## 3. 新发现的生态资产（交接未提 / 判断可用性）

> 资格线：**公开可核验** + 与 RL/agentic 方向相关。完整 40 仓见 `data/eco-org-repos.txt` / `reports/eco/REPORT.md` §2。

| 资产 | 是什么 | 活跃度 / 许可 | 对交接判断的影响 |
|---|---|---|---|
| `rwkv-rs/verl-rwkv` | fork `verl-project/verl`：native `rwkv_lm` engine（EngineRegistry）+ RWKV7 GRPO launcher + MaxRL 入口 + 每日 upstream rebase；43 个 RWKV 文件、18 个 PR | 2026-05-21 建，**2026-08-02 停更**；Apache-2.0 | 推翻"skyrl 是唯一/最早 RL 集成"；"停更后换乘 skyrl"是重要历史信号 |
| `rwkv-rs/torchtitan-rwkv` | fork pytorch/torchtitan：first-class RWKV-7 训练（`torchtitan/models/rwkv7/` RWKVTrainer + FlashRWKV2）+ state tuning 实验 | **2026-10-31 活跃**；BSD-3 | 训练栈又多一条（PyTorch 原生），交接 §8 未画 |
| `rwkv-rs/Megatrwkv-Bridge` | fork NVIDIA-NeMo/Megatron-Bridge：Megatron+RWKV 桥孵化位 | **2026-11-02 新建**；Apache-2.0，尚无 RWKV 代码 | 与 Megatron 28B 线配套，值得跟踪 |
| `rwkv-rs/browsecomp-plus-eval` | **830 题 BrowseComp-Plus 完整 RWKV agent 评测复现包**：search(top5)/get_document/final_answer 100 步循环、3 路候选、vendored vLLM-RWKV、官方 judge | 2026-07-21 抽取后未更新；**无 LICENSE、无 scores** | 推翻"agentic 评测空白"→ 降级为"有可复现评测包、无公开分数"；但**无许可 = 不可商用** |
| `No-22-Github/RWKV-Agent`（生态外） | **公开 568 题多步 agent 考卷**（15 场景、每题 verify.py）+ 公开跑分：G1l 基模 **187/568=32.9%**，NoRA v2.3 **320.5/568=56.4%**（p=2e-24）+ 公开适配器权重（HF `No-22/rwkv-agent-weights`）与训练数据 | 2026-10/11 活跃；**无 LICENSE** | 直接推翻"没有模型/没有评测成绩"；但也说明现有能力来自 **SFT/NoRA**，非 RL |
| `rwkv-rs/antidoom-rwkv` / `fla-rwkv` / `any2rwkv` / `llm-compressor-rwkv` | Anti-Doom/FTPO 工具；RWKV7 FLA kernel（MIT）；attention→RWKV 架构转换研究；RWKV7 量化 | 07-07 / 08-06 / 10-31 / 07-31；前两者 Apache、fla MIT | 补齐 L1/L2 层；`any2rwkv` 是新的"混合架构"路线 |
| `rwkv-rs/rwkv-skills` 的 scoreboard 管线 | README 引用 Helicopter；仓库内有 Next.js dashboard + FastAPI API + `SCOREBOARD_API_BASE_URL`；`lm-eval-rwkv` 有 "Evaluation Producer Contract" + 9 条 `codex/rwkv-*` 分支 | 2026-08-09 后停；**无 LICENSE** | 评测生产体系比交接描述成熟，但**公开成绩仍缺** |

---

## 4. 更新后的结论（建议直接替换交接 §0/§5）

### 4.1 §0 建议版本

> RWKV 的**单轮 RLVR 已成熟且有官方组织**（DAPO 配方、skyrl-rwkv、异步 RLVR 基建）；
> **多轮 agentic RL 训练仍是公开空白**（无公开配方、无公开训练结果、state-native rollout 层仍需自建）。
> 但 **agentic 能力/评测本身已不再空白**：官方 G1l（2026-10-31）已官方化 tool-call/multi-turn 提示接口并把 agentic 实践入口指向社区；
> 社区已有公开的 568 题多步 agent 考卷与跑分（No-22：G1l 基模 32.9% → NoRA 适配器 56.4%）、830 题 BrowseComp-Plus 评测复现包（无分数）。
> 因此工作量重心从"从零建评测"下调为"**接公开评测 + 自建多轮 rollout/RL**"。

### 4.2 §5 建议版本

把"评测层：有框架，几乎没成绩"改为：
> **评测已工业化**（lm-eval/lighteval/evalscope 三个 fork + scoreboard 发布管线 + 16 benchmark 计划，其中 `agentic = []` 为空类目），
> **但公开的标准 agentic 成绩仍缺**；唯一公开的 agentic 成绩来自生态外自建 568 题考卷（No-22，无许可证）。

### 4.3 §9 路线图影响（最小改动）

- **P0（自建 32 题评测）**：可复用 No-22 的 568 题考卷格式 + `browsecomp-plus-eval` 的 agent loop，把 3 周压缩；
- **P2（单轮 RLVR）**：不变，仍用 skyrl-rwkv + DAPO；但可参考 `verl-rwkv` 的 `rwkv_lm` engine 设计；
- **P3（多轮 rollout）**：不变，仍是生态空白；`heli` 分支只覆盖"训练→评测回调"，不是 rollout 层。
- 新增跟踪项：`torchtitan-rwkv`（训练栈）、`Megatrwkv-Bridge`（Megatron 桥）、`any2rwkv`（架构转换）、G1l 之后的官方 tool-call 生态。

---

## 5. 仍未验证 / 需要下一轮的事项

| 事项 | 现状 | 建议动作 |
|---|---|---|
| `skyrl-rwkv` 真机跑通 | 静态：可装但**原样不能跑**（8×96GB Pro6000 配方 + NUM_GPUS==8 + cu130 vs 12.9.1） | 需在 8 卡 A100/H100 上改 `NUM_GPUS`/多节点或容器化 cu130；先跑 5 条 launcher 的 `--test_mode` |
| 28B 长跑/收敛 | 只有 30 步容量验证与 2.7B 的 12h 长跑 | 向 `codex/qwen-rwkv28b-distill` 作者确认是否有 28B 长跑/权重；或自建 |
| Helicopter 本体 | 公开 404；契约出现在 skyrl heli 分支与 rwkv-skills | 关注 `feat/heli-r00-training-eval` 是否合并 main、是否发布 scoreboard 数据 |
| 标准 benchmark 分数 | BrowseComp-Plus 830 题包无 scores；τ-bench/BFCL 无 RWKV 数字 | 用该包跑 G1l/NoRA 基线，产出第一份公开分数（无硬件也能先搭 judge） |
| `No-22` 资产许可 | 考卷/权重/数据均无 LICENSE | 不可商用；需自行重写评测或取得授权 |
| TLPO 并入 | skyrl main 0 命中 | 跟踪官方后续提交 / 公众号 |
| 官方 G1l 之后的 agentic 动作 | 10-31 起接口官方化 | 跟踪 rwkv.cn / HF / RWKV-LM README 变化（已入 `tracking/sources.md` 信号 7） |

---

## 6. 本轮交付物与可复跑入口

| 交付物 | 说明 |
|---|---|
| `tracking/sources.md` | 三层信息源 / 8 项信号 / 失真登记 / 每轮复查清单 |
| `tracking/repos.txt` | 35 个跟踪仓库（rwkv-rs 组织全量 + 关键外部仓库），**零 API 配额** |
| `tracking/check.sh` | 快照脚本：`bash tracking/check.sh [--diff] [--deep]`；输出 `tracking/runs/<UTC>.md/.tsv` |
| `tracking/runs/2026-11-05T200900Z.*` | 首轮快照（35 仓：HEAD/最后提交/许可/分支数/stars/描述） |
| `docs/ecosystem-review-2026-11-05.md` | 公开版生态综述（中性表述） |
| `reports/EVIDENCE.md` | 证据政策 / 归档 sha256 / 复抓方法 |
| `reports/skyrl/REPORT.md` | skyrl-rwkv 深度核验（241 行 + 15 件证据，全部保留） |
| `reports/state/REPORT.md` | wkvm / Megatron 28B / Helicopter（363 行 + 35 件证据 + 3 件归档） |
| `reports/eco/REPORT.md` | rwkv-rs 40 仓全量 + 新信号 + 官方渠道（384 行 + 33 件证据 + 194 件归档） |
| `data/eco-org-repos.txt` | 40 仓库全量清单（kind/license/created/last commit/交接覆盖） |
| `内部交接 2026-11-05（未公开存档）` | 交接原文基线（本报告相对它给出 delta；公开综述见 `docs/ecosystem-review-2026-11-05.md`） |

### 复跑命令

```bash
cd ~/AlchemyRepos/RWKV-AgenticLearning
bash tracking/check.sh --diff          # 下一轮：与 2026-11-05 快照对比，打印变化
```

关键证据回查示例：
```bash
grep -n '2852a7b1d' repos/skyrl-rwkv/pyproject.toml          # skyrl pin 真相
sed -n '1,20p' repos/wkvm/wkvm/server.py                     # wkvm 端点（无 migrate）
sed -n '9,13p' repos/skyrl-rwkv/examples/train/rwkv/eval/run.sh  # NUM_GPUS==8 硬门禁
```

---

## 7. 增量更新（2026-11-06）

本报告发布后 24 小时内的新证据（helicopter 仓库定位、v8/ROSA 前沿层、贡献者活跃度分层、AI 提交信号）
见 [`2026-11-06-ecosystem-update.md`](2026-11-06-ecosystem-update.md)。
