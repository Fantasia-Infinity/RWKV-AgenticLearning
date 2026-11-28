# 2026-11-28 新模型调查：RWKV-Agent-Lab 的 7.2B Agent 家族

> 调查时间：2026-11-28 14:30–16:00 CET。来源：HuggingFace API/raw、GitHub API/raw、rwkv.cn API。
> 触发：11-26 RWKV Agent 专场 slide（chase 线）列出的 3 个 HF 模型 + rwkv-pi / rwkv_lightning_cuda。

## 0. 图像 ↔ 实际公开状态

slide 列出的三个模型：

| slide 名称 | slide 描述 | 2026-11-28 实际状态 |
|---|---|---|
| `RWKV7-Agent-7.2B` | 多源开智通用底座 | 单仓 **401（私有/gated）**；权重在公开 bundle 中：`RWKV7-Agent-7.2B-v0.1.pth` |
| `RWKV7-Pi-7.2B-Anneal` | 同框架契约退火权重 | 单仓 **401**；权重：`RWKV7-Pi-7.2B-Anneal-v0.1.pth` |
| `RWKV7-Pi-7.2B` | rwkv-pi 强化发布版 · 开箱即用 | 单仓 **401**；权重：`RWKV7-Pi-7.2B-v0.1-final.pth`（legacy）+ **v0.2**（11-27 新增，推荐） |

- **公开分发仓**：`RWKV-Agent-Lab/RWKV7-Agent-7.2B-OpenSource`（created 2026-11-26T11:22Z，**Apache-2.0**）
- **另一公开仓**：`RWKV-Agent-Lab/RWKV7-DSH-7.2B`（created 11-26T11:20Z，**Apache-2.0**，NoRA r64 adapter）
- HF 组织 `RWKV-Agent-Lab`（"RWKV Agent Lab"）：**未认证（isVerified=false）**，4 members / 2 models / 2 datasets；
  **不是官方 RWKV 组织**，应视为 chase 线的工作组
- rwkv.cn 尚未发直播回顾（最新仍为 11-19 的 #23423445 预告）

## 1. 公开 bundle 内容（`RWKV7-Agent-7.2B-OpenSource`）

模型卡：**所有 `.pth` 都是 standalone merged BF16 权重**（无需外挂 LoRA/NoRA），家族谱系：

```text
RWKV7-Agent-7.2B-v0.1.pth                  (Shared General-Purpose Agent Foundation)
├── RWKV7-Pi-7.2B-Anneal-v0.1.pth          (Pi Coding — Post-SFT Annealed)
│   └── RWKV7-Pi-7.2B-v0.1-final.pth       (Pi Coding — legacy oldText/newText edit)
└── RWKV7-DSH-7.2B-Anneal-*.pth            (DSH Deep-Search — Annealed; 由 DSH track 上传)
```

| 文件 | 精度 | 大小 | 说明 |
|---|---|---|---|
| `RWKV7-Agent-7.2B-v0.1.pth` | BF16 | **14.40 GB** | 通用多轮工具使用/推理底座 |
| `RWKV7-Pi-7.2B-Anneal-v0.1.pth` | BF16 | 14.40 GB | 高信号 post-SFT 退火编码 agent |
| `RWKV7-Pi-7.2B-v0.1-final.pth` | BF16 | 14.40 GB | 旧编辑协议（`RWKV_EDIT_MODE=text`），已被 v0.2 取代 |
| **`RWKV7-Pi-7.2B-v0.2.pth`** | BF16 | 14.40 GB | **推荐**：Line-Edit v2 + DAgger（`RWKV_EDIT_MODE=line`） |
| `RWKV7-Pi-7.2B-v0.1-final.w8a16.rwkvq` | W8A16 | **7.69 GB** | 旧版量化 |
| **`RWKV7-Pi-7.2B-v0.2.w8a16.rwkvq`** | W8A16 | **7.69 GB** | **12–16 GB 显卡推荐**（rwkv_lightning_cuda 原生 `.rwkvq`） |
| `engine/rwkv-lightning-v1.8.15-*.zip` | — | 2.72 GB 合计 | Linux/Windows × CUDA 12.9/13.2（作者许可再分发） |
| `quickstart-linux.sh` / `quickstart-windows.ps1` | — | 小 | 一键部署（自动选 W8A16/BF16、注册 pi/rwkv-engine/rwkv-demos） |
| `rwkv-pi-demos.*`、`rwkv_vocab_v20230424.txt`、`SHA256SUMS.txt` | — | 小 | 演示与词表 |

