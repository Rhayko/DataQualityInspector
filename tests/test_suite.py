import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from data_quality_inspector.inspector import inspect_csv
from data_quality_inspector.profiling import column_profile
from data_quality_inspector.validation import duplicate_mask, find_outliers, find_type_issues


class DataQualityInspectorTests(unittest.TestCase):
    def test_duplicate_mask_flags_every_member_of_group(self):
        frame = pd.DataFrame({"id": [1, 1, 2], "value": ["a", "a", "b"]})
        self.assertEqual(duplicate_mask(frame).tolist(), [True, True, False])

    def test_type_validation_separates_missing_and_invalid_values(self):
        frame = pd.DataFrame({"amount": ["10", None, "12.5", "bad"], "date": ["2025-01-01", "", None, "not-a-date"]})
        issues = find_type_issues(frame, {"amount": "numeric", "date": "date"})
        self.assertEqual([(issue.column, issue.invalid_count) for issue in issues], [("amount", 1), ("date", 1)])
        self.assertEqual(issues[0].examples, ("bad",))

    def test_integer_validation_rejects_decimal_values(self):
        issues = find_type_issues(pd.DataFrame({"count": ["4", "4.5"]}), {"count": "integer"})
        self.assertEqual(issues[0].invalid_count, 1)

    def test_unknown_expected_type_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported expected type"):
            find_type_issues(pd.DataFrame({"x": [1]}), {"x": "currency"})

    def test_iqr_outlier_reports_csv_row_number(self):
        result = find_outliers(pd.DataFrame({"measurement": [10, 11, 10, 9, 10, 100]}))
        self.assertEqual(result[0].count, 1)
        self.assertEqual(result[0].row_numbers, (7,))

    def test_profile_reports_missingness_and_statistics(self):
        profile = column_profile(pd.DataFrame({"score": [1.0, 2.0, None], "group": ["a", "a", "b"]})).set_index("column")
        self.assertEqual(profile.loc["score", "missing_percent"], 33.33)
        self.assertEqual(profile.loc["score", "mean"], 1.5)
        self.assertEqual(profile.loc["group", "unique_count"], 2)

    def test_empty_dataset_profiles_without_dividing_by_zero(self):
        profile = column_profile(pd.DataFrame(columns=["empty"]))
        self.assertEqual(profile.loc[0, "missing_percent"], 0.0)

    def test_complete_inspection_writes_report_bundle(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_path = root / "input.csv"
            pd.DataFrame(
                {
                    "id": [1, 2, 2, 3, 4, 5, 6],
                    "amount": [10, 11, 11, None, 9, 10, 100],
                    "date": ["2025-01-01", "bad", "bad", "2025-01-04", "2025-01-05", "2025-01-06", "2025-01-07"],
                }
            ).to_csv(input_path, index=False)
            config_path = root / "config.json"
            config_path.write_text(json.dumps({"expected_types": {"date": "date"}, "outlier_columns": ["amount"]}))
            result = inspect_csv(input_path, root / "report", config_path)
            self.assertEqual((result.rows, result.missing_cells, result.duplicate_rows), (7, 1, 2))
            self.assertEqual(result.type_issues[0].invalid_count, 2)
            expected = {"data_quality_report.md", "summary.json", "column_profile.csv", "duplicate_rows.csv", "missing_values.png", "numeric_distributions.png"}
            self.assertTrue(expected.issubset({path.name for path in (root / "report").iterdir()}))


if __name__ == "__main__":
    unittest.main()

