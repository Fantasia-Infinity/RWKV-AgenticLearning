# skyrl-rwkv 深度核验报告（任务 task-1）

> 核验时间：2026-11-05 21:08–21:26 CET（20:08–20:26 UTC）
> 主机：Snellius login node（Snellius 登录节点），工作区 `~/AlchemyRepos/RWKV-AgenticLearning/`
> 对象：`rwkv-rs/skyrl-rwkv`（main @ `04a5c985`，heli 分支 @ `785a231a`）+ `rwkv-rs/vllm-rwkv`（rwkv @ `7a6adcc6`）
> 方法：只读静态核验。clone 用 `--filter=blob:none`（完整提交历史，blob 按需拉取）；未安装依赖、未跑 GPU/SLURM 作业；GitHub API 仅用 **1 次**（配额 4 次上限内），其余用 `git ls-remote` / `curl` / 网页。
> 原始证据（命令 + 输出 + 时间戳）：`reports/skyrl/evidence/`（见 §5 索引）。


> **公开版说明（2026-11-05）**：为符合公开发布政策，第三方全文/HTML/ATOM 已从本仓库移除（原始文件 sha256 见 `evidence/ARCHIVED.tsv` 与 `evidence/CITATIONS.md`，可按其中的 URL 重新抓取）。保留的命令输出与结构化数据可直接查看；正文引用中已移除的文件名仍保留，用于追溯当时证据。

---

## §1 结论摘要表（逐条对应任务清单 1–8）

| # | 核验项 | 结论 | 一句话结论（证据见 §2） |
|---|---|---|---|
| 1 | clone 两仓 + 分支基线 | ✅ | 与交接基线完全一致：skyrl main `04a5c9856830e0862eb33b67f6d8924e33aaceee`（2026-10-31T10:47:56Z）、heli `785a231aa346ff2920df10af303bf2cd403ea9eb`（2026-10-28T08:54:46Z）；vllm-rwkv 单分支 rwkv `7a6adcc6a02482552a426c64f5e68da061043a05`（2026-10-31T10:56:01Z）。分支仅 main + feat/heli-r00-training-eval。 |
| 2 | CI 真相 + 3,354 行单测 | ⚠️ | 行数 **精确成立**：4 个 RWKV 测试文件共 **3,354 行**（790+788+1087+689）。但“不在 CI”的**真正原因**比交接更严重：fork 继承上游 16 个 workflow，**全部**带 `if: github.repository == 'NovaSky-AI/SkyRL'` 门禁 → **fork 里 CI 整体不运行**（不止 RWKV 测试）；`.github/`、`ci/` 全目录 grep `rwkv` 为 0 命中；fork 相对 merge-base 只加了 `.github/CODEOWNERS`，没动任何 CI。 |
| 3 | vLLM fork pin | ❌ | 交接的 `67f0c599` **不是当前 pin**。当前 pin（main 与 heli 两分支相同）= **`rwkv-rs/vllm-rwkv@2852a7b1d597f6e2131ec801de331b886471cd95`**（`pyproject.toml:584`、`uv.lock:10591/10830/12347`）。该 pin 是 rwkv 分支 HEAD 的**祖先，落后 HEAD 2 个提交**（2026-10-26 → 2026-10-31）。`67f0c5996c50dca0ad779da545cb491527de988f` 确实存在于 vllm-rwkv 对象库（2026-08-04 的旧提交，页面提及 `mr-1` 分支），但**不在 rwkv 分支历史里**（`rev-list --all` 无此号，非 HEAD 祖先），不可能是当前 pin。**“私有”也不成立：两仓均公开可 clone（无凭证）**。 |
| 4 | 多轮 / max_turns / loss_mask / skyrl-agent | ✅（细节需补） | `max_turns` 默认 **1**（`skyrl/train/config/config.py:1586`），`examples/train/rwkv/` 全目录 **0 处设置** → 实际单轮，交接说法成立。但补充两点：①`use_conversation_multi_turn` **默认就是 True**（`config.py:1599`），且 `sao/run.sh:131` 显式 `=true`（并非“代码里有但默认没开”）；②`loss_mask` 明确区分 assistant/observation（`skyrl_gym_generator.py:125-144` 注释原文 “Observation tokens are always masked out”），`RWKVTrajectoryLogger` 记录 `num_turns`/`assistant_spans`/`loss_mask`（`skyrl/train/utils/rwkv_trajectory_logging.py:34-37`）；③`skyrl-agent/` 对 RWKV **0 引用**（grep 空）。 |
| 5 | TLPO + 算法/launcher | ✅（tlpo）/⚠️（文件数） | `tlpo`/`TLPO` **全仓 0 命中**，§3“tlpo 0”✅。5 条 launcher 目录齐全（`antidoom/flashreinforce/opd/sao/sft`），`antidoom` README 标题即 “**RWKV Antidoom / FTPO**”，`ftpo_loss`/`extract_ftpo_pair`/`regularise_ftpo_rows` 在 `antidoom/train.py:547,590,653` ✅。但交接“按文件数 grpo 191 · dapo 87 · cispo 17 · sao 15 · flashreinforce 20 · opd 25 · antidoom 14 · ftpo 6”**无法用常规口径复现**：`grep -ril`（排除 .git）实测 221/104/20/21/**20**/34/**14**/9/0（仅 flashreinforce、antidoom、tlpo 三项对上）；名称级、.py 级、历史路径级、行数级也都不吻合 → 该组数字应标注统计口径/时点或删除。 |
| 6 | feat/heli-r00-training-eval 分支 | ✅（有重大新发现） | 分支 = main + **8 个提交**（main 比它多 1 个 `chore: configure code owners`），最后提交 `785a231a 2026-10-28T08:54:46Z`；8 个提交全部围绕 “**bounded post-training evaluation**”（+516/−48，15 文件：eval/prepare.py +283、eval/run.sh +85、README +71，改 SFT/OPD/FlashREINFORCE launcher 与 `skyrl/train` 入口）。**“heli” = Helicopter（评测 scoreboard/流水线）**：分支 README 里给出回调 `["python","-m","helicopter","checkpoint-result","/run/spec.json","train"]`、模型名 `rwkv7-g1l-13.3b-heli-r01-sft`（heli-r00/r01 = run 编号）。即该分支是“给 Helicopter 记分板跑训练-评测闭环”的集成分支，**不是** Helicopter 仓库本身；`rwkv-rs/Helicopter` 网页 **404**（公开不可见，与交接 §10.1 一致）。main 上 `antidoom/train.py:175` 已引用 `https://eval.rwkv.rs/scoreboard`。 |
| 7 | 8 卡可跑性 | ⚠️ 需真机 + 先适配 | 静态结论：**软件栈齐全且可安装（证据充分），但“默认 8 卡配方”在 Snellius 单节点不能原样跑**。①README 明说默认目标是“**one node with eight 96 GB Pro6000 GPUs**”（`README.md:17,23-25`），5 条 launcher 的 8 卡拆分表齐全；②`launcher_common.sh:21-23` 写死 `CUDA_VISIBLE_DEVICES=0..7`、`NUM_GPUS=8`、`RAY_ADDRESS=local`（**单节点假设**），`sft/run.sh:61` `placement.num_nodes=1`；③**`eval/run.sh:12` 硬性 `NUM_GPUS` 必须等于 8**，否则直接 exit 2；④**Snellius 没有 8-GPU 节点**：`gpu_h100` = 4×H100/节点、`gpu_a100` = 4×A100/节点（sinfo/scontrol 实测），且 80GB < 96GB 目标显存，eval 默认 `MAX_NUM_SEQS=1024`（`eval/run.sh:29`）在 80GB 上按 heli README 的 61.95 GiB/1024 seq 估算会 OOM；⑤主仓依赖 torch==2.13.0 + cu130 轮子（`pyproject.toml` rwkv extra + `docker/Dockerfile` 基础镜像 `anyscale/ray:2.57.0-py312-cu130`），而 Snellius 登录节点可见 CUDA module 最高 **12.9.1**、无 13.x；`--prepare-flashrwkv2` 必须在有 GPU + `nvidia-smi` 的机器上预编译并校验 vLLM commit（`prepare_flashrwkv2.py:15-48`），集群驱动版本未能静态确认 → 编译链/CUDA 13 兼容性需实测。⑥`--test_mode` 五条 launcher + eval 均支持 ✅。结论等级：**能装（静态可判定）/ 默认 8 卡配方 = 需先做多节点与显存 profile 适配；能否跑通 = 需真机实测**（不能下“能跑”结论）。 |
| 8 | 与上游 272 ahead / 58 behind | ✅（behind 应为 59） | `git rev-list --left-right --count upstream/main...origin/main` = **59 / 272**（2026-11-05T20:24Z）：**ahead=272 精确一致**；behind=59（交接 58，多出的 1 个是 upstream 今天 19:32Z 的新提交 `1f77d34 [megatron] Qwen3.8-Flash-Next context parallelism up to 262K (#2607)`）→ 建议写“≈59（随上游推进）”。merge-base = `69410e77`（2026-10-23T22:23:49Z），fork 相对它改 186 文件 +38,659/−1,787。 |

