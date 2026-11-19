# Copyright (c) 2026 Harmattan AI.
"""One-off migration of the renamed loose PDFs into papis document folders."""

import argparse
import difflib
import re
from pathlib import Path

import yaml

from paperlib import library, pdftext
from paperlib.naming import (
    NamingError,
    doc_families,
    doc_name,
    format_name,
    title_snake,
)

SKIP_DIRS = {"confluence_pages", "mit_mark_drela_course", "mit_course", "tools", ".git"}
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)", re.IGNORECASE)
REVIEW = "needs-review"
COLUMNS = ["status", "stem", "dir", "source", "doi", "crossref_year", "note"]


def loose_pdfs(root: Path) -> list[Path]:
    """List in scope PDFs that are not yet in a document folder.

    Args:
        root: library root.

    Returns:
        Sorted PDF paths.
    """
    found = []
    for pdf in root.rglob("*.pdf"):
        parts = set(pdf.relative_to(root).parts[:-1])
        if parts & SKIP_DIRS or any(p.endswith("_files") for p in parts):
            continue
        if not (pdf.parent / library.INFO).exists():
            found.append(pdf)
    return sorted(found)


def _similar(title: str, stem: str) -> bool:
    try:
        snake = title_snake(title).lower()
    except NamingError:
        snake = re.sub(r"\W+", "_", title.lower())
    return (
        difflib.SequenceMatcher(None, snake, stem.lower()[: len(snake)]).ratio() > 0.8
    )


def crossref(pdf: Path, stem: str) -> tuple[dict | None, str]:
    """Find the paper's own DOI on pages 1 to 2 and fetch Crossref data.

    Args:
        pdf: PDF path.
        stem: agreed name stem.

    Returns:
        Papis data or None, and the DOI tried.
    """
    import papis.crossref

    tried = ""
    for doi in dict.fromkeys(DOI_RE.findall(pdftext.extract(pdf, 1, 2))):
        doi = doi.rstrip(".,;)]}⟩>")
        tried = doi
        try:
            hits = papis.crossref.get_data(dois=[doi])
        except Exception:  # noqa: BLE001, network or unknown DOI
            continue
        if hits and _similar(str(hits[0].get("title", "")), stem):
            return hits[0], doi
    return search(stem) or (None, tried)


def search(stem: str) -> tuple[dict, str] | None:
    """Search Crossref by the name's words; accept only a matching title and first author.

    Args:
        stem: agreed name stem.

    Returns:
        Papis data and DOI, or None.
    """
    import papis.crossref

    words = stem[:-5].replace("_", " ").replace("et al", "")
    try:
        hits = papis.crossref.get_data(query=words, max_results=5)
    except Exception:  # noqa: BLE001, network
        return None
    for hit in hits:
        families = doc_families(hit)
        first = surname_key(families[0]) if families else ""
        same_year = str(hit.get("year", "")) == stem[-4:]
        if (
            first
            and first in stem.lower()
            and same_year
            and _similar(str(hit.get("title", "")), stem)
        ):
            hit["_searched"] = True
            return hit, str(hit.get("doi", ""))
    return None


def _match_case(data: dict, stem: str) -> None:
    """Take surname casing from the stem when Crossref differs only in case (STEFKO)."""
    for author in data.get("author_list") or []:
        key = surname_key(author.get("family") or "")
        idx = stem.lower().find(f"_{key}_") if key else -1
        if idx >= 0:
            author["family"] = stem[idx + 1 : idx + 1 + len(key)].replace("_", " ")


def _page_title(pdf: Path, title_part: str) -> str | None:
    """Recover the original casing of a filename title from page 1 text.

    Returns:
        Title as printed, or None.
    """
    words = [re.escape(w).replace(r"\-", r"[-‐‑\s]*") for w in title_part.split("_")]
    match = re.search(r"[\W_]+".join(words), pdftext.extract(pdf, 1, 2), re.IGNORECASE)
    if not match:
        return None
    text = " ".join(match.group(0).split())
    try:
        return text if title_snake(text) == title_part else None
    except NamingError:
        return None


