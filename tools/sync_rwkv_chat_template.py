"""Sync the rwkv chat template from the upstream rwkv-rs/transformers-rwkv fork.

Why: PR #20 (2026-11-10, merge 6d0d57af) fixed two problems with tool-call history
rendering in `temp/rwkv_chat_template.jinja`:

  1. crash when a conversation has tool-call history + a system message but no
     `tools` (`tools | default([])` does not replace a None value), and
  2. past tool calls were rendered as indented JSON with escaped string
     `arguments`; the instructed format is one-line
     `{"name": ..., "arguments": {...}}`.

Model exports produced before the fix keep the old template. This script fetches
the pinned post-fix template, verifies its sha256, optionally backs up the old
template, and writes it into a model directory. It never touches weights.

Usage:
    python tools/sync_rwkv_chat_template.py --model-dir /path/to/hf/export
    python tools/sync_rwkv_chat_template.py --model-dir ... --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import urllib.request
from pathlib import Path

# rwkv-rs/transformers-rwkv main after PR #20 and #21 merged (2026-11-10).
UPSTREAM_COMMIT = "46bb5d260316c23c17df0f804386cf9097264390"
TEMPLATE_PATH = "temp/rwkv_chat_template.jinja"
EXPECTED_SHA256 = "6929421a9212aff1046602142253e86bdcbb5b0f9d0045bf3f62ef4fd70d1e7d"


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as resp:  # noqa: S310
        return resp.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True, type=Path)
    ap.add_argument("--source", default=None, help="local file or URL (default: pinned upstream)")
    ap.add_argument("--expected-sha256", default=EXPECTED_SHA256)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    target = args.model_dir / "chat_template.jinja"
    if not args.model_dir.is_dir():
        sys.exit(f"model dir not found: {args.model_dir}")

    src = args.source or (
        f"https://raw.githubusercontent.com/rwkv-rs/transformers-rwkv/{UPSTREAM_COMMIT}/{TEMPLATE_PATH}"
    )
    data = Path(src).read_bytes() if Path(src).is_file() else fetch(src)
    digest = hashlib.sha256(data).hexdigest()
    print(f"source: {src}")
    print(f"sha256: {digest}")

    if args.expected_sha256 != "PLACEHOLDER" and digest != args.expected_sha256:
        sys.exit(f"sha256 mismatch: expected {args.expected_sha256}")

    text = data.decode("utf-8")
    if "tools or []" not in text:
        sys.exit("downloaded template lacks the PR #20 `tools or []` fix")
    if 'payload = \'{"name": ' not in text and '{"name": ' not in text:
        sys.exit("downloaded template lacks the PR #20 one-line tool-call format")

    if args.dry_run:
        print(f"[dry-run] would write {len(data)} bytes to {target}")
        return 0

    if target.exists():
        backup = target.with_suffix(".pre-pr20.jinja")
        shutil.copy2(target, backup)
        print(f"backed up old template -> {backup}")
    target.write_bytes(data)
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
