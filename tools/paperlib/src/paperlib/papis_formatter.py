# Copyright (c) 2026 Harmattan AI.
"""Papis formatter plugin: python formatter plus the {thesis_name} pattern."""

from typing import Any

from papis.document import DocumentLike, from_data
from papis.format import FormatFailedError
from papis.format.python import PythonFormatter

from paperlib.naming import NamingError, doc_name

THESIS_PATTERN = "{thesis_name}"


class ThesisFormatter(PythonFormatter):
    """Python formatter where the pattern {thesis_name} yields the naming_rules.out stem."""

    name = "thesis"

    def format(
        self,
        fmt: str,
        doc: DocumentLike,
        doc_key: str = "",
        additional: dict[str, Any] | None = None,
        default: str | None = None,
    ) -> str:
        """Format *fmt*; {thesis_name} is replaced by the document name stem.

        Args:
            fmt: format pattern.
            doc: papis document.
            doc_key: document name in the pattern.
            additional: extra pattern entries.
            default: fallback pattern on failure.

        Returns:
            Formatted string.

        Raises:
            FormatFailedError: the name cannot be built and no default is given.
        """
        if fmt.strip() != THESIS_PATTERN:
            return super().format(
                fmt, doc, doc_key=doc_key, additional=additional, default=default
            )
        try:
            return doc_name(dict(from_data(doc)))
        except NamingError as exc:
            if default is not None:
                return super().format(
                    default, doc, doc_key=doc_key, additional=additional
                )
            raise FormatFailedError(str(exc)) from exc
