#!/usr/bin/env bash
# RWKV 生态跟踪快照 —— 零 GitHub API 调用。
#   数据来源: git ls-remote (HEAD/分支) / commits atom feed (最后提交) / GitHub HTML (LICENSE 探测+描述+stars)
# 用法:
#   bash tracking/check.sh            # 采集一轮快照 -> tracking/runs/<UTC时间>.md|.tsv
#   bash tracking/check.sh --diff     # 采集后与上一轮比较, 只打印变化
#   bash tracking/check.sh --deep     # 额外核验已知 pin 的 commit 是否存在于历史(需 clone, 较慢)
# 输出同时写 stdout。
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIST="$ROOT/tracking/repos.txt"
RUNDIR="$ROOT/tracking/runs"
DIFF=0; DEEP=0
for a in "$@"; do case "$a" in --diff) DIFF=1;; --deep) DEEP=1;; esac; done
mkdir -p "$RUNDIR"
TS="$(date -u +%Y-%m-%dT%H%M%SZ)"
MD="$RUNDIR/$TS.md"; TSV="$RUNDIR/$TS.tsv"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

now_date="$(date -u +%Y-%m-%d)"
declare -a REPORT=()
missing=0; total=0

# --- 采集单个仓库 ---
collect() {
  local repo="$1" want_branch="$2" note="$3"
  local branch="" head="" last="" lic="NONE" stars="" desc="" nheads=0

  local lsout
  lsout="$(timeout 30 git ls-remote --symref "https://github.com/$repo" HEAD 2>/dev/null)" || {
    REPORT+=("${repo}|—|—|MISSING|—|${note}"); return 1; }
  branch="$(echo "$lsout" | awk '/^ref:/{print $2}' | sed 's#refs/heads/##')"
  head="$(echo "$lsout" | awk '/^[0-9a-f]{40}/{print $1; exit}')"
  [ -n "$want_branch" ] && branch="$want_branch"

  # 分支数(轻量二次 ls-remote)
  nheads="$(timeout 30 git ls-remote --heads "https://github.com/$repo" 2>/dev/null | wc -l)"

  # 最后提交时间: atom feed
  last="$(timeout 25 curl -s "https://github.com/$repo/commits/$branch.atom" 2>/dev/null | grep -o '<updated>[^<]*' | head -1 | sed 's/<updated>//')"
  [ -z "$last" ] && last="?"

  # HTML: LICENSE 文件 + 描述 + stars
  if [ -z "$note" ] || [ "$note" = "-" ]; then
    timeout 25 curl -s "https://github.com/$repo" -o "$TMP/page.html" 2>/dev/null
    if [ -s "$TMP/page.html" ]; then
      local cand
      cand="$(grep -o 'title="LICENSE[^"]*"' "$TMP/page.html" 2>/dev/null | sed 's/title="//;s/"$//' | sort -u | grep -v '^LICENSES$' | tr '\n' ' ')"
      for licname in $cand; do
        local body
        body="$(timeout 20 curl -s "https://raw.githubusercontent.com/$repo/$branch/$licname" 2>/dev/null)"
        case "$body" in 404:*|"") continue;; esac
        lic="$(printf '%s' "$body" | head -c 60 | tr '\n' ' ' | tr -s ' ')"; break
      done
      desc="$(grep -o '<meta name="description" content="[^"]*' "$TMP/page.html" 2>/dev/null | head -1 | sed 's/.*content="//' | cut -c1-90)"
      stars="$(grep -o 'stargazerCount\":[0-9]*' "$TMP/page.html" 2>/dev/null | head -1 | cut -d: -f2)"
    fi
  fi
  [ -z "$lic" ] && lic="NONE"
  [ -z "$stars" ] && stars="?"
  [ -z "$desc" ] && desc="-"

  REPORT+=("${repo}|${branch}|${head:0:9}|${last}|${lic}|${nheads} branches|${stars}★|${desc}")
  return 0
}

# --- 读清单 ---
while IFS= read -r line; do
  line="${line%%#*}"; line="$(echo "$line" | sed 's/[[:space:]]*$//')"
  [ -z "$line" ] && continue
  repo="$(echo "$line" | awk -F'|' '{gsub(/[[:space:]]/,"",$1); print $1}')"
  branch="$(echo "$line" | awk -F'|' '{if (NF>=2) {gsub(/[[:space:]]/,"",$2); print $2}}')"
  note="$(echo "$line" | awk -F'|' '{if (NF>=3) {sub(/^[[:space:]]+/,"",$3); print $3}}')"
  total=$((total+1))
  collect "$repo" "$branch" "$note" || missing=$((missing+1))
