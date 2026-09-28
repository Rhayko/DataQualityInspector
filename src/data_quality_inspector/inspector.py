"""Orchestrate a complete CSV inspection."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import pandas as pd

from .profiling import column_profile
from .reporting import write_report
from .validation import OutlierSummary, TypeIssue, duplicate_mask, find_outliers, find_type_issues
from .visualization import save_missing_values_chart, save_numeric_distributions


@dataclass(frozen=True)
class InspectionResult:
    report_path: Path
    rows: int
    columns: int
    missing_cells: int
    duplicate_rows: int
    type_issues: tuple[TypeIssue, ...]
    outliers: tuple[OutlierSummary, ...]


def inspect_csv(csv_path: Path, output_dir: Path, config_path: Path | None = None) -> InspectionResult:
    """Read a CSV, run all checks, and write a compact report bundle."""
    frame = pd.read_csv(csv_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    config: dict[str, object] = {}
    if config_path:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    expected_types = dict(config.get("expected_types", {}))
    outlier_columns = config.get("outlier_columns")

    profile = column_profile(frame)
    duplicates = duplicate_mask(frame)
    type_issues = find_type_issues(frame, expected_types)
    outliers = find_outliers(frame, outlier_columns if isinstance(outlier_columns, list) else None)

    profile.to_csv(output_dir / "column_profile.csv", index=False)
    frame.loc[duplicates].to_csv(output_dir / "duplicate_rows.csv", index=False)
    save_missing_values_chart(frame, output_dir / "missing_values.png")
    save_numeric_distributions(frame, output_dir / "numeric_distributions.png")
    report_path = write_report(
        source_name=csv_path.name,
        frame=frame,
        profile=profile,
        duplicate_count=int(duplicates.sum()),
        type_issues=type_issues,
        outliers=outliers,
        output_dir=output_dir,
    )

    return InspectionResult(
        report_path=report_path,
        rows=len(frame),
        columns=len(frame.columns),
        missing_cells=int(frame.isna().sum().sum()),
        duplicate_rows=int(duplicates.sum()),
        type_issues=tuple(type_issues),
        outliers=tuple(outliers),
    )

