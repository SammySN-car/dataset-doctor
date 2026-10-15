# Dataset Doctor

Dataset Doctor is a command-line tool for diagnosing CSV dataset quality and
machine-learning readiness. It loads a CSV file, calculates structural
statistics, detects a small set of common data-quality issues, and renders a
terminal, JSON, or standalone HTML report.

[GitHub repository](https://github.com/SammySN-car/dataset-doctor) ·
[Issue tracker](https://github.com/SammySN-car/dataset-doctor/issues)

## Current features

- CSV loading with UTF-8 and UTF-8 BOM support.
- Strict header and row-width validation.
- Row and column counts.
- Pandas-inferred column dtypes.
- Missing-value counts and percentages.
- Duplicate-row counts beyond the first occurrence.
- Constant-column detection.
- Structured findings with severity, descriptions, and numeric evidence.
- Terminal, deterministic JSON, and standalone HTML reports.

This project deliberately does not yet implement streaming, automatic
cleaning, outlier detection, target analysis, mixed-runtime-type detection,
recommendations, or additional report formats.

## Installation

Create and activate a virtual environment, then install the project with its
development tools:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

The runtime dependency is pandas. The `dev` extra adds pytest and Ruff.

## Usage

Profile a CSV file using the terminal report:

```powershell
dataset-doctor profile data.csv
```

Select a report format with `--format`:

```powershell
dataset-doctor profile data.csv --format terminal
dataset-doctor profile data.csv --format json
dataset-doctor profile data.csv --format html
```

Terminal output is intended for interactive use. JSON is a deterministic,
indented machine-readable document. HTML is a standalone document with inline
CSS and no external assets.

### Demonstration

The synthetic [sample.csv](examples/sample.csv) demonstrates a missing value,
a duplicate row, a constant column, and ordinary numeric and text columns:

```powershell
dataset-doctor profile examples\sample.csv
dataset-doctor profile examples\sample.csv --format json
dataset-doctor profile examples\sample.csv --format html
```

The commands write reports to stdout. Redirect the JSON or HTML output when a
file is needed:

```powershell
dataset-doctor profile examples\sample.csv --format json > sample-report.json
dataset-doctor profile examples\sample.csv --format html > sample-report.html
```

## Supported findings

Dataset Doctor currently reports:

- `missing_values` (`warning`): a column contains some, but not all, missing
  values.
- `all_missing_column` (`error`): a non-empty column contains only missing
  values.
- `constant_column` (`warning`): a column has at most one distinct non-missing
  value. All-missing columns are reported as `all_missing_column` instead of
  receiving a redundant constant-column finding.
- `duplicate_rows` (`warning`): the dataset contains duplicate row
  occurrences beyond the first row in each duplicate group.

A successful analysis exits with status 0 even when findings are present.

## Input validation

CSV input must be UTF-8, may include a UTF-8 BOM, and must contain a header and
at least one data row. Quoted commas and quoted fields containing embedded
newlines are supported. Duplicate column names, including repeated empty
header names, are rejected. Data rows with fewer or more fields than the
header are rejected. Blank fields are interpreted as missing values by pandas.
Input files are never modified.

Expected input errors are reported concisely on stderr without a traceback.

## Development

Run the test suite:

```powershell
python -m pytest
```

Run Ruff:

```powershell
ruff check .
```

GitHub Actions runs the same installation, test, and Ruff checks on every
push and pull request using the minimum supported Python version.

The package uses a `src/` layout and exposes the `dataset-doctor` console
script. Module invocation is also available:

```powershell
python -m dataset_doctor.cli profile examples\sample.csv
```

## Scalability limitation

CSV files are loaded eagerly into pandas memory. Profiling operations such as
duplicate detection and per-column uniqueness calculations may require
substantial memory for large datasets. There are currently no automatic file
size limits, streaming safeguards, or chunked-processing mode.

## Release notes

Generated JSON and HTML reports are demonstration outputs and are not required
for the source distribution. For a portfolio README, terminal output or a
locally captured HTML report can be used as a screenshot source without
committing generated report files.

## License

Dataset Doctor is licensed under the [MIT License](LICENSE).