**总评**：交接 §3 的“结构判断”基本可靠（fork 事实、5 launcher、数学-only 评测、单轮现状、工程约束、3,354 行单测、272 ahead、heli 分支存在），但**两个关键事实错误/需改**：①**pin 写成 67f0c599（实际 2852a7b1d，且非私有）**；②**对“不在 CI”的解释不完整（fork CI 整体被上游门禁关掉）**。另有 heli 分支含义可升级为确定结论（= Helicopter scoreboard 训练-评测闭环），8 卡结论应改为“需先适配 Snellius 硬件/多节点后实测”。

---

## §2 逐条证据

> 所有证据文件在 `reports/skyrl/evidence/`；下列“E-xx:行”指向文件内原文。

### 2.1 仓库、分支、时间基线（任务 1）

- 命令与原始输出：`evidence/01-ls-remote-skyrl-rwkv.txt`、`evidence/02-ls-remote-vllm-rwkv.txt`、`evidence/05-branches-and-commits.txt`。
- `git ls-remote`（2026-11-05T20:08Z）：
  - skyrl-rwkv：`HEAD`/`refs/heads/main` = `04a5c985…`；`refs/heads/feat/heli-r00-training-eval` = `785a231a…`；无其他分支。
  - vllm-rwkv：仅 `refs/heads/rwkv` = `7a6adcc6…`（另有 252 个 PR ref，无分支）。
- 两仓 HEAD 提交时间（`git log -1 --format='%H %cI'`）：main `2026-10-31T03:47:56-07:00` = **10:47:56Z**；heli `2026-10-28T01:54:46-07:00` = **08:54:46Z**；vllm `2026-10-31T18:56:01+08:00` = **10:56:01Z**。与交接基线逐秒一致。
- 克隆方式：`git clone --filter=blob:none`（skyrl 72MB / vllm 271MB，完整提交历史；vllm rwkv 分支历史 23,078 commits）。
- 远端：`origin=https://github.com/rwkv-rs/skyrl-rwkv`，为比较另加 `upstream=https://github.com/NovaSky-AI/SkyRL`。

### 2.2 CI 真相 & 3,354 行 RWKV 单测（任务 2）

