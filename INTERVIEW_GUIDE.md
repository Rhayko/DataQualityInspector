# Interview Guide

## The 30-second explanation

“Data Quality Inspector is a small Python tool that accepts a CSV and produces a repeatable quality review. It profiles the dataset, finds missing and duplicate records, checks selected columns against expected types, flags unusual numeric values, and creates both a readable Markdown report and machine-readable outputs. I separated the checks from reporting so each rule is easy to test, explain, and change.”

## Walkthrough by major part

- `cli.py` handles the user's command and passes paths to the inspector.
- `inspector.py` is the coordinator. It loads the CSV and configuration, calls each focused check, and sends the results to the output modules.
- `profiling.py` builds one summary row per column: detected pandas type, completeness, distinct values, and numeric statistics.
- `validation.py` contains the business rules. Keeping them as small functions makes their behavior easy to test independently.
- `visualization.py` creates two charts that help a reviewer spot missingness and unusual distributions quickly.
- `reporting.py` turns the findings into Markdown, CSV, and JSON outputs for human review or downstream use.

## How to explain each check

### Missing values

Pandas identifies null cells column by column. The project reports both a count and percentage because ten missing records mean something different in a 20-row dataset than in a million-row dataset. A missing value is reported, not automatically filled or removed; the correct response depends on why it is missing.

### Duplicates

The tool compares complete rows and uses `keep=False`, which marks every row in a duplicate group. That is deliberate: a reviewer needs to see the original and all copies. In a production system, the duplicate key might instead be configurable because identical rows are not always errors.

### Type validation

CSV files do not enforce a schema. A mostly numeric column can contain a phrase such as “unknown.” The JSON configuration declares what selected columns should contain. The validator attempts a safe conversion and reports non-empty values that cannot be converted. Missing values remain a separate quality dimension.

### Potential outliers

For numeric columns, the tool calculates the first and third quartiles and the interquartile range (IQR). Values below `Q1 - 1.5 × IQR` or above `Q3 + 1.5 × IQR` are flagged. This method is understandable and resistant to extreme values, but a flag is not proof of bad data. A legitimate production shutdown could look like an outlier.

### Design decisions

- A command-line tool keeps dependencies and setup small while still being useful on any CSV.
- JSON configuration separates dataset expectations from Python code.
- Markdown is readable on GitHub; CSV and JSON make the results reusable.
- Functions return structured results instead of only printing text, which makes testing and future integration easier.
- The project avoids a web framework because a user interface would add complexity without strengthening the core data-quality demonstration.

## Questions you may be asked

**Why not delete duplicates or outliers automatically?**  
Because detection and remediation are different decisions. Domain context determines whether a repeated row or extreme value is an error.

**Why does pandas initially show some numeric-looking columns as text?**  
A single malformed value can cause the whole CSV column to load as an object/string type. The explicit type check exposes that issue.

**How would you extend it?**  
Add configurable uniqueness, allowed-value, range, and cross-column rules; support larger files in chunks; compare quality over time; and publish a CI report on incoming datasets.

**What would change for production scale?**  
I would add structured logging, versioned rule configuration, chunked or distributed processing, severity levels, stored historical metrics, and alerting. I would keep the validation functions independent and testable.

