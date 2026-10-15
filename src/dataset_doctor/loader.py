"""CSV loading and input validation."""

import csv
from os import PathLike
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


class CSVLoadError(Exception):
    """Raised when a CSV file cannot be loaded or does not meet requirements."""


def load_csv(path: str | PathLike[str]) -> pd.DataFrame:
    """Load a UTF-8 CSV with a header and at least one data row."""
    csv_path = Path(path)

    if not csv_path.exists():
        raise CSVLoadError(f"CSV file does not exist: {csv_path}")
    if csv_path.is_dir():
        raise CSVLoadError(f"Expected a CSV file, but received a directory: {csv_path}")

    _validate_csv_structure(csv_path)

    try:
        dataframe = pd.read_csv(
            csv_path,
            encoding="utf-8",
            header=0,
            on_bad_lines="error",
        )
    except UnicodeDecodeError as error:
        raise CSVLoadError(
            f"CSV file is not valid UTF-8: {csv_path}. "
            "Save the file as UTF-8 and try again."
        ) from error
    except EmptyDataError as error:
        raise CSVLoadError(
            f"CSV file is empty: {csv_path}. "
            "Provide a header row and at least one data row."
        ) from error
    except ParserError as error:
        raise CSVLoadError(
            f"CSV file is malformed: {csv_path}. "
            "Check delimiters, quoting, and row lengths."
        ) from error
    except OSError as error:
        raise CSVLoadError(f"Could not read CSV file: {csv_path}: {error}") from error

    if dataframe.empty:
        raise CSVLoadError(
            f"CSV file has a header but no data rows: {csv_path}. "
            "Provide at least one data row."
        )

    return dataframe


def _validate_csv_structure(csv_path: Path) -> None:
    """Reject duplicate headers and data rows with inconsistent field counts."""
    try:
        with csv_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as csv_file:
            reader = csv.reader(csv_file, strict=True)
            try:
                header = next(reader)
            except StopIteration as error:
                raise CSVLoadError(
                    f"CSV file is empty: {csv_path}. "
                    "Provide a header row and at least one data row."
                ) from error

            duplicates = _duplicate_names(header)
            if duplicates:
                names = ", ".join(repr(name) for name in duplicates)
                raise CSVLoadError(
                    f"CSV file contains duplicate column names: {names}. "
                    "Rename the columns and try again."
                )

            data_row_count = 0
            for row in reader:
                if not row:
                    continue
                data_row_count += 1
                if len(row) < len(header):
                    raise CSVLoadError(
                        f"CSV file has too few fields on data row "
                        f"{reader.line_num}: expected {len(header)}, "
                        f"found {len(row)}."
                    )
                if len(row) > len(header):
                    raise CSVLoadError(
                        f"CSV file has too many fields on data row "
                        f"{reader.line_num}: expected {len(header)}, "
                        f"found {len(row)}."
                    )

            if data_row_count == 0:
                raise CSVLoadError(
                    f"CSV file has a header but no data rows: {csv_path}. "
                    "Provide at least one data row."
                )
    except UnicodeDecodeError as error:
        raise CSVLoadError(
            f"CSV file is not valid UTF-8: {csv_path}. "
            "Save the file as UTF-8 and try again."
        ) from error
    except csv.Error as error:
        raise CSVLoadError(
            f"CSV file is malformed: {csv_path}. "
            "Check delimiters and quoting."
        ) from error
    except OSError as error:
        raise CSVLoadError(f"Could not read CSV file: {csv_path}: {error}") from error


def _duplicate_names(names: list[str]) -> list[str]:
    """Return duplicate header names once, preserving their header order."""
    seen: set[str] = set()
    duplicates: list[str] = []
    for name in names:
        if name in seen and name not in duplicates:
            duplicates.append(name)
        seen.add(name)
    return duplicates