- `evidence/07-rwkv-tests.txt`：`find tests -path '*rwkv*' -type f` → 4 个文件；`wc -l` = 790 / 788 / 1087 / 689 = **3354**。✅ 交接数字精确。
- 测试文件：`tests/backends/skyrl_train/rwkv/test_{antidoom,model_wrapper,rollout,value_pretraining}.py`；目录**无 `__init__.py`**，模块级无 `skip/skipif`（即 pytest 会正常收集，不会被 skip）。
- CI 侧：`evidence/06-ci.txt`
  - `.github/workflows/` 共 **16 个** workflow（上游原样），`grep -ril rwkv .github/ ci/` → **0 命中**；
  - **每个 workflow 均带 `if: github.repository == 'NovaSky-AI/SkyRL'` 门禁**（cpu_skyrl 有 4 处，其余 1–2 处；示例 `.github/workflows/cpu_skyrl.yaml:38`，注释原文：“CI runs only in the upstream repo … fork CI is off by policy”）→ 在 `rwkv-rs/skyrl-rwkv` 这个 fork 里**任何 CI 都不会跑**；
  - fork 相对 merge-base 对 `.github`/`ci` 的改动只有 `A .github/CODEOWNERS`（内容 `* @Cai-z-us`）；
  - 上游 CPU workflow 的 pytest 收集路径是 `pytest tests/train/ tests/backends/skyrl_train/ …`（`cpu_skyrl.yaml:79`），**如果**该 workflow 在本 tree 运行会递归收集到 `tests/backends/skyrl_train/rwkv/`——但这只发生在上游仓库，fork 中不运行。
- 结论：交接“3,354 行 RWKV 单测存在但不在 CI”✅ 正确；更准确表述应升级为“**fork 内 CI 被上游仓库门禁整体关闭，等于全仓无 CI**”。

### 2.3 vLLM fork pin（任务 3）——交接此处有误

- `evidence/08-pin.txt`：
  - `pyproject.toml:584`：`vllm = { git = "https://github.com/rwkv-rs/vllm-rwkv", rev = "2852a7b1d597f6e2131ec801de331b886471cd95", extra = "rwkv" }`
  - `uv.lock:10591/10830/12347` 同 pin；锁定版本串 `0.23.1rc1.dev5461+g2852a7b1d.rwkv`。
  - heli 分支（`git show origin/feat/heli-r00-training-eval:pyproject.toml`）pin **相同**。
  - vllm-rwkv：HEAD = `7a6adcc6`（2026-10-31）；pin = `2852a7b1d`（2026-10-26T16:33:41-07:00，`Merge pull request #82 from rwkv-rs/fix/rwkv-tuning-cache`）；`git merge-base --is-ancestor pin HEAD` → **YES**；`rev-list --count pin..HEAD` = **2**（`7a6adcc6` 与 `0ee2d0d4`）。即 **pin 落后当前 fork HEAD 2 个提交**，但存在且在历史中。
  - 交接所称 `67f0c599`：完整 SHA `67f0c5996c50dca0ad779da545cb491527de988f` 在 GitHub 上存在（`curl https://github.com/rwkv-rs/vllm-rwkv/commit/67f0c599` → 200，标题 `fix(benchmark): remove unsupported rapid-sampler seed`，提交日期 **2026-08-04**），`git fetch --depth=1` 亦成功；但 **不是 rwkv 分支 HEAD 的祖先**（`merge-base --is-ancestor` = NO；`rev-list --all` 无此号；ls-remote 所有 ref 也无此号）→ 只是旧分支/PR 上的历史提交，**不是可安装的当前 pin**。
  - pin 校验代码：`examples/train/rwkv/train/common/prepare_flashrwkv2.py:15-25` `validate_vllm_revision()` 读取 `pyproject.toml` 的 pin，与已安装 `vllm` 的 `direct_url.json#vcs_info.commit_id` **强校验**，不一致直接 `SystemExit`；`--check` 再校验 native cache manifest。
- 结论：**交接“绑定私有 vLLM-RWKV fork @67f0c599” ❌**（哈希错、且仓库公开）。“绑 fork”本身 ✅。

### 2.4 多轮 / loss_mask / skyrl-agent（任务 4）

- `evidence/09-multiturn-tlpo.txt`：
  - `max_turns: int = 1`（`skyrl/train/config/config.py:1586`）；`grep -rn max_turns examples/train/rwkv/` → **0 命中**（5 条 launcher 全部没设置）；
  - `use_conversation_multi_turn: bool = True`（`config.py:1599`，**默认已开**）；RWKV 目录仅 `sao/run.sh:131` 显式 `generator.use_conversation_multi_turn=true`；
  - 生成器把 `max_turns` 注入 env：`skyrl_gym_generator.py:186,414,934`（env 侧按 max_turns 判 done）→ 默认 1 即单轮；
  - `TurnOutput.get_turn_loss_mask()`（`skyrl_gym_generator.py:125-144`）：assistant 生成 token 记 1、补的 EOS 记 0、**“Observation tokens are always masked out (set to 0)”**；
  - `RWKVTrajectoryLogger`（`skyrl/train/utils/rwkv_trajectory_logging.py:34-37`）采样字段含 `num_turns`、`assistant_spans`、`loss_mask`；`_assistant_spans()` 位于同文件 `:9`；
  - `grep -rn "rwkv\|RWKV" skyrl-agent/` → **空**（0 引用）✅。
- 小修正：交接把 multi-turn 说成“代码有（use_conversation_multi_turn…）”，实际该开关**默认已是 True**；限制核心仍是 `max_turns` 默认 1 且 RWKV recipe 从未设置。

### 2.5 TLPO / launcher / 算法数（任务 5）

