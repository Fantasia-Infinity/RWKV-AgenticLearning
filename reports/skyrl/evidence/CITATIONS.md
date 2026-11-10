# Evidence citations — skyrl/

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
| `00-env.md` | 794 | `f921d17b0fa94a80e47809f901979f41fb15fefe2e25570c4817076331abe5f4` |
| `01-ls-remote-skyrl-rwkv.txt` | 700 | `8105f5d684458e1c8ea9ad470756a700706c4b27081b904b55c886cb5d937020` |
| `02-ls-remote-vllm-rwkv.txt` | 15250 | `42a0a88c444392210d0d251b6b5dd0dee8b73742842eaf3f95b8f39752ae4970` |
| `03-ls-remote-helicopter.txt` | 143 | `db3fd9f09031ac654b38a22abe1a25596ea57fc37bc5ad2915e32490e567532a` |
| `04-api-repo-metadata.json` | 18560 | `6e9b202d7616ea5516c2f52591fffb6ba6b9a2eac5c093cc8d52b3e3277da8c4` |
| `05-branches-and-commits.txt` | 1545 | `a2581cefa47bc4eca935ef4d0e072dbcc4aecbb2494e691ed99334da397c8620` |
| `06-ci.txt` | 5583 | `f148b71f2bb56a15a2d92b435b1ee11623b4f8770189eb007abf18586d3bf926` |
| `07-rwkv-tests.txt` | 3029 | `88147fe6bc9d33772e2db7c7a0545014ab7d3cb92f6e34a930a0a45f3618eda6` |
| `08-pin.txt` | 2990 | `fd67ecf6dc96ce9f6c26e863c716af1e720c7f4875c172d75fbc15a7688b9bdd` |
| `09-multiturn-tlpo.txt` | 3709 | `84163c9578e6d2977154839c20d9aba3a44d64c8829c7f4e7743edd350c473e6` |
| `10-heli-branch.txt` | 6093 | `11efed5a9005bf13a5e10969a4baa36cfbaab04e7006ffe5eff559e8f37031e8` |
| `11-8gpu.txt` | 9540 | `7cb3181756ef22aaab31b748d89470a08b701df8e37ab90d6e2abca55898f14a` |
| `12-upstream-compare.txt` | 1235 | `69dfe2c0ca2669e264bb1feb74c3a3b151037191fa3de20cba4fcdfe593db5d3` |
| `13-quotes.txt` | 8126 | `d858a7b79c0850f7ab3d2ff3651fe528bca57d62102b817e045f38829f6342e2` |
| `14-web-checks.txt` | 1599 | `3a353c32b2da93678ffad42a491ce2251e64329926ce584ef154810f696766c4` |

## Archived originals (not distributed)

0 files, listed in [`ARCHIVED.tsv`](ARCHIVED.tsv) with size + sha256.

Source mapping:

- `07*` → https://github.com/rwkv-rs/skyrl-rwkv (README/CI/pin 等提取)

Default source: https://github.com/rwkv-rs/skyrl-rwkv · https://github.com/rwkv-rs/vllm-rwkv
