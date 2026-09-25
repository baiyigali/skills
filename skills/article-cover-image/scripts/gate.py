#!/usr/bin/env python3
"""Hard gate for article-cover-image.

Refuse to generate a cover until the article is genuinely finished on disk.
This is the deterministic guard that replaces "please remember to do this
after writing" — a model can ignore prose, it cannot ignore exit code 1.

Usage:  python3 gate.py <article.md> [--min-chars N]
Exit:   0 = article complete, cover allowed
        1 = article incomplete, STOP
        2 = bad usage
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_MIN_CHARS = 800


def count_chars(text: str) -> int:
    """Count CJK characters plus Latin words."""
    return len(re.findall(r"[\u4e00-\u9fff]", text)) + len(re.findall(r"[A-Za-z]+", text))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify an article is finished before generating its cover image."
    )
    parser.add_argument("article", help="path to the article .md file")
    parser.add_argument(
        "--min-chars",
        type=int,
        default=DEFAULT_MIN_CHARS,
        help=f"minimum body length (default {DEFAULT_MIN_CHARS})",
    )
    args = parser.parse_args()

    md = Path(args.article)

    if not md.is_file():
        print(f"[FAIL] 文章文件不存在：{md}")
        print("       封面必须在文章 .md 落盘之后生成，不允许先出图。")
        return 1

    text = md.read_text(encoding="utf-8")
    lines = text.splitlines()
    problems: list[str] = []

    if not lines or not lines[0].startswith("# "):
        problems.append("首行不是 H1 标题")

    body = "\n".join(lines[1:])
    size = count_chars(body)
    if size < args.min_chars:
        problems.append(
            f"正文仅 {size} 字，低于 {args.min_chars} 字下限 —— 文章未写完"
            f"（短篇可用 --min-chars 调低门槛）"
        )

    if not re.search(r"#[^\s#]", body):
        problems.append("文末缺少话题标签 —— 文章未收尾")

    if "placeholder" in text.lower():
        problems.append("文中存在 placeholder 假链接，先修掉")

    if problems:
        print(f"[FAIL] {md.name} 尚未完成，禁止生成封面：")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"[OK] {md.name} 已完成（{size} 字），可以生成封面")
    return 0


if __name__ == "__main__":
    sys.exit(main())