- `evidence/09-multiturn-tlpo.txt`：
  - `grep -rn "tlpo\|TLPO"`（排除 .git）→ **0 命中**；“tlpo 0”✅。
  - 5 条 launcher：`examples/train/rwkv/train/{antidoom,flashreinforce,opd,sao,sft}`（+ `common`, `launcher_common.sh`）✅。
  - `antidoom` README 第 1 行 `# RWKV Antidoom / FTPO`；FTPO 实现 `antidoom/train.py:547 regularise_ftpo_rows`、`:590 extract_ftpo_pair`、`:653 ftpo_loss` ✅（“antidoom(FTPO)”成立）。
  - 算法文件数（同一统计口径复测，2026-11-05T20:19Z）：`grep -ril <alg> --exclude-dir=.git` = grpo 221 / dapo 104 / cispo 20 / sao 21 / flashreinforce 20 / opd 34 / antidoom 14 / ftpo 9 / tlpo 0；`.py`-only = 25/20/12/7/10/14/9/2/0；历史路径 = 58/135/3/6/5/23/6/0/0。**没有一种口径能同时复现交接的 191/87/17/15/20/25/14/6**（仅 flashreinforce=20、antidoom=14 恰好一致）→ 交接该组数字口径不明，建议降级/删除。

### 2.6 feat/heli-r00-training-eval 分支（任务 6）

- `evidence/10-heli-branch.txt`：
  - `git rev-list --count origin/main..heli` = **8**（heli 独有）；`heli..main` = **1**（`04a5c985 chore: configure code owners`，2026-10-31）→ heli 分支在 CODEOWNERS 提交前分叉，未合并。
  - 8 个提交（2026-10-27T20:39 → 2026-10-28T01:54-07:00，最后提交 **2026-10-28T08:54:46Z**，与交接基线一致）：
    `36da5f80 feat(rwkv): integrate bounded post-training evaluation` → `ad26084d`、`7ad5e438`、`f2414a61`、`d9661360`、`c6fa5248`、`0c584e4b`、`785a231a fix(rwkv): resume bounded training and evaluation phases`。
  - `git diff --stat main..heli`：15 文件 **+516/−48**，主体是 `examples/train/rwkv/eval/prepare.py +283`、`eval/run.sh +85`、`README +71`、`launcher_common.sh +9`、`sft/prepare.py +45`，另动 pyproject/uv.lock/skyrl 入口 → 即“训练结束后发布 HF export → probe → 全量评测 → 回调”的 bounded train-eval 生命周期。
  - **heli 含义 = Helicopter**：heli 分支 README:70/74/79 出现 `"model": "/weights/rwkv7-g1l-13.3b-heli-r01-sft"`、`"SERVED_MODEL_NAME": "rwkv7-g1l-13.3b-heli-r01-sft"`、`"callback": ["python","-m","helicopter","checkpoint-result","/run/spec.json","train"]`；`r00/r01` 是 run 编号。main 分支 `antidoom/train.py:44,140,142,175,182,1466` 已有 scoreboard 元数据（URL `https://eval.rwkv.rs/scoreboard`）。
  - `https://github.com/rwkv-rs/Helicopter` → **HTTP 404**（`evidence/14-web-checks.txt`）；`git ls-remote` 该仓返回 “could not read Username”（= 公开不可达）。即 Helicopter 仓库当前公开不可见（与 §10.1 一致），但“heli 分支用途”可由分支内容确定。
- 结论：heli 分支 = **Helicopter scoreboard 的训练-评测闭环集成分支（r00/r01 用）**，不是“另一个 scoreboard 仓库”，也**未合并进 main**（main 只有 CODEOWNERS 一个后续提交）。

### 2.7 8 卡可跑性（任务 7，含 §10.1 第 1 条）

证据：`evidence/11-8gpu.txt`、`evidence/13-quotes.txt`、`evidence/14-web-checks.txt`。

**(a) 安装方式与依赖链（静态可判定，证据充分）**
- `uv sync --extra rwkv`（`temp/rwkv-grpo-start.md:9`；README/AGENTS 同款）；Python **3.12**（`.python-version`）。
- rwkv extra（`pyproject.toml:146-155`）：`skyrl[skyrl-train]` + `torch==2.13.0` + `transformers==5.21.0.dev0`（fork）+ `vllm`（fork）+ `FlashRWKV2==0.1.0a17` + `tokenizers`（fork）+ `lighteval`（fork）+ matplotlib。
- git 依赖 pin（`pyproject.toml:583-586`）：transformers-rwkv `f93dd4e0`、vllm-rwkv `2852a7b1d`、lighteval-rwkv `c5475e27`、tokenizers-rwkv `c5d8dde5`；另 `Joluck/NoRA@4669c35c`（`:348`）。**全部公开可达**（2026-11-05T20:2x UTC curl 实测均为 200，含 PyPI `FlashRWKV2` JSON 与 HF `rwkv-rs/rwkv7-g1-st`）。
- CUDA 链：`[[tool.uv.index]] pytorch-cu130`（cu130 轮子）+ `docker/Dockerfile` 基础镜像 `anyscale/ray:2.57.0-py312-cu130`。
- 原生扩展：`prepare_flashrwkv2.py` 需 `nvidia-smi` 读 driver、`load_extension()` 现场**编译/加载** FlashRWKV2 native，并输出 `environment.json`（torch/cuda_runtime/driver/compute_capability/artifact）——**必须在目标 GPU 上跑**，登录节点不可完成。
- 形态：5 条 launcher 均支持 `--test_mode`（ANTIDOOM/FlashREINFORCE/OPD/SAO/SFT `run.sh` 首部解析 + `eval/run.sh:13`），README 说 test_mode = 有界数据前缀 + 5 个 optimizer steps、关 W&B。

