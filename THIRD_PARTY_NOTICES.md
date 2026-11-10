# Third-party notices

This repository's **own** content (reports, trackers, docs, scripts) is licensed under
[Apache-2.0](LICENSE).

Third-party material is treated as follows:

- We **do not redistribute full texts** (READMEs, model cards, HTML pages, commit feeds, source files) of third-party
  projects. Removed originals are recorded in `ARCHIVED.tsv` files inside each `reports/*/evidence/` directory with
  size + **sha256**, so anyone can re-fetch the original from the cited URL and verify it byte-for-byte.
- Short quotations and factual data points (versions, commit SHAs, dates, file counts, benchmark numbers) are included
  for identification, review, and commentary. Copyright remains with the original authors.
- Where a source has **no license**, we only quote short factual excerpts and never reproduce its full text; such
  material should not be reused commercially without the authors' permission.

## Sources referenced (by license)

| Source | License | What appears here |
|---|---|---|
| [rwkv-rs/skyrl-rwkv](https://github.com/rwkv-rs/skyrl-rwkv) | Apache-2.0 | version pins, CI/workflow names, short quotes, branch/commit data |
| [rwkv-rs/vllm-rwkv](https://github.com/rwkv-rs/vllm-rwkv) | Apache-2.0 | pin commit, repo metadata |
| [rwkv-rs/verl-rwkv](https://github.com/rwkv-rs/verl-rwkv) | Apache-2.0 | file lists, engine/paths; `evidence/04-verl-rwkv/` retains small verbatim excerpts under this license |
| [TimeMobius/RWKV-Megatron](https://github.com/TimeMobius/RWKV-Megatron) | Apache-2.0 | branch/config references, benchmark numbers |
| [Joluck/RWKV-PEFT](https://github.com/Joluck/RWKV-PEFT) | Apache-2.0 | feature/PEFT facts |
| [BlinkDL/RWKV-LM](https://github.com/BlinkDL/RWKV-LM) | Apache-2.0 | G1x prompt-template excerpt (`evidence/09-official/`) |
| [rwkv-rs/FlashRWKV2](https://github.com/rwkv-rs/FlashRWKV2) | MIT | license/version facts |
| [rwkv-rs/lm-evaluation-harness-rwkv](https://github.com/rwkv-rs/lm-evaluation-harness-rwkv) | MIT (fork of EleutherAI harness) | benchmark config facts |
| [rwkv-rs/lighteval-rwkv](https://github.com/rwkv-rs/lighteval-rwkv) | MIT (fork of HuggingFace lighteval) | branch/activity facts |
| [rwkv-rs/evalscope-rwkv](https://github.com/rwkv-rs/evalscope-rwkv) | Apache-2.0 (fork of ModelScope evalscope) | branch/activity facts |
| [rwkv-rs/torchtitan-rwkv](https://github.com/rwkv-rs/torchtitan-rwkv) | BSD-3-Clause (fork of PyTorch torchtitan) | RWKV file facts |
| [xiaol/wkvm](https://github.com/xiaol/wkvm) | **No license file** | short factual excerpts only (performance numbers, endpoints, claim-ledger facts) |
| [rwkv-rs/browsecomp-plus-eval](https://github.com/rwkv-rs/browsecomp-plus-eval) | **No license** | package facts (830 questions, agent loop) only; full README archived, not published |
| [No-22-Github/RWKV-Agent](https://github.com/No-22-Github/RWKV-Agent) + HF assets | **No license** | benchmark numbers (568 questions, 32.9%, 56.4%) and dataset facts only |
| [rwkv-rs/rwkv-skills](https://github.com/rwkv-rs/rwkv-skills) | **No license** | one quoted sentence about the scoreboard; no full text |
| [RWKV-Vibe/rwkv_lightning](https://github.com/RWKV-Vibe/rwkv_lightning) | **No license** | license-status fact only |
| [scarletwolf_ai/rwkv-toolcaller-bench](https://codeberg.org/scarletwolf_ai/rwkv-toolcaller-bench) | Apache-2.0 | benchmark facts |
| [rwkv.cn](https://www.rwkv.cn/) official documentation | © RWKV / 元始智能 | short excerpts (function-call format) |
| HuggingFace model cards (`RWKV/*`, `BlinkDL/*`, `No-22/*`) | per-model | short factual excerpts; no full card reproduction |
| GitHub organization pages and commit feeds | — (factual metadata) | repository lists, dates, commit SHAs |

If you believe a quotation here exceeds fair-use/commentary bounds, please open an issue and it will be removed or
shortened.