> 整包 ≈**76 GB**（4×14.4 BF16 + 2×7.69 W8A16 + 引擎 2.72 + 杂项）。
> 部署要求：显存 ≥12 GB（W8A16 约 8.5 GB 占用，但模型卡/部署文档明确 **量化有精度损失**，显存允许建议 BF16 ≈14.2 GB）。

## 2. DSH 线：`RWKV7-DSH-7.2B`（带公开评测）

- **`RWKV7-DSH-7.2B-v0.1-adapter-r64.pth`：302.2 MB NoRA r64**（BF16），对公开基模
  `rwkv7-g1l-7.2b-20261031-ctx34304` 提取：**98.71% SVD energy 保留、0 个非目标 tensor diff**；
  可热加载到 `rwkv_lightning_cuda`（BF16 或 W8A16 base）
- 谱系：`g1l-7.2b-20261031` → `RWKV7-Agent-7.2B`（Stage 1 A-D）→ `RWKV7-DSH-7.2B`（本 adapter）

### 评测（模型卡原文，`k=1`, `max_steps=30`, auto-fold v2 + tolerant）

**私有长程 benchmark `PB-20261120-200-Coding`（200 题 / 2000 分）**：

| 模型 | 总分 / 2000 | 得分率 | PB-100-Edit | git-eval-35 | wspill-30 | codefix-15 | cf-eval-20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `rwkv7-g1l-7.2b-20261031`（base） | 279.16 | **13.96%** | 102.50 | 98.33 | 61.66 | 10.00 | 6.67 |
| `RWKV7-Agent-7.2B`（stage1abcd） | 728.33 | **36.42%** | 273.30 | 193.34 | 138.34 | 90.00 | 33.33 |
| **`RWKV7-DSH-7.2B-v0.1`** | **980.83** | **49.04%** | 419.13 | 243.35 | 178.33 | 100.00 | 40.00 |

→ base → DSH **3.51×**（直播说的"3 倍以上"很可能来自这里；但这是 **DSH 线 + 私有 benchmark**，不是 Pi 线的数字）。

**公开 Harbor benchmark（同口径）**：

| Benchmark | Tasks | 结果 |
|---|---:|---:|
| HumanEvalFix | 164 | **80/164 = 48.78%** |
| EditBench-zh | 108 | **24/108 = 22.22%**（valid 22.43%） |
| EditBench (en) | 108 | **19/108 = 17.59%**（valid 17.76%） |
| QuixBugs | 80 | **4/80 = 5.00%** |
| Aider Polyglot | 225 | **10/225 = 4.44%**（valid 5.03%） |

→ 相对 base 有明显提升，但**绝对值仍低**（Aider 4.4%、QuixBugs 5%），与 Terminal-Bench 0/8 同一量级的"agent 差距"。

## 3. `w1c2j3/rwkv-pi`（客户端）

- GitHub：**TypeScript**，created 2026-11-08，pushed **2026-11-27**，**★0，无 LICENSE**（API `license: null`；仅 `templates/LICENSE` 为 Apache-2.0 模板许可）
- 定位：把 RWKV 接入 Pi coding agent（`@earendil-works/pi-coding-agent`），Pi 的真实 loop/tools/sessions/terminal 不变，
  RWKV 通过 `rwkv_lightning_cuda` 以纯续写模型运行
- 关键设计：
  - **训练/服务逐字节一致**：同一 renderer + engine 原生 tokenizer 打包 SFT 数据（tokenizer 只走 Lightning 原生，不用 HF/irwkv/vLLM）
  - **Line-Edit v2 + tolerant edit**（v0.2 推荐；旧 v0.1 为 oldText/newText 协议）
  - 工具 read/write/edit/bash（grep/find/ls 可选）；重复失败/相同调用/单路径连续失败都有 hard limit
  - 插件：`strong-model` 教师接管（stall detector）、`subagents`
  - harness：真实 Pi + bubblewrap 沙箱；数据管线（Harbor lane、trajectory 打包）
