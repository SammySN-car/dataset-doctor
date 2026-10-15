from pathlib import Path

import pandas as pd
import pytest

from dataset_doctor.loader import CSVLoadError, load_csv


def test_load_csv_returns_dataframe_with_original_column_order(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("name,score,group\nAlice,10,A\nBob,20,B\n", encoding="utf-8")

    result = load_csv(path)

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["name", "score", "group"]
    assert result.to_dict(orient="records") == [
        {"name": "Alice", "score": 10, "group": "A"},
        {"name": "Bob", "score": 20, "group": "B"},
    ]


def test_load_csv_preserves_quoted_commas(tmp_path: Path) -> None:
    path = tmp_path / "quoted.csv"
    path.write_text('name,description\nAlice,"Senior, analyst"\n', encoding="utf-8")

    result = load_csv(path)

    assert result.iloc[0]["description"] == "Senior, analyst"


def test_load_csv_preserves_quoted_embedded_newlines(tmp_path: Path) -> None:
    path = tmp_path / "embedded-newline.csv"
    path.write_text(
        'name,notes\nAlice,"line one\nline two"\n',
        encoding="utf-8",
    )

    result = load_csv(path)

    assert result.iloc[0]["notes"].splitlines() == ["line one", "line two"]


def test_load_csv_supports_utf8_bom(tmp_path: Path) -> None:
    path = tmp_path / "bom.csv"
    path.write_bytes(b"\xef\xbb\xbfname\nAlice\n")

    result = load_csv(path)

    assert list(result.columns) == ["name"]
    assert result.iloc[0]["name"] == "Alice"


def test_load_csv_rejects_duplicate_column_names(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-columns.csv"
    path.write_text("name,name\nAlice,Smith\n", encoding="utf-8")

    with pytest.raises(CSVLoadError, match="duplicate column names.*name"):
        load_csv(path)


def test_load_csv_rejects_repeated_empty_column_names(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-empty-columns.csv"
    path.write_text(",\nAlice,Smith\n", encoding="utf-8")

    with pytest.raises(CSVLoadError, match="duplicate column names"):
        load_csv(path)


def test_load_csv_rejects_short_data_rows(tmp_path: Path) -> None:
    path = tmp_path / "short-row.csv"
    path.write_text("name,score,group\nAlice,10\n", encoding="utf-8")

    with pytest.raises(CSVLoadError, match="too few fields"):
        load_csv(path)


def test_load_csv_rejects_extra_fields_in_data_rows(tmp_path: Path) -> None:
    path = tmp_path / "extra-fields.csv"
    path.write_text("name,score\nAlice,10,unexpected\n", encoding="utf-8")

    with pytest.raises(CSVLoadError, match="too many fields"):
        load_csv(path)


def test_load_csv_rejects_nonexistent_path(tmp_path: Path) -> None:
    path = tmp_path / "missing.csv"

    with pytest.raises(CSVLoadError, match="does not exist"):
        load_csv(path)


def test_load_csv_rejects_directory_path(tmp_path: Path) -> None:
    with pytest.raises(CSVLoadError, match="directory"):
        load_csv(tmp_path)


def test_load_csv_rejects_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(CSVLoadError, match="empty"):
        load_csv(path)


def test_load_csv_rejects_header_only_file(tmp_path: Path) -> None:
    path = tmp_path / "header-only.csv"
    path.write_text("name,score\n", encoding="utf-8")

    with pytest.raises(CSVLoadError, match="no data rows"):
        load_csv(path)


def test_load_csv_rejects_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "invalid-encoding.csv"
    path.write_bytes(b"name\n\xff\n")

    with pytest.raises(CSVLoadError, match="valid UTF-8"):
        load_csv(path)


def test_load_csv_rejects_malformed_input(tmp_path: Path) -> None:
    path = tmp_path / "malformed.csv"
    path.write_text('name,description\nAlice,"unterminated\n', encoding="utf-8")

    with pytest.raises(CSVLoadError, match="malformed"):
        load_csv(path)
