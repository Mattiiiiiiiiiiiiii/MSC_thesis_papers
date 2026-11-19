# Copyright (c) 2026 Harmattan AI.
"""Document folder helpers: load, check and fix names."""

import subprocess
from pathlib import Path

import yaml

from paperlib.naming import doc_name

INFO = "info.yaml"


def library_dir() -> Path:
    """Return the papis library directory.

    Returns:
        Library root from the papis configuration.
    """
    import papis.config

    return Path(papis.config.get_lib_dirs()[0]).expanduser().resolve()


def load(folder: Path) -> dict:
    """Read a document's info.yaml.

    Args:
        folder: document folder.

    Returns:
        Document data.
    """
    return yaml.safe_load((folder / INFO).read_text(encoding="utf-8")) or {}


def save(folder: Path, data: dict) -> None:
    """Write a document's info.yaml.

    Args:
        folder: document folder.
        data: document data.
    """
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)
    (folder / INFO).write_text(text, encoding="utf-8")


def doc_folder(path: Path) -> Path | None:
    """Find the document folder holding *path*.

    Args:
        path: file or folder inside the library.

    Returns:
        Folder with info.yaml, or None.
    """
    folder = path if path.is_dir() else path.parent
    return folder if (folder / INFO).is_file() else None


def problems(folder: Path) -> list[str]:
    """List naming problems of a document folder.

    Args:
        folder: document folder.

    Returns:
        Problem descriptions, empty when compliant.
    """
    try:
        stem = doc_name(load(folder))
    except ValueError as exc:
        return [f"{folder}: {exc}"]
    found = []
    if folder.name != stem:
        found.append(f"{folder}: folder should be {stem}")
    files = load(folder).get("files") or []
    if files != [f"{stem}.pdf"]:
        found.append(f"{folder}: files {files} should be ['{stem}.pdf']")
    elif not (folder / files[0]).is_file():
        found.append(f"{folder}: missing {files[0]}")
    return found


def fix(folder: Path) -> Path:
    """Rename a document folder and its single PDF to the expected name.

    Args:
        folder: document folder.

    Returns:
        New folder path.

    Raises:
        FileExistsError: a target already exists.
        ValueError: the document does not hold exactly one PDF.
    """
    data = load(folder)
    stem = doc_name(data)
    files = data.get("files") or []
    on_disk = sorted(p.name for p in folder.glob("*.pdf"))
    if len(files) == 1 and not (folder / files[0]).exists() and len(on_disk) == 1:
        files = on_disk
        data["files"] = files
    if len(files) != 1 or not files[0].lower().endswith(".pdf"):
        raise ValueError(f"{folder}: expected one PDF in files, got {files}")
    target_pdf = folder / f"{stem}.pdf"
    if files[0] != target_pdf.name:
        if target_pdf.exists():
            raise FileExistsError(target_pdf)
        (folder / files[0]).rename(target_pdf)
        data["files"] = [target_pdf.name]
        save(folder, data)
    target = folder.parent / stem
    if folder != target:
        if target.exists():
            raise FileExistsError(target)
        folder.rename(target)
    return target


def git(*args: str, cwd: Path) -> str:
    """Run git in *cwd*.

    Args:
        *args: git arguments.
        cwd: working directory.

    Returns:
        Standard output.
    """
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout
