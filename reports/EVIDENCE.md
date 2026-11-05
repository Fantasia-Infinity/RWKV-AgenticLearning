# Evidence — policy, layout, and how to re-verify

This repository is evidence-first: every finding in `reports/` points to a file or a command output here.
To keep the public snapshot redistributable, **full third-party texts are not published**; only our own command
outputs, structured metadata, and short quotations are included.

## Layout

```
reports/
├── 2026-11-05-verification.md     # summary report
├── skyrl/REPORT.md  + skyrl/evidence/   # 15 files kept, 0 archived
├── state/REPORT.md  + state/evidence/   # 35 files kept, 3 archived
└── eco/REPORT.md    + eco/evidence/     # 33 files kept, 194 archived
```

Each `evidence/` directory contains:

| File | Meaning |
|---|---|
| `CITATIONS.md` | what is published, what was removed, source URL mapping, re-fetch examples |
| `ARCHIVED.tsv` | `path`, `size`, `sha256` of every removed original (third-party full texts, HTML pages, commit feeds) |
| kept files | command outputs (`.txt`), structured metadata (`.tsv`, `.json`), short excerpts (`.md`) |

## Re-fetch and verify

```bash
# 1) pick a row from an ARCHIVED.tsv
grep '07_wkvm_README_full' reports/state/evidence/ARCHIVED.tsv

# 2) re-fetch the original and compare
curl -sL https://raw.githubusercontent.com/xiaol/wkvm/main/README.md | sha256sum
```

GitHub usage in the audit: **2 API calls total**; everything else came from `git ls-remote`, `commits.atom`,
`raw.githubusercontent.com`, and GitHub HTML — see [`../docs/methodology.md`](../docs/methodology.md).

## Reproducing the audit

```bash
# full tracker snapshot (≈90 s, zero API quota)
bash tracking/check.sh

# delta since the previous snapshot
bash tracking/check.sh --diff
```

The reports were produced by shallow clones under `repos/` (not committed; gitignored). Recreate any of them with:

```bash
git clone --depth 1 https://github.com/rwkv-rs/skyrl-rwkv
```
