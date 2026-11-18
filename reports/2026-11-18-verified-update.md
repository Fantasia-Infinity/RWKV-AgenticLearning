# 2026-11-18 生态核验更新：any2rwkv 首个外部 PR、FlashRWKV2 0.2.0a1 迁移栈

> 核验时间：2026-11-18 11:20–12:00 CET。GitHub API / raw / atom 回源。
> 对应外部摘要：2026-11-18 日检。

## 一、已核验事实

### 1. `rwkv-rs/any2rwkv` 首个外部贡献（结构性变化，属实）
- **PR #2** `feat(qwen3.5): add opt-in signed GQA priming with adaptive heads`，作者 **`EntropyPhoton`**（社区账号），
  **merged 2026-11-17T14:54:05Z**，+1806/−4，6 文件
- 内容与日检一致：opt-in Qwen3.5 **GQA→RWKV7 priming**，自适应 K/V head 扩展 + 每 query head 一个 signed DPLR state；
  迁移 Q/K/V/O、QK norm、text partial RoPE、output gate，再加 token shift / learned decay-erase / first-GQA value residual /
  per-head readout；**初始化不保证 softmax 等价**（PR body 明说）；层内训练只动 GQA mixer、packed train/val、冻结 GDA adapter、
  strict delta ckpt、epoch resume、输出锁
- 实体文件确认：`docs/gqa2rwkv.md`（11,029B）、`docs/gqa_priming.md`、
  `src/any2rwkv/qwen2rwkv/qwen3_5/gqa2rwkv.py`（34,818B）
- **评审规范实际路径是 `.github/PR_REVIEW.md`**（另有 `AGENTS.md`），不是日检写的 `.agents/docs/pr-review.md`
- **`mla2rwkv.py` / `kda2rwkv.py` 仍 0 字节**（`docs/mla2rwkv.md`、`docs/kda2rwkv.md`、两个 .py 均 0）✅
- ⚠️ **该仓无 LICENSE**（API `license: null`）→ 按我们的许可政策：可读/设计参考，**不可复制代码**

### 2. FlashRWKV2 0.2.0a1 协调迁移（全部 open，尚未发布）
| 仓库 | PR | 内容 | 状态 |
|---|---|---|---|
| `rwkv-rs/FlashRWKV2` | **#29（P3）** | `refactor: replace runtime tuning profiles and simplify GPU CI`：移除 tuning session/磁盘 profile/fingerprint/lock/在线计时；删 `prepare_tuning`/`get_tuning_cache_dir`；根导出 23→21；stacked on #28 | **open** |
| `rwkv-rs/FlashRWKV2` | #28 | `perf: accelerate TileLang WKV7 and vocabulary head backward`（P1/#29 的基底） | **open** |
| `rwkv-org/irwkv` | **#22** | `[RWKV] Adapt native inference to FlashRWKV2 0.2.0a1` | **open** |
| `rwkv-org/irwkv` | **#23（P3）** | `[RWKV] Remove online tuning from inference with offline dispatch` | **open** |
| `rwkv-org/irwkv` | **#25** | `[RWKV] Default serving WKV state to FP16` | **open** |
| `rwkv-rs/vllm-rwkv` | **#86** | `[RWKV] Adapt serving to FlashRWKV2 0.2.0a1` | **open** |
| `rwkv-rs/vllm-rwkv` | **#87（P3）** | `[RWKV] Remove runtime tuning from serving` | **open** |
| `rwkv-rs/vllm-rwkv` | **#88** | `[RWKV] Default serving WKV state to FP16` | **open** |
| `rwkv-rs/transformers-rwkv` | **#26** | `fix(rwkv): support FlashRWKV2 0.2.0a1 training and deferred FP16 state` | **open** |

**修正**：`FlashRWKV2` 最新 release 仍是 **v0.1.0a19（2026-11-11）**，**0.2.0a1 尚未发布**；
所以"迁移"是**进行中的 PR 栈**，不是已落地版本。

