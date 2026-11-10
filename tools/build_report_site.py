"""Build a static HTML site for the Markdown reports in this repository.

Usage:
    python tools/build_report_site.py [--out site]

Requires the `markdown` package (pip install markdown) and optionally Pygments.
The generated `site/` directory is committed so the reports can be read in a
browser without a build step.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/Fantasia-Infinity/RWKV-AgenticLearning"
SITE_TITLE = "RWKV-AgenticLearning · 报告站"

HERE = Path(__file__).resolve().parent

def load_markdown():
    for extra in (str(HERE / ".." / ".mdlib"), "/tmp/mdlib"):
        if Path(extra).is_dir() and extra not in sys.path:
            sys.path.insert(0, extra)
    try:
        import markdown  # noqa: F401
        return markdown
    except ImportError:
        sys.exit("markdown package missing: pip install markdown (or set PYTHONPATH to a dir containing it)")

INCLUDE_GLOBS = [
    "README.md",
    "ROADMAP.md",
    "THIRD_PARTY_NOTICES.md",
    "docs/**/*.md",
    "reports/**/*.md",
]
EXCLUDE_PREFIXES = ("repos/", "private/", "site/", ".git/")


def discover() -> list[Path]:
    files: list[Path] = []
    for pattern in INCLUDE_GLOBS:
        files.extend(p for p in REPO.glob(pattern) if p.is_file())
    unique = {}
    for p in files:
        rel = p.relative_to(REPO).as_posix()
        if rel.startswith(EXCLUDE_PREFIXES):
            continue
        unique[rel] = p
    return [unique[k] for k in sorted(unique)]


def title_of(text: str, rel: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        t = re.sub(r"[`*_]", "", m.group(1)).strip()
        if t:
            return t
    return Path(rel).stem


def excerpt_of(text: str) -> str:
    body = re.sub(r"^#\s+.+$", "", text, count=1, flags=re.M)
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"^\s*[-*|>].*$", "", body, flags=re.M)
    for line in body.splitlines():
        line = line.strip()
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"[`*_#]", "", line)
        if len(line) > 40:
            return line[:220]
    return ""


def category(rel: str) -> str:
    if rel in ("README.md", "ROADMAP.md", "THIRD_PARTY_NOTICES.md"):
        return "项目"
    if rel.startswith("docs/"):
        return "文档"
    if rel.startswith("reports/") and any(rel.startswith(f"reports/{x}") for x in ("skyrl/", "state/", "eco/")) or rel == "reports/EVIDENCE.md":
        return "专题报告"
    return "核心报告"


def date_of(rel: str) -> str:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", rel)
    return m.group(1) if m else ""


def rel_html(rel: str) -> str:
    if rel == "README.md":
        return "index.html"
    if rel.endswith(".md"):
        return rel[:-3] + ".html"
    return rel


def build(out: Path, files: list[Path]) -> None:
    markdown = load_markdown()
    import pygments
    from pygments.formatters import HtmlFormatter

    out.mkdir(parents=True, exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)

    md = markdown.Markdown(
        extensions=["extra", "tables", "fenced_code", "codehilite", "toc", "sane_lists", "attr_list"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
            "toc": {"anchorlink": True, "toc_depth": "2-3"},
        },
        output_format="html5",
    )

    entries = []
    rendered: dict[str, str] = {}
    for p in files:
        rel = p.relative_to(REPO).as_posix()
        text = p.read_text(encoding="utf-8")
        md.reset()
        body = md.convert(text)
        body = re.sub(r'href="([^"#]+)\.md(#[^"]*)?"', lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', body)
        outline = md.toc
        rendered[rel] = body
        entries.append({
            "rel": rel, "html": rel_html(rel), "title": title_of(text, rel),
            "excerpt": excerpt_of(text), "category": category(rel), "date": date_of(rel),
            "outline": outline, "chars": len(text),
        })

    style = (HERE / "report_site.css").read_text(encoding="utf-8") if (HERE / "report_site.css").is_file() else ""
    pyg = HtmlFormatter(style="default").get_style_defs(".codehilite")
    (out / "assets" / "style.css").write_text(style + "\n" + pyg + "\n", encoding="utf-8")

    entries_by_cat: dict[str, list[dict]] = {}
    for e in entries:
        entries_by_cat.setdefault(e["category"], []).append(e)
    order = ["核心报告", "专题报告", "文档", "项目"]
    entries_by_cat = {k: sorted(v, key=lambda x: (x["date"], x["rel"]), reverse=True) for k, v in entries_by_cat.items()}
    entries_by_cat = {k: entries_by_cat[k] for k in order if k in entries_by_cat}

    def nav(active: str, prefix: str) -> str:
        parts = [f'<a href="{prefix}index.html">首页</a>']
        for cat, items in entries_by_cat.items():
            parts.append(f'<span class="nav-cat">{html.escape(cat)}</span>')
            for e in items:
                cls = ' class="active"' if e["rel"] == active else ""
                parts.append(f'<a href="{prefix}{e["html"]}"{cls}>{html.escape(e["title"])}</a>')
        parts.append(f'<a class="ext" href="{REPO_URL}" target="_blank" rel="noopener">GitHub ↗</a>')
        return "\n".join(parts)

    def page(title: str, active: str, prefix: str, main: str, extra_head: str = "") -> str:
        built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {html.escape(SITE_TITLE)}</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
{extra_head}
</head>
<body>
<header class="topbar"><div class="wrap"><a class="brand" href="{prefix}index.html">{html.escape(SITE_TITLE)}</a>
<span class="built">built {built}</span></div></header>
<div class="layout wrap">
<nav class="sidebar">{nav(active, prefix)}</nav>
<main class="content">
{main}
<footer class="foot">Generated from the repository Markdown sources · <a href="{REPO_URL}" target="_blank" rel="noopener">source on GitHub</a></footer>
</main>
</div>
</body>
</html>
"""

    for e in entries:
        depth = e["rel"].count("/")
        prefix = "../" * depth
        src_url = f"{REPO_URL}/blob/main/{e['rel']}"
        main = f"""<article class="report">
<div class="crumb"><a href="{prefix}index.html">首页</a> / {html.escape(e['rel'])}</div>
<h1 class="report-title">{html.escape(e['title'])}</h1>
<div class="meta"><span class="badge">{html.escape(e['category'])}</span>"""
        if e["date"]:
            main += f'<span class="badge date">{e["date"]}</span>'
        main += f'<a class="src" href="{src_url}" target="_blank" rel="noopener">Markdown 源文件 ↗</a></div>'
        main += f'<details class="toc-box" open><summary>目录</summary>{e["outline"]}</details>'
        main += f'<div class="md-body">{rendered[e["rel"]]}</div></article>'
        target = out / e["html"]
        target.parent.mkdir(parents=True, exist_ok=True)
        rel_prefix = "../" * e["html"].count("/")
        target.write_text(page(e["title"], e["rel"], rel_prefix, main), encoding="utf-8")

    # index
    cards = []
    for cat, items in entries_by_cat.items():
        cards.append(f'<section class="cat"><h2>{html.escape(cat)}</h2><div class="cards">')
        for e in items:
            d = f'<span class="badge date">{e["date"]}</span>' if e["date"] else ""
            cards.append(
                f'<a class="card" href="{e["html"]}"><div class="card-head"><h3>{html.escape(e["title"])}</h3>{d}</div>'
                f'<p>{html.escape(e["excerpt"])}</p><code>{html.escape(e["rel"])}</code></a>'
            )
        cards.append("</div></section>")
    idx_main = f"""<article class="report">
<h1 class="report-title">{html.escape(SITE_TITLE)}</h1>
<p class="lead">本仓库全部公开报告与文档的 HTML 版本（由 <code>tools/build_report_site.py</code> 从 Markdown 生成）。
覆盖：RWKV 生态核验、skyrl/state/eco 专题、证据方法学，以及 2026-11-08~10 的 SFT/RL 实验汇总
（DAPO 在 G1l-1.5B 上 avg@4 21.0→31.0，p=6.6e-05）。</p>
{"".join(cards)}
</article>"""
    (out / "index.html").write_text(page("首页", "__index__", "", idx_main), encoding="utf-8")

    # copy non-markdown assets referenced by reports (data JSON etc.)
    import shutil
    data_dir = REPO / "reports" / "data"
    if data_dir.is_dir():
        for src in data_dir.rglob("*"):
            if src.is_file():
                dst = out / "reports" / "data" / src.relative_to(data_dir)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    # machine-readable site index
    (out / "index.json").write_text(json.dumps({
        "site": SITE_TITLE, "repo": REPO_URL,
        "built": datetime.now(timezone.utc).isoformat(),
        "reports": [{k: e[k] for k in ("rel", "html", "title", "category", "date", "chars")} for e in entries],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site")
    args = ap.parse_args()
    out = (REPO / args.out).resolve()
    files = discover()
    build(out, files)
    print(f"built {len(files)} reports -> {out}")


if __name__ == "__main__":
    main()