**(b) 8 卡配方与单节点假设（关键）**
- README `:17` “default training settings target **eight Pro6000 GPUs**”；`:23-40` 明确“recommended hardware profile for **one node with eight 96 GB Pro6000 GPUs**”，并给 5 法拆分表（AntiDoom/FTPO 8-rank FSDP；FlashREINFORCE 4 learner+4 inference；OPD 6+2；SAO 2 policy+4 critic+2 inference；SFT 8-rank FSDP）。
- `launcher_common.sh:21-23`：`CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`、`NUM_GPUS=8`、`RAY_ADDRESS=local` → **单节点 8 卡写死默认**；`sft/run.sh:61` `placement.num_nodes=1`；eval 侧 **`eval/run.sh:12` 硬性 `NUM_GPUS==8`，否则 exit 2**（`eval/run.sh:11-12`）。
- eval 默认：`GPU_MEMORY_UTILIZATION=0.65`、`MAX_NUM_SEQS=1024`、`MAX_MODEL_LEN=32768`（`eval/run.sh:28-30`）；heli 分支 README 说明 61 层/4096 hidden 单序列 FP32 state ≈ **61.95 MiB**，1024 seqs = **61.95 GiB**（heli 分支因此把 eval 默认降到 128 seqs/worker）。→ 在 80GB 卡上需显著下调，默认 1024 有 OOM 风险。

**(c) Snellius 实测硬件（登录节点只读查询，未提交作业）**
- `sinfo`/`scontrol show node gcn73`：`gpu_h100` 分区 = **4×H100/节点**（GRES `gpu:h100:4`，RealMemory 720G/节点）；`gpu_a100` = **4×A100/节点**（`gpu:a100:4`）。**没有任何 8-GPU 单节点分区**；8 卡需跨 2 节点（Slurm 支持多节点分配，但仓库默认 `RAY_ADDRESS=local`/单节点 launcher 需改造）。
- CUDA：登录节点 `module spider CUDA` 可见最高 **CUDA/12.9.1**（2023–2026 全 stack 均无 13.x）；仓库要求 cu130 轮子 + Docker base cu130 → 本机 `uv sync` 下来的 torch 是 cu130，`--prepare-flashrwkv2` 若用集群 nvcc 12.9 编译原生扩展可能版本不匹配（torch cpp_extension 会拒绝）；**驱动版本无法从登录节点静态获得**（无 nvidia-smi/GPU），需在 GPU 节点实测确认（SURF wiki 被 Anubis 反爬拦截，无法在线取官方文档；已如实记录）。
- 开发机画像：`AGENTS.md:170-172` 显示官方开发环境是 `ssh rwkv-sha-pro6000x8` 的 **8×PRO6000 机器**、`~/Projects/MachineLearning/skyrl-rwkv` —— 说明默认配方是给那台机器调的，不是 Snellius。

**(d) 结论（分级）**
1. **能装**：Linux + Python 3.12 + 网络下 `uv sync --extra rwkv` 静态可行（依赖全部公开、pin 齐全、有 `uv.lock` 4.1MB 锁文件）；FlashRWKV2 PyPI wheel 存在。
2. **默认 8 卡配方 ≠ Snellius 可跑**：单节点 8×96GB 假设与 Snellius 4×H100 80GB/节点冲突；`eval/run.sh` 硬性 8 卡；eval 默认 1024 seqs 显存估计 61.95GiB > 80GB 可用余额（还有权重/workspace）。**需改造**（多节点 Ray 或 `NUM_GPUS=4` + 调 batch/seq 上限/eval 128 seqs）后才能谈跑通。
3. **能否跑通 = 需真机实测**（见 §4）；静态只能判定到“装得上、配方目标硬件与 Snellius 不匹配”。

### 2.8 与上游 NovaSky-AI/SkyRL 的 272 ahead / 58 behind（任务 8）

- `evidence/12-upstream-compare.txt`（2026-11-05T20:24Z）：
  - `git rev-list --left-right --count upstream/main...origin/main` → **`59  272`**（左=upstream 独有=behind，右=fork 独有=ahead）。
  - fork main HEAD `04a5c985`（2026-10-31T10:47:56Z）；upstream main HEAD `1f77d340`（2026-11-05T11:32:37-08:00 = 19:32Z，`[megatron] Qwen3.8-Flash-Next context parallelism up to 262K (#2607)`）；merge-base `69410e77`（2026-10-23T22:23:49Z）。
  - fork 相对 merge-base：186 文件、+38,659/−1,787（uv.lock 占大头）。
- 结论：**ahead 272 ✅ 精确**；behind 交接写 58，实测 **59**（原因是 upstream 在 2026-11-05T19:32Z 又合并了 1 个 commit，交接测量时点更早）。建议写“272 ahead / 59 behind（截至 2026-11-05T20:24Z，随上游推进）”。

### 2.9 §3 其余事实抽查（均带证据）