### 3. FP16 serving vs FP32 rollout（已核验原文）
irwkv #25 body 原文要点：
- `mamba_ssm_cache_dtype="auto"` → **FP16 WKV state**；serving 示例用默认值
- **BF16 weights / activations / shift state，FP32 递推算术与 head logits**（沿用既有执行路径）
- **rollout instructions explicitly select FP32 recurrence**；显式 FP16 与 FP32 仍可选
- seeded 回归：eager 用显式 FP16，graph 用 auto；显式 FP32 用例继续覆盖 rollout 精度
→ 设计取舍与日检判断一致：serving 省显存 vs **RL rollout 保 logprob 数值保真**

### 4. 其他核验
- `lightning_cuda` **#25 已合并**：merged **2026-11-18T07:35:11Z**；#26（training packed BF16）**仍 open**
- `dsh-rwkv-plugin` tolerant-edit 集成：11-17 16:17 `fix(tolerant-edit): read fs via ctx.get...`、
  17:07 `feat: add auto-fold context mode and set empty-think + tolerant-edit...` ✅；默认仍为 line-edit
- **irwkv open PR = 8**：Cai-z-us 4（#20/#22/#23/#25）+ w1c2j3 3（#8/#21/#24）+ 社区 1（#12）
  → 日检"Cai-z-us 5 + w1c2j3 2 + 社区 1"计数有误
- **vllm-rwkv open = 5**（#85/#86/#87/#88/#50）✅
- `rwkv-agent-eval` 三个 Pi PR **第 7 天仍 open** ✅
- `rwkv-org/F-rwkv` 仍只有 LICENSE（11,357B）✅

## 二、对日检判定的评估

| 日检判断 | 评估 |
|---|---|
| "any2rwkv 首个外部贡献，评审规范→外部 PR→合并 7 天闭环" | ✅ 事实成立；修正文档路径为 `.github/PR_REVIEW.md`；补充：**该仓无 LICENSE**，外部贡献的代码不可按 Apache/MIT 复用 |
| "0.2.0a1 跨 4 仓库协调迁移" | ✅ PR 栈属实（4 仓 9 个 open PR）；修正：**0.2.0a1 尚未发布**，最新 release 仍 a19 |
| "serving 用 FP16、rollout 用 FP32" | ✅ 原文确认；这是 RL 侧最重要的设计点（重要性远超普通 perf PR） |
| "移除 runtime tuning = 可复现性" | ✅ 方向正确；但 PR 仍 open，需等合并后确认 |
| "lightning #25 已合并；tolerant-edit 合流" | ✅ 均属实；#26 仍 open，默认仍 line-edit |

## 三、对我们的影响

1. **精度分层直接关系 RL**：我们训练/评测用 vLLM-RWKV + FP32 state；若未来切到 irwkv/vLLM 新默认（serving FP16），
   rollout logprob 必须显式 FP32，否则 importance ratio 会因数值偏移失真——这与我们已知的
   "RWKV raw logprobs 要求未修改分布"是同一类约束。
2. **去 runtime tuning**：对我们"paired eval 可复现"是好消息；等 0.2.0a1 发布后再考虑 pin 升级（仍需 parity 测试）。
3. **外部贡献 + 评审规范**：说明该生态开始有正常治理流程；但 any2rwkv/lightning 均无 LICENSE，公开交付仍只能引用。
4. **无新 RL 分数**：58.7 基线不变，仍是 SFT。

## 四、引用

- any2rwkv PR #2: https://github.com/rwkv-rs/any2rwkv/pull/2
- any2rwkv 评审规范: https://github.com/rwkv-rs/any2rwkv/blob/main/.github/PR_REVIEW.md
- FlashRWKV2 #29: https://github.com/rwkv-rs/FlashRWKV2/pull/29
- irwkv #22/#23/#25: https://github.com/rwkv-org/irwkv/pulls
- vllm-rwkv #86/#87/#88: https://github.com/rwkv-rs/vllm-rwkv/pulls
- transformers-rwkv #26: https://github.com/rwkv-rs/transformers-rwkv/pull/26
- lightning #25: https://github.com/Alic-Li/rwkv_lightning_cuda/pull/25
