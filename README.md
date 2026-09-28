# Data Quality Inspector

A focused Python tool that turns a CSV into an evidence-based data-quality review. It profiles the data, flags common risks, creates two visualizations, and produces a report that can be read directly on GitHub.

![Example missing-values chart](outputs/example/missing_values.png)

## Problem

Analysis is only as reliable as its input data. CSV files are convenient, but they do not enforce types, uniqueness, completeness, or reasonable numeric ranges. Analysts often discover these problems after calculations or dashboards have already been built.

Data Quality Inspector moves that review to the beginning of the workflow. It does not silently “clean” questionable records. It shows what needs attention so an analyst can make a defensible decision with domain context.

## Features

- Profiles row and column counts, detected types, completeness, unique values, and numeric summary statistics.
- Reports missing-value counts and percentages by column.
- Exports every row that belongs to a full-row duplicate group.
- Validates configured numeric, integer, date, and boolean expectations.
- Flags potential numeric outliers with the 1.5 × IQR rule.
- Produces missing-value and numeric-distribution charts.
- Writes a readable Markdown report plus reusable CSV and JSON outputs.
- Runs from one command and has no web framework or external service dependency.

## Approach

The command-line layer accepts the input, output, and optional rule configuration paths. A small coordinator loads the CSV and calls independent profiling and validation functions. Reporting and visualization are separate, which keeps the checks easy to test and makes output formats replaceable.

The optional JSON configuration makes expectations explicit without hard-coding them into the program:

```json
{
  "expected_types": {
    "inspection_date": "date",
    "units_produced": "integer",
    "defect_rate_pct": "numeric"
  },
  "outlier_columns": ["units_produced", "defect_rate_pct"]
}
```

Type failures, missing values, duplicates, and potential outliers remain separate findings. That distinction matters: a blank value is not the same problem as the word `unknown` in a numeric field, and an unusual measurement is not automatically an error.

## Project Structure

```text
data-quality-inspector/
├── config/                     # Example expectations for the sample CSV
├── data/                       # Synthetic data and provenance
├── outputs/example/            # Committed example report bundle
├── scripts/                    # Reproducible sample-data generator
├── src/data_quality_inspector/
│   ├── cli.py                  # Command-line arguments
│   ├── inspector.py            # Workflow coordinator
│   ├── profiling.py            # Column-level summaries
│   ├── validation.py           # Duplicate, type, and outlier rules
│   ├── visualization.py        # Report charts
│   └── reporting.py            # Markdown, CSV, and JSON output
├── tests/                      # Unit and end-to-end coverage
├── INTERVIEW_GUIDE.md          # Plain-language project walkthrough
├── pyproject.toml
└── requirements.txt
```

## Example Results

The included synthetic manufacturing file contains 182 inspection records and deliberately seeded quality problems. The generated example report found:

| Finding | Result |
| --- | ---: |
| Missing cells | 7 |
| Rows in duplicate groups | 4 |
| Invalid typed values | 4 |
| Potential outliers | 9 |

The type review identifies an impossible date, a written phrase in an integer column, and invalid text in two numeric columns. The outlier results include the calculated bounds and original CSV row numbers for investigation.

See the complete [example report](outputs/example/data_quality_report.md), [column profile](outputs/example/column_profile.csv), and [JSON summary](outputs/example/summary.json). The sample is entirely synthetic and reproducible; details are in [data provenance](data/PROVENANCE.md).

## How to Run

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Inspect the included sample:

```bash
inspect-data data/sample_manufacturing_quality.csv \
  --config config/sample_config.json \
  --output outputs/my-report
```

Inspect any CSV without configured type expectations:

```bash
inspect-data path/to/your_file.csv --output outputs/my-report
```

The output folder contains:

- `data_quality_report.md` — the main readable report;
- `summary.json` — headline results for another system;
- `column_profile.csv` — a sortable column-level inventory;
- `duplicate_rows.csv` — all members of full-row duplicate groups;
- `missing_values.png` and `numeric_distributions.png` — review charts.

## Validation / Testing

Run the automated checks from the repository root:

```bash
python -m unittest discover -s tests -v
```

The suite covers missingness and summary statistics, complete duplicate-group detection, numeric/integer/date type checks, unsupported configuration, IQR outliers and CSV row numbers, empty input behavior, and an end-to-end report build. The committed example output was generated with the same public command shown above.

To reproduce the synthetic source file before regenerating the report:

```bash
python scripts/generate_sample_data.py
```

## Limitations

- Duplicate detection currently compares complete rows; business-key duplicates require a configurable key rule.
- CSV type expectations are configured manually because the format carries no reliable schema.
- IQR flags are statistical review prompts, not proof that a value is wrong.
- The tool reads a file into memory and is intended for analyst-sized datasets, not distributed processing.
- It does not modify or impute data; remediation should be a separate, documented decision.
