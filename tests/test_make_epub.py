import subprocess
import sys

from conftest import REPO_ROOT
from ebooklib import epub


def test_builds_epub_with_chapters(tmp_path):
    md = tmp_path / "issue.md"
    md.write_text(
        "# Semi-Supervised\n"
        "<!-- mood: Holding -->\n\n"
        "A short intro line.\n\n"
        "## First Piece\n\n*by Iris — on how children grow*\n\nHello world.\n\n"
        "## Second Piece\n\n*by Cleo — on time & family*\n\nAnother piece.\n"
    )
    out = tmp_path / "semi-supervised-2026-06-16.epub"

    result = subprocess.run(
        [sys.executable, f"{REPO_ROOT}/scripts/make_epub.py",
         "--md", str(md), "--out", str(out),
         "--cover-src", str(tmp_path / "no_cover.png")],  # nonexistent -> skipped
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out.exists()

    book = epub.read_epub(str(out))
    titles = [it.get_name() for it in book.get_items()
              if it.get_name().startswith("chap_")]
    # intro becomes chap_00, the two pieces chap_01/chap_02.
    assert len(titles) == 3


def test_empty_markdown_fails(tmp_path):
    md = tmp_path / "empty.md"
    md.write_text("# Semi-Supervised\n")
    out = tmp_path / "x-2026-06-16.epub"
    result = subprocess.run(
        [sys.executable, f"{REPO_ROOT}/scripts/make_epub.py",
         "--md", str(md), "--out", str(out)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
