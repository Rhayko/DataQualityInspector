"""Generate a reproducible, synthetic manufacturing-quality dataset."""

from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    rng = np.random.default_rng(42)
    rows = 180
    frame = pd.DataFrame(
        {
            "batch_id": [f"B-{1001 + index}" for index in range(rows)],
            "inspection_date": pd.date_range("2025-01-02", periods=rows, freq="D").strftime("%Y-%m-%d"),
            "plant": rng.choice(["North", "Central", "South"], rows, p=[0.35, 0.4, 0.25]),
            "shift": rng.choice(["Day", "Evening", "Night"], rows),
            "product_line": rng.choice(["Alpha", "Bravo", "Charlie"], rows),
            "inspector_id": rng.choice(["I-104", "I-117", "I-126", "I-133", "I-141"], rows),
            "units_produced": rng.normal(510, 42, rows).round().astype(int),
            "defect_rate_pct": np.clip(rng.normal(2.8, 0.75, rows), 0.3, None).round(2),
            "downtime_minutes": np.clip(rng.gamma(2.2, 8, rows), 0, None).round(1),
            "temperature_c": rng.normal(22.5, 1.6, rows).round(1),
            "inspection_status": rng.choice(["Pass", "Review", "Hold"], rows, p=[0.84, 0.12, 0.04]),
        }
    )

    # CSVs can hold mixed values even when a column is intended to be numeric.
    frame[["units_produced", "defect_rate_pct", "downtime_minutes"]] = frame[
        ["units_produced", "defect_rate_pct", "downtime_minutes"]
    ].astype(object)

    # Seed realistic quality problems for demonstration and automated validation.
    frame.loc[[8, 47, 112, 154], "inspector_id"] = np.nan
    frame.loc[[21, 67, 68], "temperature_c"] = np.nan
    frame.loc[31, "inspection_date"] = "2025-02-30"
    frame.loc[73, "units_produced"] = "five hundred"
    frame.loc[125, "defect_rate_pct"] = "n/a?"
    frame.loc[145, "downtime_minutes"] = "unknown"
    frame.loc[42, "defect_rate_pct"] = 14.8
    frame.loc[96, "downtime_minutes"] = 138.0
    frame.loc[161, "temperature_c"] = 35.6
    frame = pd.concat([frame, frame.iloc[[15]], frame.iloc[[88]]], ignore_index=True)

    destination = Path(__file__).resolve().parents[1] / "data" / "sample_manufacturing_quality.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)
    print(f"Wrote {len(frame)} synthetic rows to {destination}")


if __name__ == "__main__":
    main()
