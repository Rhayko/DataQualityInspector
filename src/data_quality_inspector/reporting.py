"""Markdown and machine-readable report output."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .validation import OutlierSummary, TypeIssue


def _markdown_table(frame: pd.DataFrame) -> str:
    display = frame.fillna("—").astype(str)
    headers = list(display.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in display.itertuples(index=False, name=None))
    return "\n".join(lines)


def write_report(
    *,
    source_name: str,
    frame: pd.DataFrame,
    profile: pd.DataFrame,
    duplicate_count: int,
    type_issues: list[TypeIssue],
    outliers: list[OutlierSummary],
    output_dir: Path,
) -> Path:
    missing_cells = int(frame.isna().sum().sum())
    issue_total = missing_cells + duplicate_count + sum(item.invalid_count for item in type_issues) + sum(item.count for item in outliers)
    status = "Review recommended" if issue_total else "No issues detected"

    type_rows = pd.DataFrame(
        [{"column": item.column, "expected": item.expected_type, "invalid": item.invalid_count, "examples": ", ".join(item.examples)} for item in type_issues]
    )
    outlier_rows = pd.DataFrame(
        [{"column": item.column, "potential outliers": item.count, "lower bound": item.lower_bound, "upper bound": item.upper_bound, "CSV rows": ", ".join(map(str, item.row_numbers))} for item in outliers]
    )

    text = f"""# Data Quality Report: {source_name}

## Executive summary

**Status:** {status}

- Rows: **{len(frame):,}**
- Columns: **{len(frame.columns):,}**
- Missing cells: **{missing_cells:,}**
- Rows in duplicate groups: **{duplicate_count:,}**
- Invalid typed values: **{sum(item.invalid_count for item in type_issues):,}**
- Potential outliers: **{sum(item.count for item in outliers):,}**

Potential outliers and invalid values are review flags, not automatic deletion decisions.

## Column profile

{_markdown_table(profile)}

## Type validation

{_markdown_table(type_rows) if not type_rows.empty else "No type inconsistencies found for configured columns."}

## Potential outliers

{_markdown_table(outlier_rows) if not outlier_rows.empty else "No potential outliers found in numeric columns."}

## Visual review

![Missing values](missing_values.png)

{"![Numeric distributions](numeric_distributions.png)" if (output_dir / "numeric_distributions.png").exists() else "No numeric columns were available to chart."}

## Interpretation notes

- Missingness may be legitimate; investigate the collection process before filling or dropping values.
- Duplicate counts include every member of a duplicate group so the report shows the full review scope.
- Type validation uses declared expectations from the configuration file.
- Outliers use the 1.5 × IQR rule. They may be valid rare events and should be checked with domain context.
"""
    report_path = output_dir / "data_quality_report.md"
    report_path.write_text(text, encoding="utf-8")

    payload = {
        "source": source_name,
        "rows": len(frame),
        "columns": len(frame.columns),
        "missing_cells": missing_cells,
        "duplicate_rows": duplicate_count,
        "type_issues": [item.__dict__ for item in type_issues],
        "outliers": [item.__dict__ for item in outliers],
    }
    (output_dir / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path