| §3 原文事实 | 实测 | 证据 |
|---|---|---|
| fork of NovaSky-AI/SkyRL；创建 2026-08-30；最后推送 2026-10-31；5★；Apache-2.0 | **全部 ✅**：`fork=true`、`created_at=2026-08-30T19:00:45Z`、`pushed_at=2026-10-31T10:49:00Z`、`stargazers_count=5`、`license=Apache-2.0`（LICENSE 文件为 Apache 2.0 全文） | `evidence/04-api-repo-metadata.json`、`evidence/14-web-checks.txt`（1 次 GitHub API，2026-11-05T20:15:51Z） |
| 单一主力贡献者 Cai-z-us | ✅ 272 个 fork-only 提交 **100%** 由 Caizus/Cai-z-us（同一人 3 个邮箱）提交：260+6+6 | `evidence/05-branches-and-commits.txt`（`git shortlog -sn --all` 的 274 条 = main 上 266 + heli 分支独有的 8；272 个 fork-only 提交按邮箱拆为 260+6+6，全部作者名为 Caizus/Cai-z-us） |
| 5 条 launcher / 算法实现 | ✅ launcher 5 个；`tlpo` 0 ✅；grpo/dapo/cispo 由上游 SkyRL 提供（本 fork 未删） | `evidence/09-multiturn-tlpo.txt` |
| 评测只有数学 5 项，无 agent 任务 | ✅ `eval/prepare.py:18-24`：gsm8k / math_500 / aime24 / aime25 / aimo_progress_prize_1；`examples/train/rwkv/` grep `bfcl|tau-bench|agentbench|toolcall` = 0 | `evidence/13-quotes.txt` |
| wkv_mode=fp32io16；FP32 recurrent state；FlashRWKV2 预编译并校验 vLLM commit | ✅ `run.sh` 中 `wkv_mode=fp32io16`、`mamba_ssm_cache_dtype=float32`；`prepare_flashrwkv2.py:15-48` 校验 pin + 预编译；heli README 有 61.95MiB FP32 state 数字 | `evidence/13-quotes.txt`、`evidence/11-8gpu.txt` |
| 右填充分块保留因果 | ✅ `model_wrapper.py:52 RWKV_CHUNK_LENGTH=16`；`:475` 注释 “right-padded bucket per microbatch. Tail padding cannot affect…”、`:490/:931-938` 右填充分块；`antidoom/train.py:562-575` “Right-pad causal contexts” | `evidence/13-quotes.txt` |
| 禁止 sequence parallel / microbatch packing / torch.compile | ✅ 文档 `docs/rwkv/upstream-weight-sync-handoff.md:49` + **代码硬校验** `model_wrapper.py:373-379/917-919`（`raise ValueError("RWKV does not support …")`）；`:156` 另有 sharded_rdt 禁止 | `evidence/13-quotes.txt` |
| 权重同步契约引文 | ✅ 逐字核对：`docs/rwkv/upstream-weight-sync-handoff.md:33` “CUDA graphs captured against the previous recurrent runtime state must be dropped”、`:35` “Recurrent state/cache slots must not survive a policy weight update.” | `evidence/13-quotes.txt` |
| logprob 问题已解决（behavior logprob/token 对齐 + Score-Centering float32 top-k 旁路 sample_support_top_k=128 + sampled-token logprob 兜底） | ⚠️ **部分**：合同文档 `upstream-weight-sync-handoff.md:52-66` 明确写有该机制（“opt-in (`flashreinforce.score_centering=false` by default)”、`sample_support_top_k` 默认 128、float32 top-k 旁路、sampled-token logprob 兜底）；代码 `config.py:886-907`、`2200-2265` 实现存在。但 **默认关闭，5 条 RWKV launcher 里 0 处启用**（grep `centering` 无命中）→ 应表述为“机制存在且默认关闭，默认配方未验证”，不能写“已解决” | `evidence/13-quotes.txt`、`evidence/09-multiturn-tlpo.txt` |

---

## §3 对交接 §3（及 §10.1 第 1 条、§2 表）的修订建议

> 格式：**原文** → **实测** → **建议改法**。“原文”均摘自 `内部交接 2026-11-05（未公开存档）` 对应行。

1. **pin 哈希（§3 line 75）**
   - 原文：“绑私有 vLLM-RWKV fork（`rwkv-rs/vllm-rwkv@67f0c599`）”
   - 实测：pin = `2852a7b1d597f6e2131ec801de331b886471cd95`（`pyproject.toml:584`、`uv.lock:10591`，main 与 heli 分支相同），是 vllm-rwkv HEAD `7a6adcc6` 的祖先、落后 2 个提交；`67f0c5996c…` 是 2026-08-04 的旧提交、不在 rwkv 分支历史，**不是 pin**；仓库**公开**（`git clone` 无凭证成功）。
   - 建议改法：“绑定公开 fork `rwkv-rs/vllm-rwkv@2852a7b1d597f6e2131ec801de331b886471cd95`（2026-10-26；落后该 fork HEAD 2 个提交；`prepare_flashrwkv2.py` 会强校验安装 commit 与 pin 一致）”。

2. **CI 表述（§3 line 75）**
   - 原文：“缺陷：**3,354 行 RWKV 单测存在但不在 CI**”
   - 实测：行数 ✅ 精确（4 文件 790+788+1087+689）；但 fork 继承的 16 个 workflow **全部**以 `if: github.repository == 'NovaSky-AI/SkyRL'` 门禁，fork 内 **CI 整体不运行**；`.github/`、`ci/` 中 `rwkv` 0 命中；fork 只新增 `.github/CODEOWNERS`。上游 CPU workflow 的通用 pytest 路径（`cpu_skyrl.yaml:79`）若在本 tree 运行**会**收集到 `tests/backends/skyrl_train/rwkv/`。
   - 建议改法：“3,354 行 RWKV 单测（`tests/backends/skyrl_train/rwkv/`，4 文件）从未在 CI 跑过；更根本的是 **fork 无 CI**：继承的上游 16 个 workflow 全部按 `github.repository == 'NovaSky-AI/SkyRL'` 跳过，fork 侧仅加 CODEOWNERS、未加任何 CI”。

