# Data Quality Inspector

I built Data Quality Inspector to turn a CSV into an evidence-based quality review. It profiles the data, flags common risks, creates two visualizations, and produces a report that can be read directly on GitHub.

![Example missing-values chart](outputs/example/missing_values.png)

## Why I Built This

I know an analysis is only as reliable as its input data. CSV files are convenient, but they do not enforce types, uniqueness, completeness, or reasonable numeric ranges. Those problems are often discovered after calculations or dashboards have already been built.

I built this project to move that review to the beginning of the workflow. I intentionally do not “clean” questionable records silently. Instead, I show what needs attention so the analyst can make a defensible decision with the right domain context.

## What It Does

- I profile row and column counts, detected types, completeness, unique values, and numeric summary statistics.
- I report missing-value counts and percentages by column.
- I export every row that belongs to a full-row duplicate group.
- I validate configured numeric, integer, date, and boolean expectations.
- I flag potential numeric outliers with the 1.5 × IQR rule.
- I produce missing-value and numeric-distribution charts.
- I write a readable Markdown report plus reusable CSV and JSON outputs.
- I keep the tool to one command with no web framework or external service dependency.

## How I Designed It

I use a command-line layer to accept the input, output, and optional rule-configuration paths. A small coordinator loads the CSV and calls independent profiling and validation functions. I keep reporting and visualization separate so each check is easier to test and the output formats can be changed without rewriting the validation logic.

I use an optional JSON configuration to make data expectations explicit without hard-coding them into the program:

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

I keep type failures, missing values, duplicates, and potential outliers as separate findings. That distinction matters to me because a blank value is not the same problem as the word `unknown` in a numeric field, and an unusual measurement is not automatically an error.

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
├── pyproject.toml
└── requirements.txt
```

## What the Example Shows

I included a synthetic manufacturing file with 182 inspection records and deliberately seeded quality problems. When I ran the inspector, it found:

| Finding | Result |
| --- | ---: |
| Missing cells | 7 |
| Rows in duplicate groups | 4 |
| Invalid typed values | 4 |
| Potential outliers | 9 |

My type review identifies an impossible date, a written phrase in an integer column, and invalid text in two numeric columns. I also include the calculated outlier bounds and original CSV row numbers so every finding can be investigated.

I committed the complete [example report](outputs/example/data_quality_report.md), [column profile](outputs/example/column_profile.csv), and [JSON summary](outputs/example/summary.json) so the results can be reviewed without running the code first. The sample is entirely synthetic and reproducible; I document its creation in [data provenance](data/PROVENANCE.md).

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

I test missingness and summary statistics, complete duplicate-group detection, numeric/integer/date type checks, unsupported configuration, IQR outliers and CSV row numbers, empty input behavior, and a complete report build. I generated the committed example output with the same public command shown above.

To reproduce the synthetic source file before regenerating the report:

```bash
python scripts/generate_sample_data.py
```

## Current Limitations

- I currently compare complete rows for duplicates; business-key duplicates would require a configurable key rule.
- I configure CSV type expectations manually because the format carries no reliable schema.
- I treat IQR flags as statistical review prompts, not proof that a value is wrong.
- I read the file into memory, so this version is intended for analyst-sized datasets rather than distributed processing.
- I do not modify or impute data because remediation should be a separate, documented decision.
