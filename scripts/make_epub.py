#!/usr/bin/env python3
"""Build a Kindle-ready EPUB from an issue's markdown.

The daily-issue skill writes one markdown file: an H1 title, an optional intro,
then `## `-headed pieces. Each `## ` section becomes an EPUB chapter so the Kindle
table of contents mirrors the issue's pieces.

The cover is a finished image (assets/cover.png) embedded directly — the title and
subtitle are part of the artwork, so we don't composite any text. Per-issue identity
(date, mood) lives in the EPUB metadata title instead, which is what shows in the
Kindle library list, so issues stay distinguishable even though they share cover art.

Usage:
    python scripts/make_epub.py --md out/issue.md \
        --out "docs/issues/semi-supervised-$(date +%F).epub" \
        --cover-src assets/cover.png
"""
from __future__ import annotations

import argparse
import os
import re
import sys

import markdown as md
from ebooklib import epub

STYLE = """
body { font-family: serif; line-height: 1.5; }
h1 { font-size: 1.4em; }
h2 { font-size: 1.2em; }
blockquote { font-style: italic; margin-left: 1em; }
em { color: #333; }
"""

BOOK_TITLE = "Semi-Supervised"


def split_chapters(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (book_title, [(chapter_title, chapter_markdown), ...])."""
    # Drop the mood-word marker (`<!-- mood: X -->`); it's metadata, not body text.
    text = re.sub(r"<!--\s*mood:.*?-->\s*", "", text)
    lines = text.splitlines()
    title = BOOK_TITLE
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines = lines[1:]

    chapters: list[tuple[str, str]] = []
    current_title, current_lines = "Today", []
    for line in lines:
        if line.startswith("## "):
            if "".join(current_lines).strip():
                chapters.append((current_title, "\n".join(current_lines)))
            current_title, current_lines = line[3:].strip(), []
        else:
            current_lines.append(line)
    if "".join(current_lines).strip():
        chapters.append((current_title, "\n".join(current_lines)))
    return title, chapters


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default="out/issue.md")
    ap.add_argument("--out", required=True,
                    help="e.g. docs/issues/semi-supervised-2026-06-16.epub")
    ap.add_argument("--author", default=os.environ.get("AUTHOR_NAME", BOOK_TITLE))
    ap.add_argument("--cover-src", default="assets/cover.png",
                    help="finished cover image to embed (used as-is, no text overlay)")
    ap.add_argument("--mood", default="", help="optional mood word, recorded in the title")
    args = ap.parse_args()

    with open(args.md) as f:
        text = f.read()
    _title, chapters = split_chapters(text)
    if not chapters:
        print(f"{args.md} has no content — not building an EPUB.", file=sys.stderr)
        return 1

    # Kindle library title: a stable prefix + the issue date (and mood, if any) so
    # every issue clusters, sorts, and stays identifiable in the Docs view even
    # though the cover art is shared. Date comes from the --out filename.
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(args.out))
    issue_date = m.group(1) if m else ""
    title = args.author
    if issue_date:
        title = f"{args.author} — {issue_date}"
        if args.mood:
            title += f" · {args.mood}"

    book = epub.EpubBook()
    book.set_identifier(re.sub(r"\W+", "-", os.path.basename(args.out)))
    book.set_title(title)
    book.set_language("en")
    book.add_author(args.author)
    # Series metadata groups issues together if ever routed through Calibre.
    book.add_metadata("OPF", "belongs-to-collection", args.author, {"id": "series"})
    if issue_date:
        book.add_metadata(None, "meta", issue_date,
                          {"name": "calibre:series", "content": args.author})

    css = epub.EpubItem(uid="style", file_name="style.css",
                        media_type="text/css", content=STYLE.encode())
    book.add_item(css)

    if args.cover_src and os.path.exists(args.cover_src):
        with open(args.cover_src, "rb") as cf:
            book.set_cover("cover.png", cf.read())

    items = []
    for i, (ch_title, ch_md) in enumerate(chapters):
        html = md.markdown(ch_md, output_format="html5")
        ch = epub.EpubHtml(title=ch_title, file_name=f"chap_{i:02d}.xhtml", lang="en")
        ch.content = f"<h2>{ch_title}</h2>\n{html}"
        ch.add_item(css)
        book.add_item(ch)
        items.append(ch)

    book.toc = items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + items

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    epub.write_epub(args.out, book)
    print(f"Wrote {args.out}: \"{title}\", {len(items)} pieces, "
          f"{len(text.split())} words.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
