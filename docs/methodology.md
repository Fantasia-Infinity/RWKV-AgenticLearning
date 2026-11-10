# Methodology — how claims in this repository are produced and checked

This repository is an **evidence-first** audit. The rule is simple: a claim without a re-runnable check is not a
claim, it is an opinion. Every statement in `reports/` carries three things: **the command (or URL), the timestamp,
and the evidence file** it came from.

## 1. Evidence standard

| Element | Requirement |
|---|---|
| Reproducibility | The exact command is shown, or the exact URL + fetch time is given |
| Timestamp | UTC timestamps in every evidence file name and in report tables |
| Locality | Primary sources only: the repository itself (`git ls-remote`, raw files, commits), the model card, the official docs |
| Quotation limit | Short excerpts for identification/critique only; full third-party texts are not redistributed (see `THIRD_PARTY_NOTICES.md`) |
| Confidence mark | `✅` verified · `⚠️` partially verified or needs qualification · `❌` refuted |

## 2. Zero-API-quota policy

GitHub's unauthenticated API allows only 60 requests/hour, shared across a network. The tracker therefore avoids
`api.github.com` entirely:

| Need | Source used | Quota |
|---|---|---|
| Repository existence / default branch / all branches | `git ls-remote [--symref]` | 0 |
| Last commit time | `https://github.com/<owner>/<repo>/commits/<branch>.atom` | 0 |
| License detection, stars, description | repository HTML page (embedded JSON) | 0 |
| File contents | `raw.githubusercontent.com` | 0 |
| Full history / pin ancestry | `git clone --filter=blob:none` / `--depth` | 0 |

API quota actually consumed during the 2026-11-05 audit: **2 requests total** (one 404 check for the Helicopter
repository, one metadata call); everything else went through the paths above.

## 3. Source-of-truth hierarchy

1. **Code / repository state** — beats documentation, catalog entries, and blog posts.
2. **Official docs / model cards** — beats community summaries; recorded with fetch time and quoted briefly.
3. **Community catalogs and articles** — *clues only*. Any decision-relevant item must be re-verified against the
   repository (several catalog entries were wrong: mislabelled licenses, archived repos not marked, misleading names).
4. **Our own prior notes** — treated as untrusted until re-checked; the audit refuted or qualified 12 of them.

## 4. Re-verifying archived evidence

Each `reports/*/evidence/` directory contains:

- `CITATIONS.md` — what is published and where to re-fetch the archived originals;
- `ARCHIVED.tsv` — path, size, and **sha256** of every original that was removed from the public snapshot
  (full texts, HTML pages, commit feeds). Re-fetch and compare:

```bash
curl -sL https://raw.githubusercontent.com/xiaol/wkvm/main/README.md | sha256sum
# compare with the corresponding row in reports/state/evidence/ARCHIVED.tsv
```

## 5. Known limitations

- **Static analysis only**: no GPU training/evaluation was run for this audit. The "8-GPU feasibility" item is a
  static conclusion with explicit blockers, not a benchmark.
- **Snapshot semantics**: numbers (stars, last commit, branches) are as of 2026-11-05; the tracker is how to refresh
  them (`bash tracking/check.sh --diff`).
- **Language**: analytical reports are Chinese (original working language); repository-level docs are English.
- **Licensing**: several key sources have no license. Facts are still verifiable, but reuse of their code/text is
  restricted — noted per source in `THIRD_PARTY_NOTICES.md`.
