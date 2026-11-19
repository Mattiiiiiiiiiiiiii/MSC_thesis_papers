# Copyright (c) 2026 Harmattan AI.
"""Text layer detection, OCR and fulltext.txt extraction."""

import re
import subprocess
from pathlib import Path

MIN_CHARS_PER_PAGE = 200
FULLTEXT = "fulltext.txt"


def page_count(pdf: Path) -> int:
    """Count PDF pages.

    Args:
        pdf: PDF path.

    Returns:
        Number of pages.
    """
    out = subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
    ).stdout
    match = re.search(r"^Pages:\s+(\d+)", out, re.MULTILINE)
    return int(match.group(1)) if match else 0


def extract(pdf: Path, first: int | None = None, last: int | None = None) -> str:
    """Extract text with pdftotext.

    Args:
        pdf: PDF path.
        first: first page, optional.
        last: last page, optional.

    Returns:
        Extracted text.
    """
    cmd = ["pdftotext"]
    if first:
        cmd += ["-f", str(first)]
    if last:
        cmd += ["-l", str(last)]
    res = subprocess.run([*cmd, str(pdf), "-"], capture_output=True, check=True)
    return res.stdout.decode("utf-8", "replace")


def is_scan(pdf: Path) -> bool:
    """Tell whether a PDF lacks a usable text layer.

    Args:
        pdf: PDF path.

    Returns:
        True when the average text per page is under MIN_CHARS_PER_PAGE.
    """
    chars = len("".join(extract(pdf).split()))
    return chars < MIN_CHARS_PER_PAGE * max(page_count(pdf), 1)


def ocr(pdf: Path) -> None:
    """Add a text layer to *pdf* in place with ocrmypdf.

    Args:
        pdf: PDF path.
    """
    tmp = pdf.with_name(pdf.name + ".ocr.tmp")
    subprocess.run(
        ["ocrmypdf", "--skip-text", "--quiet", str(pdf), str(tmp)], check=True
    )
    tmp.replace(pdf)


def write_fulltext(pdf: Path) -> Path:
    """Write fulltext.txt next to *pdf*, running OCR first for scans.

    Args:
        pdf: PDF path inside a document folder.

    Returns:
        Path of fulltext.txt.
    """
    if is_scan(pdf):
        ocr(pdf)
    out = pdf.parent / FULLTEXT
    subprocess.run(["pdftotext", str(pdf), str(out)], check=True)
    return out
