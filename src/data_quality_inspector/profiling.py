"""Dataset profiling and descriptive statistics."""

from __future__ import annotations

import pandas as pd


def column_profile(frame: pd.DataFrame) -> pd.DataFrame:
    """Return one concise profile row for every input column."""
    rows: list[dict[str, object]] = []
    total = len(frame)

    for name in frame.columns:
        series = frame[name]
        non_null = series.dropna()
        row: dict[str, object] = {
            "column": name,
            "dtype": str(series.dtype),
            "non_null_count": int(series.notna().sum()),
            "missing_count": int(series.isna().sum()),
            "missing_percent": round(float(series.isna().mean() * 100), 2) if total else 0.0,
            "unique_count": int(non_null.nunique()),
        }

        numeric = pd.to_numeric(series, errors="coerce")
        numeric_share = float(numeric.notna().sum() / len(non_null)) if len(non_null) else 0.0
        summary_values = series if pd.api.types.is_numeric_dtype(series) else numeric
        if numeric_share >= 0.8 and summary_values.notna().any():
            summary_values = summary_values.dropna()
            row.update(
                {
                    "mean": round(float(summary_values.mean()), 3),
                    "median": round(float(summary_values.median()), 3),
                    "min": round(float(summary_values.min()), 3),
                    "max": round(float(summary_values.max()), 3),
                    "std": round(float(summary_values.std()), 3),
                }
            )
        else:
            row.update({"mean": None, "median": None, "min": None, "max": None, "std": None})

        rows.append(row)

    return pd.DataFrame(rows)
