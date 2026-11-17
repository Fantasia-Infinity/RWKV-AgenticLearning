# 2026-11-17 生态核验更新：w1c2j3 状态管理 PR 集中提交 / XHarness 无法核实 / 编辑接口双解法

> 核验时间：2026-11-17 14:10–15:00 CET。GitHub API / raw / curl 回源。
> 对应外部摘要：2026-11-17 日检。

## 一、已核验事实

### 1. w1c2j3 的 4 个性能/接口 PR
| 仓库 | PR | 标题（原文） | 状态 | 创建 |
|---|---|---|---|---|
| `Alic-Li/rwkv_lightning_cuda` | **#25** | `perf(inference): reduce forward scratch and state-copy overhead` | **open** | 2026-11-17 |
| `Alic-Li/rwkv_lightning_cuda` | **#26** | `perf(training): optimize packed BF16 execution and safe gradient pruning` | **open** | 2026-11-17 |
| `rwkv-org/irwkv` | **#21** | `[Perf][RWKV] Batch 5D state-pool transfers without host synchronization` | **open** | 2026-11-17 |
| `No-22-Github/dsh-rwkv-plugin` | **#3** | `edit: add recall-tolerant edit mode with dual-anchor sliding guard and TS sync` | **closed（未 merge）**，内容以 11-17 commit 合入 main | 2026-11-17 |

PR #25 body 关键数字：forward arena channel-sized scratch 从 `31 * rows * C` 降到 `21 * rows * C`；
连续 state 切片用**一次 CUDA launch** 拷贝（vectorized FP16/FP32 state-slice copying + scalar fallback）。
PR #26 body：packed BF16 训练把**受监督行压紧**做 output-head/CE，并显式省略到不了冻结 embedding 的
layer-0 输入伴随量；其余含六路 BF16 time-mix 融合、去 WKV 反向递归 register copy、NoRA 投影/梯度 GEMM 特化。
→ 日检对 PR 内容的概括**属实**；但注意它们目前都是 **open（未合并）**，尚无合并后的基准数字。

### 2. `dsh-rwkv-plugin` 的编辑接口进展
- PR #3 作者为 **w1c2j3**，2026-11-17 09:04 关闭且未合并；同日 commit
  `edit: merge PR #3 tolerant-edit mode with line-edit default and TS sync...` 把内容合入 main
- 实际能力：在标准 `edit_file` 之上加 **`editMode: 'tolerant'`（内容锚点 + 双锚点滑动保护，容忍缩进/空行/空白漂移）**，
  可实时在 `tolerant` / `line-edit`（`edit_lines`）/ `literal` 间切换；**默认仍是 line-edit**
- 11-16 的 commit 也确认：`worklist: add stateful work list, full-CoT history, non-withdrawn budget...` 等已合入
→ 日检"编辑接口双人共演"判断成立；但注意**默认未改变**（line-edit 仍是默认，tolerant 是可选模式）。

### 3. irwkv 4 个 open PR（已核对）
- **#21** w1c2j3（11-17，state-pool 批量化，无 host 同步）
- **#20** Cai-z-us（11-16，`fix(rust): render long chats with the upstream template policy`）
- **#12** Triang-jyed-driung（11-07，better state management）
- **#8** w1c2j3（10-31，keep the state before the chat generation prompt）
→ 日检"4 个 open PR"属实。

### 4. vLLM 上游 issue：**归属需修正**
- **#68081 `[Bug]: MTP speculative decoding is a net performance negative on Qwen3.5/3.8 hybrid`：
  作者确为 `123213213weqw`**，2026-11-17 创建 ✅
- #49497 作者 `Dhruv235`、#36010 作者 `NilsHellwig`、#36077 作者 `yufangbo`；
  这三个 issue 的公开页面 HTML 中 **`123213213weqw` 出现 0 次**（无署名、无可查评论）
→ 日检把 4 个 issue 并列成"他的 6 个 issue"**不准确**：目前只能确认 #68081 由他提交；
其余需说明"参与/评论"来源，否则应删去。