done < "$LIST"

# --- 特殊检查 ---
special=""
if timeout 20 git ls-remote "https://github.com/rwkv-rs/Helicopter" >/dev/null 2>&1; then
  special="${special}- rwkv-rs/Helicopter: **存在** (此前 404)\n"
else
  special="${special}- rwkv-rs/Helicopter: 404 / 不存在（$(date -u +%Y-%m-%d) 复验）\n"
fi
wkvm_lic="$(timeout 20 curl -s -o /dev/null -w '%{http_code}' https://raw.githubusercontent.com/xiaol/wkvm/main/LICENSE)"
special="${special}- xiaol/wkvm LICENSE: HTTP ${wkvm_lic}（404 = 仍缺许可证）\n"
skyrl_lic="$(timeout 20 curl -s -o /dev/null -w '%{http_code}' https://raw.githubusercontent.com/rwkv-rs/skyrl-rwkv/main/LICENSE)"
special="${special}- skyrl-rwkv LICENSE: HTTP ${skyrl_lic}\n"

if [ "$DEEP" = "1" ]; then
  special="${special}- [deep] skyrl pin 67f0c599 是否在 vllm-rwkv 历史中: "
  if timeout 180 git clone -q --bare --filter=blob:none "https://github.com/rwkv-rs/vllm-rwkv" "$TMP/vllm.git" 2>/dev/null; then
    if git -C "$TMP/vllm.git" cat-file -e 67f0c599 2>/dev/null; then
      special="${special}**是**\n"
    else
      special="${special}**否**（快照/迁移?）\n"
    fi
  else
    special="${special}clone 失败\n"
  fi
fi

# --- 输出 MD ---
{
  echo "# RWKV 生态跟踪快照 ${TS}"
  echo
  echo "- 采集时间: ${TS} (UTC) / ${now_date}"
  echo "- 仓库数: ${total}；采集失败/不存在: ${missing}"
  echo "- 数据源: \`git ls-remote\` + \`commits/*.atom\` + GitHub HTML（**零 API 配额**）"
  echo
  echo "| 仓库 | 分支 | HEAD | 最后提交 (UTC) | LICENSE | 分支数 | Stars | 描述 |"
  echo "|---|---|---|---|---|---|---|---|"
  printf '%s\n' "${REPORT[@]}" | awk -F'|' '{printf "| %s | %s | %s | %s | %.45s | %s | %s | %.70s |\n", $1,$2,$3,$4,$5,$6,$7,$8}'
  echo
  echo "## 特殊检查"
  echo
  printf '%b' "$special"
} > "$MD"

# --- 输出 TSV(供 diff) ---
{
  printf 'repo\tbranch\thead\tlast_commit\tlicense\tbranches\tstars\tdesc\n'
  printf '%s\n' "${REPORT[@]}" | awk -F'|' '{printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", $1,$2,$3,$4,$5,$6,$7,$8}'
} > "$TSV"

cat "$MD"

# --- diff ---
if [ "$DIFF" = "1" ]; then
  prev="$(ls -1 "$RUNDIR"/*.tsv 2>/dev/null | grep -v "$TS.tsv" | tail -1)"
  echo
  echo "## Δ vs 上一轮 (${prev:-无})"
  echo
  if [ -n "$prev" ]; then
    python3 - "$prev" "$TSV" <<'PY'
import sys
def load(p):
    rows={}
    for i,l in enumerate(open(p, encoding='utf-8')):
        if i==0: continue
        f=l.rstrip('\n').split('\t')
        if len(f)>=5: rows[f[0]]=f
    return rows
a,b=load(sys.argv[1]),load(sys.argv[2])
changed=0
for r in sorted(set(a)|set(b)):
    if r not in a: print(f"+ 新增 {r}"); changed+=1; continue
    if r not in b: print(f"- 移除 {r}"); changed+=1; continue
    fa,fb=a[r],b[r]
    diffs=[n for n,i in (("HEAD",2),("最后提交",3),("LICENSE",4)) if fa[i]!=fb[i]]
    if diffs: print(f"~ {r}: " + "; ".join(f"{n}: {fa[i] if n!='HEAD' else fa[2]} -> {fb[i] if n!='HEAD' else fb[2]}" for n,i in (("HEAD",2),("最后提交",3),("LICENSE",4)) if fa[i]!=fb[i])); changed+=1
print(f"变化条目: {changed}")
PY
  fi
fi

echo
echo "快照: $MD"
