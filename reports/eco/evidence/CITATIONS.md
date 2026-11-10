# Evidence citations — eco/

# Evidence policy & citations

This directory contains **only evidence that can be redistributed**: command outputs produced by this project,
structured metadata (TSV/JSON), and short quotations needed to support the findings.

What is **not** published here (and why):

- Full copies of third-party READMEs, model cards, HTML pages and commit feeds are **not redistributed**;
  they remain the property of their authors and are kept only in a private archive on the maintainer's machine.
- Every removed file is listed in `ARCHIVED.tsv` with its path, size and **sha256** so anyone can re-fetch the
  original from the cited URL and verify it byte-for-byte.
- Full-text reproduction is unnecessary for verification and would raise copyright questions, especially for
  sources without a license.

Re-fetch examples:

```bash
# last commit time of a repo
curl -s https://github.com/rwkv-rs/skyrl-rwkv/commits/main.atom | head
# raw README (compare sha256 with ARCHIVED.tsv)
curl -sL https://raw.githubusercontent.com/xiaol/wkvm/main/README.md | sha256sum
```


## Published evidence files

| File | Bytes | sha256 |
|---|---|---|
| `01-org/org-repos-40-merged.tsv` | 5629 | `0b5ad8d3003ce42aa040946b4c1d2329107813f5cf842e894595b4b15e34a1eb` |
| `02-atoms/branch-commit-summary-2.tsv` | 1679 | `29253be1b8359eefba18c5aed4c2ed3429e201137340ae46857bf240fbc4e4d1` |
| `02-atoms/branch-commit-summary.tsv` | 4350 | `36a92dfa72a2d9c1cf9c6f216a7773e48c3ffe3ad037bdaded12039eb7acfa64` |
| `02-atoms/commit-summary.tsv` | 3116 | `3d94593c39ecc1cfc62d10883409d81730c23626e2249bb29bfc3f3cde25ba16` |
| `03-repo-pages/repo-created.tsv` | 4835 | `726e2d42887dc5f0a6b28b2444def652c269cb4d43faa25ee5a1fce9d24d8e9a` |
| `04-verl-rwkv/engine-rwkv_lm-README.md` | 672 | `af568c202d93e6581a6ca93939f558d64dbb38914ec863db6e50dbd70b99da89` |
| `04-verl-rwkv/examples-rwkv_trainer-config-README.md` | 3873 | `80b114c816e6ed3adf61b335bf8a3ebff29d113bd2a45c3a45c3d110fcab89e3` |
| `04-verl-rwkv/head-commit.txt` | 126 | `aa145578f5de908bad4b5d28198fc71db82cd58ab5d3f11cfe722b7240c4e51e` |
| `04-verl-rwkv/maxrl.py` | 24939 | `1bc8b96409675ba1f9bdd0bc233ffb46be54362eb0f78d2e633e9f7c5de11df3` |
| `04-verl-rwkv/models-rwkv-README.md` | 645 | `4cfb80dce508b6983476ed7a5d8839f45c26b841a859a67460ae24f1793739eb` |
| `04-verl-rwkv/rebase-rwkv.yml` | 7807 | `5df5e389418d8d4cbb4e2b0f61b07ca9192abab763cc2c7f4fc623f57bc6ad54` |
| `04-verl-rwkv/refs-heads.txt` | 230 | `34c1f59991743c07da075054a85d2da9271eee6003e2e57e8032b1d39f14cf6f` |
| `04-verl-rwkv/run_rwkv7_grpo_rwkv_lm.sh` | 8931 | `a44fa29ecc925342efbe0591bc303e61dbf0b88abb5dcde7fd6b7db62ae5ae3c` |
| `04-verl-rwkv/rwkv-files.txt` | 1979 | `f5608d27d1a52524ce3654d960e855e91cb882b52c18b08ed9031ad81a886353` |
| `04-verl-rwkv/tree.txt` | 54623 | `9a0d5d96050599779232cb847135486b571a745a8f7b48120b8dd1035ea53d40` |
| `04-verl-rwkv/upstream-tree.txt` | 59304 | `7a7e5c78256ef61981c58a2f062def0775c0475e557b2584fa182f0bfde04218` |
| `06-eval-infra/benchmarks.toml` | 401 | `28b15830f58ec2e72042ef7782fe18d805312066c23d38b5da0d4c10f8b2c4a5` |
| `06-eval-infra/branch-summary-evalscope-lmeval.tsv` | 4350 | `36a92dfa72a2d9c1cf9c6f216a7773e48c3ffe3ad037bdaded12039eb7acfa64` |
| `06-eval-infra/lm-eval-scoreboard-files.txt` | 247 | `e15733c29a51c3e0caacde9f0c28400a39854210487e74b3dccfd9616f575f9b` |
| `07-ecosystem-no22/agent-exam-versions.json` | 1635 | `504b9b823acf47246e39ea27b33e6dd2bd41dc9a7bea78b1a73425fbbf3f7811` |
| `08-hf/api/blinkdl-g1.json` | 2784 | `6b18495e229fae457869e441780c63a70061c2643ee11c1f6f0c39ee646f32f2` |
| `08-hf/api/g1l.json` | 6379 | `3b5592cc7768f61c0a99bd4524e33ae0f34091ab8ef007d48528b49f5f78d445` |
| `08-hf/api/no22-agent-exam.json` | 129335 | `846cda5f68469797ab4dd4c5359651459990cb872811b7d1148d65878dc6ec9b` |
| `08-hf/api/no22-agent-weights.json` | 1542 | `71fd34d9c329d05b79862ed92b40a20e88d6f1838e9ca8898a99c093e8e4aebe` |
| `09-official/RWKV7-G1x-templates.txt` | 2280 | `21dd0a38bc907c1d070742c19a8f83fcc57eec462f62dfabb84569851256d441` |
| `09-official/rwkv-vibe-org-repos.txt` | 377 | `b61e7d15e3b9a3c508fdf13a05b92964e67ff0aac02ece07048b361e44cce62b` |
| `09-official/rwkv.cn-lightning-excerpts.md` | 2262 | `9dd8ba1dbd91f3891f8edbf8680643d536c77ea977d1f3ba1f9954284789f4fc` |
| `09-official/rwkv.cn-promptformat-excerpts.md` | 932 | `22f8095cd4fb789f72f83d4ec91556229552d91456aa7e29aca3d5b98cec3edf` |
| `10-checks/helicopter-check.txt` | 378 | `ef02525feb7d5fdacc110d141a7aee1a9d667e752a0c1a6a793cc96c2d91c5e9` |
| `10-checks/rwkv-skills-branches.txt` | 313 | `640fd3d54961ea4de23aa35fe40cae6b09f9922b98d15d2a9af7a1db80887089` |
| `10-checks/verl-upstream-rwkv-count.txt` | 224 | `e60560124443788c7d14c0dca873411c25a973af6eadf680e0322fe95099c353` |
| `10-checks/wx-cli-451.txt` | 365 | `2bb0408ff719d7131bcc8b083f2c53bed36cf1698571173f2ef445baa837d23b` |
| `org-repos-embedded-json.json` | 21566 | `2475257c1baa4def3b3b0cf92e5fc85bf8980695c1935441cc633fb9d5281bce` |