- **代码仓只放代码**：README 明确"questions/trajectories/datasets/evaluation reports 留在私有存储"，
  训练与评测需要私有 artifact；因此 **Pi v0.2 的公开评测数字目前没有**（11-27 commit "report cumulative v0.2 demo pass rates" 的产物也未公开）

## 4. 公开数据集（RWKV-Agent-Lab）

| 数据集 | 内容 | 许可 | 规模 |
|---|---|---|---|
| `rwkv-pi-cot-trajectories-20261117` | Qwen/DeepSeek 历史合成轨迹 + CoT-cleaned v2 + CoT-compressed Open-SWE/SI2CA 子集 | **CC-BY-4.0** | **31,346** 条（29,143 train / 2,203 val）；组成 O2 19,353 + T3 8,524 + T1 1,094 + … |
| `rwkv-pi-bad-cases-20261118` | 从 37 次 PiRwkv 评测的 3,425 条非能力失败中抽取的 **100 条 bad cases** + Top-7 harness/state/protocol 失败分类 | **Apache-2.0** | 100 条（坏例 + on-policy repair queue） |

## 5. 判断与对我们的影响

### 5.1 是什么 / 不是什么
- **是**：目前公开的**最大规模 RWKV agent 模型族**（7.2B，4 个 BF16 + 2 个 W8A16 checkpoint，含 Pi/DSH 两条线、公开评测卡、一键部署、公开数据集）。
- **不是 RL**：训练路线是 SFT → anneal → DAgger（on-policy 纠错，监督式）/ Line-Edit v2；**没有 RLVR/GRPO 结果**。
  这与此前判断一致：公开 agent 成绩仍以 SFT 类为主。
- **"3×+" 的出处**：最接近的是 DSH 私有 benchmark 上 base 13.96% → 49.04%（**3.51×**），但 benchmark 私有、且是 DSH 而非 Pi 线；
  公开 Harbor 结果（Aider 4.4%、QuixBugs 5%）说明绝对能力仍有限。**不可把 3× 当作公开可复现的 benchmark 结论。**

### 5.2 与我们的实验对照
1. **接口方向一致**：Line-Edit v2 + tolerant edit + DAgger，正是我们 P3 负结果指出的"工具接口 + 行为修正数据"路线；
   我们当时用 answer-only RL 得到 tool-call shortcut，他们用 DAgger/接口改造绕过——两条路线可以互补。
2. **评测口径**：他们用私有 PB benchmark + Harbor 公开子集；我们 P4 若要对标，应优先选 **Harbor/Terminal-Bench** 类公开任务，
   避免私有 benchmark 的不可复现问题。
3. **规模差异**：这是 7.2B（14.4GB/ckpt）的 SFT 模型族；我们 1.5B 的 DAPO/SAO 是 **RL** 结果。两者只在"相对提升"层面可比，
   不能直接比较绝对分。
4. **许可**：模型权重 Apache-2.0（可用）；**rwkv-pi 客户端无 LICENSE**（只能读，不能复用代码）；
   lightning 引擎 zip 是"作者许可再分发"但上游仓库无 LICENSE；trajectories 数据集 CC-BY-4.0（需署名）、bad cases Apache-2.0。

### 5.3 待观察
- 3 个 slide 模型单仓何时转公开（当前 401），或官方是否会把它们作为独立仓库发布；
- Pi v0.2 的公开评测数字（目前只在私有侧）；
- 11-26 直播回顾（rwkv.cn 尚未发）；
- 7.2B 模型在 **RL（skyrl/skyrl-rwkv）** 上的后续（目前全是 SFT/DAgger 类）。

## 六、引用

- Bundle: https://huggingface.co/RWKV-Agent-Lab/RWKV7-Agent-7.2B-OpenSource
- DSH adapter: https://huggingface.co/RWKV-Agent-Lab/RWKV7-DSH-7.2B
- rwkv-pi: https://github.com/w1c2j3/rwkv-pi
- 数据集: https://huggingface.co/datasets/RWKV-Agent-Lab/rwkv-pi-cot-trajectories-20261117 ; https://huggingface.co/datasets/RWKV-Agent-Lab/rwkv-pi-bad-cases-20261118
- lightning engine: https://github.com/Alic-Li/rwkv_lightning_cuda
- 基模: https://huggingface.co/BlinkDL/rwkv7-g1
- 预告（11-26 直播）: https://www.rwkv.cn/news/read/23423445
