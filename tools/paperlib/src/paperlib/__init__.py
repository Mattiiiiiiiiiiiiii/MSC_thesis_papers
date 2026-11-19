# Copyright (c) 2026 Harmattan AI.
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("paperlib")
except PackageNotFoundError:
    __version__ = "unknown"
