"""Command-line interface for the data-quality inspector."""

from __future__ import annotations

import argparse
from pathlib import Path

from .inspector import inspect_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Profile a CSV and generate a data-quality report.")
    parser.add_argument("csv", type=Path, help="Path to the CSV file to inspect")
    parser.add_argument("--output", type=Path, default=Path("outputs/report"), help="Directory for report files")
    parser.add_argument("--config", type=Path, help="Optional JSON file with expected types and outlier columns")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = inspect_csv(args.csv, args.output, args.config)
    print(f"Inspected {result.rows:,} rows and {result.columns:,} columns.")
    print(f"Report written to {result.report_path}")


if __name__ == "__main__":
    main()

