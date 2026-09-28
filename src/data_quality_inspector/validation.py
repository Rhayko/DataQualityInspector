"""Reusable checks for common tabular data-quality problems."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TypeIssue:
    column: str
    expected_type: str
    invalid_count: int
    examples: tuple[str, ...]


@dataclass(frozen=True)
class OutlierSummary:
    column: str
    count: int
    lower_bound: float
    upper_bound: float
    row_numbers: tuple[int, ...]


def duplicate_mask(frame: pd.DataFrame) -> pd.Series:
    """Flag every row belonging to a duplicate group, including the first."""
    return frame.duplicated(keep=False)


def find_type_issues(
    frame: pd.DataFrame, expected_types: dict[str, str]
) -> list[TypeIssue]:
    """Validate non-empty values against numeric, integer, date, or boolean types."""
    issues: list[TypeIssue] = []
    converters = {
        "numeric": lambda values: pd.to_numeric(values, errors="coerce"),
        "integer": lambda values: pd.to_numeric(values, errors="coerce").where(
            lambda converted: converted.mod(1).eq(0)
        ),
        "date": lambda values: pd.to_datetime(values, errors="coerce"),
        "boolean": lambda values: values.astype(str).str.lower().map(
            {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
        ),
    }

    for column, expected in expected_types.items():
        if column not in frame.columns:
            continue
        if expected not in converters:
            raise ValueError(f"Unsupported expected type '{expected}' for column '{column}'.")

        source = frame[column]
        present = source.notna() & source.astype(str).str.strip().ne("")
        converted = converters[expected](source[present])
        invalid_values = source[present][converted.isna()]
        if not invalid_values.empty:
            examples = tuple(invalid_values.astype(str).drop_duplicates().head(3))
            issues.append(TypeIssue(column, expected, len(invalid_values), examples))

    return issues


def find_outliers(frame: pd.DataFrame, columns: list[str] | None = None) -> list[OutlierSummary]:
    """Identify potential numeric outliers with the 1.5 × IQR rule."""
    candidates = columns or list(frame.select_dtypes(include=np.number).columns)
    summaries: list[OutlierSummary] = []

    for column in candidates:
        if column not in frame.columns:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        usable = values.dropna()
        if len(usable) < 4:
            continue

        q1, q3 = usable.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = float(q1 - 1.5 * iqr), float(q3 + 1.5 * iqr)
        mask = values.lt(lower) | values.gt(upper)
        if mask.any():
            summaries.append(
                OutlierSummary(
                    column=column,
                    count=int(mask.sum()),
                    lower_bound=round(lower, 3),
                    upper_bound=round(upper, 3),
                    row_numbers=tuple(int(index) + 2 for index in frame.index[mask]),
                )
            )

    return summaries