### 5. `x-harness-rs` → `XHarness` 改名：**无法核实**
- 实测（GitHub 连通性正常，对照 `dsh-rwkv-plugin`/`FlashRWKV2` 均 200）：
  - `https://github.com/123213213weqw/x-harness-rs` → **404**
  - `https://github.com/123213213weqw/XHarness` → **404**
  - `https://github.com/123213213weqw`（用户页）→ **404**
- 结论：公开 GitHub 上**账号/仓库目前不可见**（转私有、改名后旧链不重定向、或删号均可能）。
  日检的"301 永久重定向到 XHarness、★16、今天推中文 UI 提交、仓库数 90→99"**均无法回源确认**；
  若是重命名，旧 URL 通常应 301 而非 404——因此更可能是**转私有/删号**，而非单纯改名。
  建议在跟踪文件里标记"未核实"，不要沿用 ★16/新名。

### 6. 其他核验
- `rwkv-agent-eval` 三个 Pi PR **仍 open**（#1/#2/#3，2026-11-12 创建，第 6 天）✅
- `rwkv-org/F-rwkv` **仍只有 LICENSE**（11357B）✅
- `any2rwkv` MLA/KDA 四个文件 **仍 0 字节** ✅
- `rwkv-rs` org public repo **39 个**（未变）✅

## 二、对日检判定的评估

| 日检判断 | 评估 |
|---|---|
| "w1c2j3 一天内 5+ PR，全部指向 state 拷贝/同步/分配开销" | ✅ 事实层面对（4 个 PR 均在 state/scratch/同步上）；但**全部 open 未合并**，"瓶颈被证实"应改为"被这些 PR 的 body 论证/针对"，等合并+基准才算证实 |
| "编辑接口双人共演" | ✅ 成立（line-edit vs tolerant dual-anchor）；补充：默认仍 line-edit，tolerant 可选 |
| "w1c2j3 开始给 No-22 的插件提 PR，两条线开始协作" | ✅ 成立（PR #3 作者 w1c2j3，内容已入 main） |
| "123213213weqw 在 vLLM 上游的 6 个 issue" | ⚠️ 只核实 1 个（#68081）；列表里另外 3 个是他人 issue |
| "x-harness-rs 改名 XHarness（301）" | ❌ 无法核实：新旧 URL 与用户页均 404；更像转私有/删号 |
| "RL rollout 瓶颈在状态管理" | 🟠 方向合理（state copy/sync/alloc 是 RNN 异步 rollout 的已知成本），但本轮证据是 open PR 的论证，不是实测基准 |

## 三、对我们项目的影响

1. **如果 #25/#26/#21 合并**，异步 rollout 的 state 开销会下降，这对我们 RL 线的吞吐/成本是直接利好；
   我们栈（skyrl + vLLM-RWKV）不用 lightning/irwkv 的 state-pool，短期受益有限，但可作为 P4 异步方案的参考。
2. **编辑接口**：tolerant/dual-anchor 是"编辑失败 27.7%"问题的第二解；我们自己的多轮工具 RL 负结果里同样有
   "重复调用/格式失败"成分，值得在后续工具环境里对比 line-based vs tolerant edit 的失败率（不现在跑）。
3. **信息卫生**：XHarness 与 vLLM issue 两处说明日检在"归因/可见性"上会出错；我们的 tracking 继续坚持
   "回源 + 标注未核实"，不直接采纳二手结论。

## 四、引用

- lightning #25: https://github.com/Alic-Li/rwkv_lightning_cuda/pull/25
- lightning #26: https://github.com/Alic-Li/rwkv_lightning_cuda/pull/26
- irwkv #21: https://github.com/rwkv-org/irwkv/pull/21 ；#20: https://github.com/rwkv-org/irwkv/pull/20
- plugin #3: https://github.com/No-22-Github/dsh-rwkv-plugin/pull/3
- vLLM #68081: https://github.com/vllm-project/vllm/issues/68081
- eval PRs: https://github.com/rwkv-org/rwkv-agent-eval/pulls
