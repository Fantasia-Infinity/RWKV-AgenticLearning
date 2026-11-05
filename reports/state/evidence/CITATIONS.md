# Evidence citations — state/

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
| `01_lsremote_20261105T200837Z.txt` | 910 | `c0678841e53fe9d270feedb0d0bee21dcc887782281b2002d0bcb2898af33fe5` |
| `02_atom_wkvm_20261105T200845Z.txt` | 2040 | `a002a4f25beff3b7c77c8584cc88704e534c7c9d7cf95301c794263421462edd` |
| `03_helicopter_rwkvskills_20261105T200908Z.txt` | 2921 | `7b911c77d099a4b3803e634117742217da925da076aa5fd1aca9dfabdc16cb57` |
| `04_wkvm_structure_20261105T200938Z.txt` | 8322 | `8207a825ddf31f6895d9b9a233ec3429e0a324f18f8feddb82b4d7c53f84e382` |
| `04b_wkvm_tracked_files_CLEAN_20261105T201614Z.txt` | 20907 | `81fb9d3e6e11758591da90ac118e057d99e684154b3547984980c48bfefe6ad1` |
| `05_wkvm_models_rwkv7_20261105T200952Z.txt` | 4756 | `20bcf3301c9a902cfc479ed92d4e1ac644262afb53bc5a7a79ef05871449f108` |
| `06_wkvm_rwkv7_layout_bench_20261105T201000Z.txt` | 18533 | `bacd150ca3c8d28b9b9817668d2b39f142559a9cbc81ace17e9ca439bf6e9f2d` |
| `08_wkvm_rwkv_bench_artifacts_20261105T201019Z.txt` | 12071 | `f65f57e67c82fca517e4d45c99b5521d42f022d801aa4eb49ec1a0a28ba35761` |
| `09_wkvm_api_capabilities_20261105T201031Z.txt` | 9891 | `98ea5546a9340063bc0cbc376beb51c56ea5cb125faa41f905a8af26b25558f7` |
| `10_wkvm_branches_20261105T201038Z.txt` | 5842 | `2a523fd01c791f614fa94812ffcd24266751d1ff6e7abf3ce026eac036c0ac8e` |
| `11_wkvm_activity_license_migrate_20261105T201051Z.txt` | 7164 | `6cda507384c656fba61d28aa37a17a947f14ce6196a5eb6defc83a5de99eac1b` |
| `12_wkvm_paper_license_scripts_20261105T201103Z.txt` | 5538 | `fc3a38fe504c9e987da5b48498efbe8bec631871241a69218c55aae9ecf17bc4` |
| `20_megatron_28b_head_20261105T201112Z.txt` | 4804 | `1933e4c531b2c5f5f8ff33cdff38050cf6293eddec02fbf75e4bac30d9bc423c` |
| `21_megatron_28b_docs_20261105T201117Z.txt` | 20151 | `396047ec1b2257440c3bab4ec2a17bc5a7947d0879845665b513ee03f2080626` |
| `22_megatron_28b_inventory_20261105T201127Z.txt` | 4574 | `3ff155b12a246aacc7f84b630ca2b7b36909585a40040b78a4e6f5f006c46954` |
| `23_megatron_atom_feeds_20261105T201129Z.txt` | 6597 | `e88639f470b6aab4b524b985d36967656341a2b0e74d6d1479aa970f6e76b4bf` |
| `25_megatron_28b_configs_20261105T201153Z.txt` | 14562 | `4e842c4ee4cd27004c98b4cf9456b7292c1eaa794217f668a8c7e3b50c597486` |
| `26_megatron_28b_artifacts_20261105T201202Z.txt` | 7657 | `e22a19d9c7b359444fed6360ef9423634880570ce46d6b94a303caffeca4a852` |
| `27_megatron_other_branches_20261105T201216Z.txt` | 8444 | `13b7f7276d71f60bed950b7ae56ba9128c845828e7ec4154832fbb2a61b1dffb` |
| `28_megatron_cp_testing_status_20261105T201234Z.txt` | 24626 | `78641b0dbf6e9ea438f1ab3ffa154518bcfe1518c07509b150aacbf42abf7bbe` |
| `29_megatron_cp_28b_evidence_files_20261105T201247Z.txt` | 14738 | `3c1d5d6d24b86b30dba9261dbcfb6b39f91f84c32ac6c804933e0da89ea90382` |
| `30_helicopter_probes_20261105T201303Z.txt` | 1722 | `cf515e31f8eb9ce69f72caaf77e78d723da8df032f936e721f0dc6d0a0796b27` |
| `31_helicopter_siblings_20261105T201320Z.txt` | 5663 | `8b69a0e7f82a28b40b0ffdf626ab1f4ed3d46b6dd62b42843c49487bb38a52ad` |
| `32_helicopter_scoreboard_rwkvskills_20261105T201331Z.txt` | 8148 | `c2753b16f338fcdc539140126d9111c34fdfb9dac48ac2de75faaac51a673abb` |
| `33_helicopter_traces_20261105T201345Z.txt` | 6614 | `95d19408e152aafdeeddfeedf4743d937f8540a54eca1eea5a7aca84499e8952` |
| `34_helicopter_codeberg_grepapp_20261105T201349Z.txt` | 2875 | `ac955021772b93ebc86fee1fc2f6e7a7137f0d77260b653fb38bab7ccb8edce5` |
| `35_helicopter_leaderboard_doc_20261105T201430Z.txt` | 1160 | `ab43899dce6f39165ceb8d39f361016316c8b2e9ad073e53df13ba761b627394` |
| `36_license_spotchecks_20261105T201435Z.txt` | 2956 | `60cfce78a78c91e774b3897cbb82b528735b7a235bddb0e784f5aa324c347c20` |
| `37_license_final_20261105T201451Z.txt` | 891 | `591cf6e3da87b728b3639134548c9200b97c8f87352ef26d2574b849cc16d926` |
| `38_license_tree_listings_20261105T201502Z.txt` | 2877 | `159a1205ebcdffb6be52a92489a5865c60b4520bebec52d3bd71345498e845e1` |
| `39_residual_checks_20261105T201523Z.txt` | 1754 | `9fe67cb78d749ba3acd8a0f4b6ed066f9a341d1ef83c573fe4e09901fdf1d75c` |
| `40_final_megatron_checks_20261105T201534Z.txt` | 2889 | `f87d0e215a4542d9dfeaff846be7767344e0f3ce5ade1033b98a762cc96600a2` |
| `41_citation_verification_20261105T202011Z.txt` | 3556 | `b4cb64af44a71569a5c0c777c3fa0de01c640c5e838c0201ed42ff43b1ea3042` |
| `42_reverify_20261105T202033Z.txt` | 1210 | `07d201069335fdaa1ff7eb43501e2791d2f8fe2be588127a20111ea6c1e01a74` |
| `KEY-FACTS_20261105T201626Z.txt` | 30061 | `0e6372b1ed1df0f0a75c41460bebeb922d4d45f9593c734d675d08cb24a51d6e` |

## Archived originals (not distributed)

3 files, listed in [`ARCHIVED.tsv`](ARCHIVED.tsv) with size + sha256.

Source mapping:

- `07_wkvm_README_full*` → https://raw.githubusercontent.com/xiaol/wkvm/main/README.md
- `24_megatron_28b_README*` → https://raw.githubusercontent.com/TimeMobius/RWKV-Megatron/codex/qwen-rwkv28b-distill/README.md

Default source: https://github.com/xiaol/wkvm · https://github.com/TimeMobius/RWKV-Megatron