3. **heli 分支（§3 未写，§10.1 只有 Helicopter 仓库 404 一行）**
   - 实测：`feat/heli-r00-training-eval` = main + 8 commits（+516/−48，2026-10-27~28，`785a231a`），内容是 **bounded post-training evaluation 生命周期**（发布 HF export → probe → 全量评测 → `python -m helicopter checkpoint-result` 回调）；“heli” = **Helicopter**（scoreboard/流水线），模型名 `rwkv7-g1l-13.3b-heli-r01-sft`；main 只比它多 1 个 CODEOWNERS 提交（分支未合并）。`rwkv-rs/Helicopter` 公开 404。
   - 建议**新增一条**：“`feat/heli-r00-training-eval` 是给 Helicopter 记分板跑 r00/r01 训练-评测闭环的分支（8 commits，未合并；+516/−48），不是主分支内容；Helicopter 仓库公开不可见（404），但回调契约可从该分支 README 反推。”

4. **多轮（§3 line 74）**
   - 原文：“代码有（`use_conversation_multi_turn`、`loss_mask` 区分 assistant/observation、`RWKVTrajectoryLogger` 记 `num_turns`/`assistant_spans`），但 RWKV recipe 里 `max_turns` 从未设置过（默认 1），`skyrl-agent/` 零 RWKV 引用”
   - 实测：全部 ✅（另：`use_conversation_multi_turn` **默认就是 True**，`sao/run.sh:131` 还显式置 true；真正的单轮限制来自 `max_turns=1` + 无 RL 多轮 env）。
   - 建议改法：保留原意，补一句“`use_conversation_multi_turn` 默认 True、SAO launcher 显式开启；单轮的根因是 `max_turns` 默认 1 且 RWKV recipe 未设置，且 RWKV 用的 `ultradata` env 是数学单轮任务”。

5. **算法“按文件数”统计（§3 line 69）**
   - 原文：“grpo 191 · dapo 87 · cispo 17 · sao 15 · flashreinforce 20 · opd 25 · antidoom 14 · ftpo 6 · **tlpo 0**”
   - 实测：`tlpo 0` ✅；其余无法用常规 grep/find 口径复现（实测文件级 221/104/20/21/20/34/14/9/0；仅 flashreinforce 20、antidoom 14 对上）。
   - 建议改法：改为“存在性”表述（“已实现 GRPO/DAPO/CISPO 与 5 条 RWKV launcher：AntiDoom+FTPO / FlashREINFORCE / OPD / SAO / SFT；**TLPO 无实现**”），或注明统计口径/统计时点。

6. **logprob（§3 line 73）**
   - 原文：“**logprob 问题已解决**：behavior logprob/token 对齐 + Score-Centering 的 float32 top-k 旁路（`sample_support_top_k=128`）+ sampled-token logprob 兜底”
   - 实测：机制在合同文档 `docs/rwkv/upstream-weight-sync-handoff.md:52-66` 与代码中确实存在（默认 `score_centering=false`，`score_centering_top_k=128` → 推断到 `sample_support_top_k`），但**默认关闭、RWKV launcher 0 处启用**，不能说“已解决”。
   - 建议改法：“logprob 对齐/Score-Centering 旁路机制已实现但**默认关闭**、默认配方未启用（`flashreinforce.score_centering=false`），属‘有代码未验证’”。

7. **8 卡（§10.1 第 1 条，line 210；§3 line 75“落后 58 commits”）**
   - 原文：“`skyrl-rwkv` 在真实 8 卡上能否跑通（依赖 pin 死的私有 vLLM fork；无 CI）”
   - 实测：pin 公开、CI 确实无（fork 门禁）、**硬件前提是单节点 8×96GB Pro6000**（README），而 Snellius 单节点最多 4×H100 80GB；`eval/run.sh` 硬性 `NUM_GPUS==8`；集群 CUDA module 最高 12.9.1 vs 仓库 cu130；依赖全部公开可装。
   - 建议改法：“在真实 8 卡上能否跑通 = 待实测；**注意默认配方假设单节点 8×96GB Pro6000，Snellius 需 2 节点（4×H100/节点、80GB）或多卡降配 + 改 eval 的 8 卡硬约束**；pin 为公开仓库 `2852a7b1d`；fork 无 CI（全 workflow 上游门禁）。”
   - 另：§3 line 75“落后上游 58 commits”建议改为“**272 ahead / 59 behind（截至 2026-11-05T20:24Z；随上游推进）**”。

---

## §4 尚未能静态判定、需真机实测的事项

> 以下全部是“登录节点只读分析”无法覆盖、必须上 GPU 节点/提交作业才能回答的：

