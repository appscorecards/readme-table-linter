"""Core linter logic (first pass: separator detection only)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


SEPARATOR_CELL = re.compile(r"^\s*:?-+:?\s*$")


@dataclass(frozen=True)
class Issue:
    file: str
    line: int
    code: str
    message: str

    def format(self) -> str:
        return f"{self.file}:{self.line}: {self.message}"


def _split_cells(row: str) -> List[str]:
    stripped = row.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return stripped.split("|")


def _is_separator_row(row: str) -> bool:
    cells = _split_cells(row)
    if not cells:
        return False
    return all(SEPARATOR_CELL.match(c) for c in cells)


def _looks_like_table_row(row: str) -> bool:
    stripped = row.strip()
    return (
        stripped.startswith("|")
        and stripped.endswith("|")
        and stripped.count("|") >= 2
    )


def lint_text(text: str, filename: str = "<stdin>") -> List[Issue]:
    issues: List[Issue] = []
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        if not _looks_like_table_row(lines[i]):
            i += 1
            continue
        header_idx = i
        next_idx = header_idx + 1
        has_next = next_idx < n and _looks_like_table_row(lines[next_idx])
        if not has_next or not _is_separator_row(lines[next_idx]):
            issues.append(
                Issue(
                    filename,
                    header_idx + 1,
                    "missing-separator",
                    "table starting here is missing a header separator row",
                )
            )
            j = header_idx + 1
            while j < n and _looks_like_table_row(lines[j]):
                j += 1
            i = j
            continue
        # Skip over body rows for now; more checks come in later commits.
        j = header_idx + 2
        while j < n and _looks_like_table_row(lines[j]):
            j += 1
        i = j
    return issues


def lint_file(path: str | Path) -> List[Issue]:
    p = Path(path)
    return lint_text(p.read_text(encoding="utf-8"), str(p))
