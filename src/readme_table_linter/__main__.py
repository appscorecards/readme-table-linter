"""CLI entry point."""

from __future__ import annotations

import argparse
import sys
from typing import List

from readme_table_linter.linter import Issue, lint_file


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="readme-table-linter",
        description="Lint markdown tables in the given files.",
    )
    p.add_argument("files", nargs="+", help="One or more markdown files.")
    return p


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    issues: List[Issue] = []
    for path in args.files:
        issues.extend(lint_file(path))
    for issue in issues:
        print(issue.format())
    return 1 if issues else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