1. `uv sync --extra rwkv` 在 Snellius 环境的**实际可安装性**：cu130 轮子下载/大小（torch 2.13+cu130、vllm fork 源码构建、FlashRWKV2、tilelang 0.1.15、PEFT/NoRA 构建）能否在登录节点/计算节点网络与磁盘配额内完成；计算节点是否能联网（仓库 launcher 用预建 `.venv` + `RAY_ENABLE_UV_RUN_RUNTIME_ENV=0`，若在登录节点 sync 完成则计算节点可离线，但未验证）。
2. `--prepare-flashrwkv2`（`prepare_flashrwkv2.py`）在 **H100 sm_90 / A100 sm_80** 上能否编译并建立 tuning cache；**CUDA 13（torch cu130）与 Snellius 可用 nvcc 12.9.1 / 实际驱动版本是否兼容**（集群 module 最高 12.9.1，驱动版本无法从登录节点读取；SURF wiki 被反爬拦截未能取官方文档）。这是当前最大的未验证风险点。
3. 5 条 launcher 的 `--test_mode`（各自 5 optimizer steps）在 Snellius 上能否完整跑通（含 FSDP、vLLM-RWKV 推理、权重同步）；`eval/run.sh` 的 8 卡硬约束需改到 4 卡或多节点后才可测。
4. 多节点（2×4 H100）是否可行：仓库默认 `RAY_ADDRESS=local`、`placement.num_nodes=1`、`CUDA_VISIBLE_DEVICES=0..7`，需要改 launcher/placement 后用 2 节点 Slurm 作业验证 Ray 集群与跨节点 NCCL weight sync。
5. 显存画像：main 分支 eval 默认 `MAX_NUM_SEQS=1024`、`GPU_MEMORY_UTILIZATION=0.65`（`eval/run.sh:28-30`）在 80GB 卡上的真实 OOM 边界；heli 分支“128 seqs / 61.95 GiB 估算”是否成立（需 13.3B `rwkv7-g1l-13.3b-heli-r01-sft` 权重实测）。
6. 权重更新后的 **recurrent state 失效 + CUDA graphs 丢弃**（`docs/rwkv/upstream-weight-sync-handoff.md` 的 8 项 validation checklist：model load / batched recurrent forward / HF-trainer logprob parity / vk_mode 生成 / NCCL+CUDA IPC / delta reload / 两次连续更新 / 更新后 CUDA graph 生成）在真机上的通过情况。
7. 多轮 rollout：即使把 `max_turns` 调大，RWKV 侧用的是 `ultradata`（数学单轮）env，**没有现成的多轮 tool env 与之对接**；`skyrl-agent/` 零 RWKV 引用 → “多轮训得动吗”仍需自建（与交接 §8/§9 判断一致，但注意这不是“调个参数”的事）。
8. heli 分支的 `RWKV_TRAIN_EVAL` 生命周期（训练→发布→probe→full→callback）在 Snellius 上能否跑通；Helicopter callback 是私有/不存在的模块（仓库 404），**外部无法复现**该回调，只能跑不加 `RWKV_TRAIN_EVAL` 的原生训练路径。
9. 交接 §5 的“评测/成绩”类结论（如 Helicopter scoreboard 是否上线、多步 0/2 等）不在本任务范围，本报告未复核。

---

## §5 证据索引（`reports/skyrl/evidence/`）

| 文件 | 内容 |
|---|---|
| `00-env.md` | 主机/时间/git/磁盘 + 末次仓库快照 |
| `01-ls-remote-skyrl-rwkv.txt` | skyrl-rwkv 全 refs（含 PR refs），2026-11-05T20:08Z |
| `02-ls-remote-vllm-rwkv.txt` | vllm-rwkv 全 refs（254 行），2026-11-05T20:08Z |
| `03-ls-remote-helicopter.txt` | `rwkv-rs/Helicopter` 不可公开访问（git 要求凭证） |
| `04-api-repo-metadata.json` | **唯一 1 次 GitHub API**：repo 元数据原始 JSON + HTTP 200 |
| `05-branches-and-commits.txt` | 分支、HEAD 时间、ahead/behind、作者统计、fork diff |
| `06-ci.txt` | 16 个 workflow 清单、门禁计数、pytest 路径、fork CI 改动 |
| `07-rwkv-tests.txt` | 4 个 RWKV 测试文件、3,354 行、无 skip、CI grep 0 命中 |
| `08-pin.txt` | pyproject/uv.lock pin、pin↔HEAD 关系、67f0c599 判定、pin 校验代码 |
| `09-multiturn-tlpo.txt` | max_turns、loss_mask、trajectory logger、skyrl-agent、tlpo、5 launcher |
| `10-heli-branch.txt` | heli 8 commits、diff stat、helicopter 回调/模型名、scoreboard URL |
| `11-8gpu.txt` | 8-GPU 配方原文、launcher GPU 默认、eval 硬 8 卡、依赖、Snellius 硬件、CUDA module |
| `12-upstream-compare.txt` | `59 272` 原始输出、三仓 HEAD、merge-base、diff stat |
| `13-quotes.txt` | §3 原文引用核对（weight-sync 33/35/49、Score-Centering、eval 列表、禁止项代码、右填充因果） |
| `14-web-checks.txt` | curl 状态（repo/Helicopter/67f0c599/依赖/HF/PyPI）、star=5、API 摘要 |

复现关键命令（均不消耗 GitHub API）：

```bash
cd ~/AlchemyRepos/RWKV-AgenticLearning
git -C repos/skyrl-rwkv rev-list --left-right --count upstream/main...origin/main   # 59 272
git -C repos/skyrl-rwkv log -1 --format='%H %cI' origin/feat/heli-r00-training-eval # 785a231a 2026-10-28T01:54:46-07:00
git -C repos/vllm-rwkv merge-base --is-ancestor 2852a7b1d597f6e2131ec801de331b886471cd95 HEAD && echo pin-is-ancestor
grep -ril rwkv repos/skyrl-rwkv/.github repos/skyrl-rwkv/ci || echo "no rwkv in CI"
wc -l repos/skyrl-rwkv/tests/backends/skyrl_train/rwkv/*.py                       # 3354 total
git -C repos/skyrl-rwkv grep -in "heli" origin/feat/heli-r00-training-eval -- '*.md'
```

---

## §6 核验边界与执行说明

- **未做**：未安装/运行任何依赖，未提交 GPU/SLURM 作业，未 clone 除任务指定外的仓库；GitHub API 只用 1 次（repo 元数据；额度 4 次内，全队 60/h 共享）。
- **环境限制**：本 session 的 read/write 工具绑定在另一侧文件系统（对本机 `/gpfs/...` 路径报 ENOENT），故全部文件读取/写入均用登录节点上的 `bash`（cat/sed/grep/heredoc）完成；不影响证据真实性。
- **时间**：所有时间戳为 UTC；本地时区 Europe/Amsterdam（UTC+1，2026-11-05 为 CET）。
- **快照会漂移**：上游 `upstream/main` 仍在推进（今天 19:32Z 新增 1 commit），ahead/behind、star 数、分支 tip 以后续复核为准；本报告所有结论标注了抓取时间，可复现。
