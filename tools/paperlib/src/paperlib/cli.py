# Copyright (c) 2026 Harmattan AI.
"""The paper command: add, name, fix, hook, migrate."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from paperlib import library, migrate, pdftext
from paperlib.naming import NamingError, doc_name

LIBRARY_NAME = "thesis"
BIB = "references.bib"


def _info_files(root: Path) -> set[Path]:
    return set(root.rglob(library.INFO)) if root.is_dir() else set()


def cmd_add(args: argparse.Namespace) -> int:
    """Add a PDF to the library with metadata, compliant name and fulltext.txt.

    Args:
        args: parsed arguments.

    Returns:
        Exit code.
    """
    lib = library.library_dir()
    sub = lib / args.subfolder
    before = _info_files(sub)
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / Path(args.pdf).name
        shutil.copy2(args.pdf, pdf)
        if pdftext.is_scan(pdf):
            print("no text layer, running OCR")
            pdftext.ocr(pdf)
        cmd = [
            "papis",
            "-l",
            LIBRARY_NAME,
            "add",
            "--batch",
            "--subfolder",
            args.subfolder,
        ]
        if args.doi:
            cmd += ["--from", "doi", args.doi]
        elif args.arxiv:
            cmd += ["--from", "arxiv", args.arxiv]
        else:
            if not (args.title and args.author and args.year):
                print(
                    "give --doi, --arxiv or all of --title, --author, --year",
                    file=sys.stderr,
                )
                return 2
            cmd += [
                "--set",
                "title",
                args.title,
                "--set",
                "author",
                " and ".join(args.author),
            ]
            cmd += ["--set", "year", args.year]
        subprocess.run([*cmd, str(pdf)], check=True, stdin=subprocess.DEVNULL)
    new = sorted(_info_files(sub) - before)
    if len(new) != 1:
        print(
            f"expected one new document under {sub}, found {len(new)}", file=sys.stderr
        )
        return 1
    folder = new[0].parent
    if args.edit:
        subprocess.run(
            [os.environ.get("EDITOR", "vi"), str(folder / library.INFO)], check=True
        )
    try:
        folder = library.fix(folder)
    except (NamingError, ValueError, FileExistsError) as exc:
        print(
            f"{exc}\nedit {folder / library.INFO} (or acronyms.txt), then run: paper fix {folder}",
            file=sys.stderr,
        )
        return 1
    pdftext.write_fulltext(folder / f"{folder.name}.pdf")
    library.git("add", str(folder), cwd=lib)
    print(folder.relative_to(lib))
    return 0


def cmd_name(args: argparse.Namespace) -> int:
    """Print the expected name of each document folder.

    Args:
        args: parsed arguments.

    Returns:
        Exit code.
    """
    code = 0
    for path in args.paths:
        folder = library.doc_folder(Path(path))
        try:
            print(
                doc_name(library.load(folder))
                if folder
                else f"{path}: not a document folder"
            )
        except NamingError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            code = 1
    return code


def cmd_fix(args: argparse.Namespace) -> int:
    """Rename document folders and PDFs to their expected names.

    Args:
        args: parsed arguments.

    Returns:
        Exit code.
    """
    code = 0
    for path in args.paths:
        folder = library.doc_folder(Path(path))
        if folder is None:
            print(f"{path}: not a document folder", file=sys.stderr)
            code = 1
            continue
        try:
            print(library.fix(folder))
        except (NamingError, ValueError, FileExistsError) as exc:
            print(exc, file=sys.stderr)
            code = 1
    return code


def export_bib(root: Path) -> None:
    """Regenerate references.bib from all documents.

    Args:
        root: library root.

    Raises:
        RuntimeError: papis export failed.
    """
    tmp = root / f".{BIB}.tmp"
    tmp.unlink(missing_ok=True)
    subprocess.run(
        ["papis", "-l", LIBRARY_NAME, "cache", "clear"],
        check=True,
        capture_output=True,
        stdin=subprocess.DEVNULL,
    )
    res = subprocess.run(
        [
            "papis",
            "-l",
            LIBRARY_NAME,
            "export",
            "--all",
            "--format",
            "bibtex",
            "--out",
            str(tmp),
        ],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    )
    if res.returncode != 0 or not tmp.exists():
        raise RuntimeError(f"papis export failed:\n{res.stdout}{res.stderr}")
    tmp.replace(root / BIB)


def cmd_hook(args: argparse.Namespace) -> int:
    """Pre-commit hook: check names, create missing fulltext.txt, refresh references.bib.

    Args:
        args: parsed arguments (staged paths).

    Returns:
        Exit code.
    """
    root = Path.cwd()
    folders = {f for f in (library.doc_folder(root / p) for p in args.paths) if f}
    errors: list[str] = []
    for folder in sorted(folders):
        found = library.problems(folder)
        if found:
            errors += found
            continue
        if not (folder / pdftext.FULLTEXT).is_file():
            pdftext.write_fulltext(folder / f"{folder.name}.pdf")
            library.git("add", str(folder), cwd=root)
    if any(Path(p).name == library.INFO for p in args.paths):
        export_bib(root)
        library.git("add", BIB, cwd=root)
    for err in errors:
        print(err, file=sys.stderr)
    if errors:
        print("run: paper fix <folder>", file=sys.stderr)
    return 1 if errors else 0


def main() -> int:
    """Entry point of the paper command.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(prog="paper", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add", help="add a PDF")
    add.add_argument("pdf")
    add.add_argument("-d", "--subfolder", required=True, help="topic folder, e.g. BEMT")
    add.add_argument("--doi")
    add.add_argument("--arxiv")
    add.add_argument("--title")
    add.add_argument(
        "--author", action="append", help="family name, repeat in paper order"
    )
    add.add_argument("--year")
    add.add_argument("--edit", action="store_true", help="edit info.yaml before naming")
    add.set_defaults(func=cmd_add)
    for name, func, text in (
        ("name", cmd_name, "print expected names"),
        ("fix", cmd_fix, "rename to expected"),
    ):
        p = sub.add_parser(name, help=text)
        p.add_argument("paths", nargs="+")
        p.set_defaults(func=func)
    hook = sub.add_parser("hook", help="pre-commit hook")
    hook.add_argument("paths", nargs="*")
    hook.set_defaults(func=cmd_hook)
    mig = sub.add_parser("migrate", help="convert loose PDFs into document folders")
    mig.add_argument("--execute", action="store_true", help="apply instead of dry run")
    mig.add_argument(
        "--overrides", type=Path, help="YAML with metadata per existing stem"
    )
    mig.add_argument("--report", type=Path, default=Path("migration_report.tsv"))
    mig.set_defaults(func=migrate.run)
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