## Archived originals (not distributed)

194 files, listed in [`ARCHIVED.tsv`](ARCHIVED.tsv) with size + sha256.

Source mapping:

- `01-org/*` → https://github.com/orgs/rwkv-rs/repositories (HTML)
- `02-atoms/*` → https://github.com/<owner>/<repo>/commits/<branch>.atom
- `03-repo-pages/*` → https://github.com/<owner>/<repo> (仓库页 HTML)
- `05-browsecomp/*` → https://github.com/rwkv-rs/browsecomp-plus-eval (包内 README/MANIFEST)
- `06-eval-infra/*` → git diff 于 rwkv-rs/{lm-evaluation-harness-rwkv,torchtitan-rwkv,evalscope-rwkv} 侧分支
- `07-ecosystem-no22/*` → https://github.com/No-22-Github/RWKV-Agent (README/评测报告)
- `08-hf/*` → https://huggingface.co/<model-or-dataset> (API JSON / 模型卡 README)
- `09-official/*` → https://www.rwkv.cn/ · https://github.com/BlinkDL/RWKV-LM
- `11-repos/trees/*` → `git ls-tree -r` 于 rwkv-rs 各仓库
- `11-repos/readmes/*` → https://raw.githubusercontent.com/<owner>/<repo>/<branch>/README*
- `org-repos-page*` → https://github.com/orgs/rwkv-rs/repositories (HTML)

Default source: 见 reports/eco/REPORT.md 内显式 URL