def surname_key(family: str) -> str:
    """Lowercase file name form of a family name.

    Args:
        family: family name.

    Returns:
        Comparable key.
    """
    from paperlib.naming import surname

    return surname(family).lower()


def _fit_title(data: dict, stem: str, pdf: Path) -> bool:
    """Replace the title by the filename title when only the title differs.

    Returns:
        True when the authors and year match the stem.
    """
    year = stem[-4:]
    try:
        suffix = format_name("x", doc_families(data), year)[2:]
    except NamingError:
        return False
    if not stem.endswith("_" + suffix):
        return False
    title_part = stem[: -len(suffix) - 1]
    data["title"] = _page_title(pdf, title_part) or title_part.replace("_", " ")
    return True


def plan_one(pdf: Path, root: Path, overrides: dict) -> tuple[dict | None, dict]:
    """Build info.yaml data for one PDF.

    Args:
        pdf: PDF path.
        root: library root.
        overrides: metadata per stem.

    Returns:
        Data (None on failure) and the report row.
    """
    stem = pdf.stem
    row = dict.fromkeys(COLUMNS, "")
    row.update(stem=stem, dir=str(pdf.parent.relative_to(root)))
    override = overrides.get(stem)
    data, doi = (
        (None, "") if override and not override.get("doi") else crossref(pdf, stem)
    )
    if override and override.get("doi") and data is None:
        import papis.crossref

        hits = papis.crossref.get_data(dois=[override["doi"]])
        data, doi = (hits[0] if hits else None), override["doi"]
    row["doi"] = doi
    searched = False
    if data is not None:
        searched = bool(data.pop("_searched", False))
        row["source"] = "crossref-search" if searched else "crossref"
        row["crossref_year"] = str(data.get("year", ""))
        _match_case(data, stem)
    if override:
        data = {**(data or {}), **override}
        row["source"] = "crossref+override" if row["source"] else "override"
    if data is None:
        row.update(status="FAIL", note="no DOI match and no override")
        return None, row
    data["year"] = int(stem[-4:])
    tags = set(data.get("tags") or [])
    if searched or not row["source"].startswith("crossref"):
        tags.add(REVIEW)
    try:
        ok = doc_name(data) == stem
    except NamingError as exc:
        ok, row["note"] = False, str(exc)
    if not ok and _fit_title(data, stem, pdf):
        tags.add(REVIEW)
        row["note"] = "title taken from filename"
        ok = doc_name(data) == stem
    if not ok:
        row["status"] = "FAIL"
        row["note"] = (
            row["note"]
            or f"metadata gives {doc_name(data) if data.get('title') else '?'}"
        )
        return None, row
    if row["crossref_year"] and row["crossref_year"] != stem[-4:]:
        row["note"] = (
            row["note"] + "; " if row["note"] else ""
        ) + "year kept from filename"
    if tags:
        data["tags"] = sorted(tags)
    data["files"] = [f"{stem}.pdf"]
    row["status"] = "OK"
    return data, row


def run(args: argparse.Namespace) -> int:
    """Dry run or execute the migration.

    Args:
        args: parsed arguments (execute, overrides, report).

    Returns:
        Exit code.

    Raises:
        FileExistsError: a target PDF already exists.
    """
    root = library.library_dir()
    overrides = (
        yaml.safe_load(args.overrides.read_text(encoding="utf-8"))
        if args.overrides
        else {}
    )
    plans = [(pdf, *plan_one(pdf, root, overrides or {})) for pdf in loose_pdfs(root)]
    with args.report.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for _, _, row in plans:
            fh.write("\t".join(str(row[c]) for c in COLUMNS) + "\n")
    failed = [row["stem"] for _, data, row in plans if data is None]
    print(f"{len(plans)} PDFs, {len(failed)} failed, report: {args.report}")
    if failed or not args.execute:
        return 1 if failed else 0
    for pdf, data, _ in plans:
        folder = pdf.parent / pdf.stem
        folder.mkdir()
        target = folder / pdf.name
        if target.exists():
            raise FileExistsError(target)
        pdf.rename(target)
        library.save(folder, data or {})
        pdftext.write_fulltext(target)
        print(folder.relative_to(root))
    return 0
