# Copyright (c) 2026 Harmattan AI.
"""File and folder names following naming_rules.out."""

import html
import re
import unicodedata
from collections.abc import Sequence
from functools import cache
from importlib.resources import files

MAX_AUTHORS = 3
MAX_BYTES = 255
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*_(19|20)\d\d")

_DASHES = str.maketrans({"‐": "-", "‑": "-", "‒": "-", "–": "-", "—": " "})
_NON_DECOMPOSING = str.maketrans(
    {
        "ø": "o",
        "Ø": "O",
        "æ": "ae",
        "Æ": "AE",
        "œ": "oe",
        "Œ": "OE",
        "ß": "ss",
        "ł": "l",
        "Ł": "L",
        "đ": "d",
        "Đ": "D",
    }
)
_DELETED = "'\"‘’“”`´"
_SUFFIXES = {"jr", "jr.", "sr", "sr."}


class NamingError(ValueError):
    """Metadata cannot produce a valid name."""


class UnknownAcronymError(NamingError):
    """Title holds all caps tokens missing from acronyms.txt."""

    def __init__(self, tokens: list[str]) -> None:
        """Store the offending tokens.

        Args:
            tokens: all caps tokens not in the whitelist.
        """
        self.tokens = tokens
        super().__init__(
            f"unknown acronyms {tokens}: add them to paperlib/acronyms.txt or lowercase them in the title"
        )


@cache
def acronyms() -> tuple[str, ...]:
    """Load the canonical token whitelist.

    Returns:
        Entries of acronyms.txt.
    """
    text = files("paperlib").joinpath("acronyms.txt").read_text(encoding="utf-8")
    return tuple(
        ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")
    )


def fold(text: str) -> str:
    """Fold diacritics to ASCII.

    Args:
        text: any string.

    Returns:
        ASCII string.
    """
    text = unicodedata.normalize("NFKD", text.translate(_NON_DECOMPOSING))
    return text.encode("ascii", "ignore").decode("ascii")


def _canonical(token: str, all_caps_title: bool) -> str | None:
    for entry in acronyms():
        if token.casefold() != entry.casefold():
            continue
        if token == entry or entry[0].isdigit() or entry == "deal.II":
            return entry
        if token.isupper() and (entry != "eN" or all_caps_title):
            return entry
    return None


def _clean_dots(token: str) -> str:
    if token.casefold() == "deal.ii":
        return token
    return re.sub(r"(?<!\d)\.|\.(?!\d)", "", token)


def _title_token(token: str, all_caps_title: bool, unknown: list[str]) -> str:
    if token.lower() in {"w", "w/"}:
        return "with"
    parts = []
    for part in token.split("-"):
        canon = _canonical(part, all_caps_title)
        if (
            canon is None
            and part.endswith("s")
            and part[:-1].isupper()
            and len(part) > 2
        ):
            plural = _canonical(part[:-1], all_caps_title)
            canon = plural + "s" if plural else None
        if canon is None:
            if (
                not all_caps_title
                and sum(c.isupper() for c in part) >= 2
                and not any(c.islower() for c in part)
            ):
                unknown.append(part)
            canon = part.lower()
        parts.append(canon)
    return "-".join(parts)


def title_snake(title: str) -> str:
    """Convert a title to the snake case title part.

    Args:
        title: published title, may hold HTML or MathML.

    Returns:
        Snake case title.

    Raises:
        UnknownAcronymError: all caps tokens are not whitelisted.
        NamingError: the title is empty.
    """
    text = html.unescape(re.sub(r"<[^>]+>", "", title)).translate(_DASHES)
    text = fold(text).replace("&", " and ")
    text = "".join(c for c in text if c not in _DELETED)
    text = re.sub(r"[^A-Za-z0-9.\s-]", " ", text)
    all_caps_title = not any(c.islower() for c in text)
    unknown: list[str] = []
    tokens = []
    for raw in text.split():
        token = _clean_dots(raw).strip("-")
        if token:
            tokens.append(_title_token(token, all_caps_title, unknown))
    if unknown:
        raise UnknownAcronymError(sorted(set(unknown)))
    if not tokens:
        raise NamingError("empty title")
    return "_".join(tokens)


def surname(family: str) -> str:
    """Convert a family name to its file name form.

    Args:
        family: family name, particles included (van Tooren).

    Returns:
        Surname with particles joined by underscores.
    """
    words = [
        w for w in fold(family).replace(",", " ").split() if w.lower() not in _SUFFIXES
    ]
    words = [re.sub(r"[^A-Za-z0-9-]", "", w) for w in words]
    return "_".join(w for w in words if w)


def format_name(title: str, families: Sequence[str], year: str | int) -> str:
    """Build the name stem shared by a paper folder and its PDF.

    Args:
        title: published title.
        families: family names (or organisation, editor, lecturer) in paper order.
        year: year of the content.

    Returns:
        Name without extension.

    Raises:
        NamingError: missing author or invalid year or result.
    """
    authors = [s for s in (surname(f) for f in families) if s]
    if not authors:
        raise NamingError("no author")
    parts = [title_snake(title), *authors[:MAX_AUTHORS]]
    if len(authors) > MAX_AUTHORS:
        parts.append("et_al")
    year_str = str(year).strip()
    if not re.fullmatch(r"(19|20)\d\d", year_str):
        raise NamingError(f"invalid year {year!r}")
    name = re.sub(r"_+", "_", "_".join([*parts, year_str]))
    if not NAME_RE.fullmatch(name) or len(name.encode()) + len(".pdf") > MAX_BYTES:
        raise NamingError(f"invalid name {name!r}")
    return name


def doc_families(doc: dict) -> list[str]:
    """Extract family names from papis document data.

    Args:
        doc: papis document or info.yaml mapping.

    Returns:
        Family names in paper order.
    """
    authors = doc.get("author_list") or []
    families = [a.get("family") or a.get("given") or "" for a in authors]
    if not any(families) and doc.get("author"):
        families = [p.split(",")[0] for p in str(doc["author"]).split(" and ")]
    return families


def doc_name(doc: dict) -> str:
    """Build the name stem for papis document data.

    Args:
        doc: papis document or info.yaml mapping.

    Returns:
        Name without extension.

    Raises:
        NamingError: title missing or metadata invalid.
    """
    if not doc.get("title"):
        raise NamingError("no title")
    return format_name(str(doc["title"]), doc_families(doc), doc.get("year", ""))
