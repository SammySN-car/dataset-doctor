import json
from pathlib import Path

import pytest

from dataset_doctor.cli import main


def test_profile_command_prints_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "data.csv"
    path.write_text("name,score\nAlice,10\nBob,20\n", encoding="utf-8")

    exit_code = main(["profile", str(path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dataset Profile" in captured.out
    assert "Rows: 2" in captured.out
    assert captured.err == ""


def test_profile_command_succeeds_when_findings_exist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "data.csv"
    path.write_text("status\nactive\nactive\n", encoding="utf-8")

    exit_code = main(["profile", str(path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[WARNING] constant_column" in captured.out
    assert captured.err == ""


def test_profile_command_selects_json_format(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "data.csv"
    path.write_text("status\nactive\nactive\n", encoding="utf-8")

    exit_code = main(["profile", str(path), "--format", "json"])

    captured = capsys.readouterr()
    document = json.loads(captured.out)
    assert exit_code == 0
    assert document["row_count"] == 2
    assert document["duplicate_row_count"] == 1
    assert document["findings"]
    assert captured.err == ""


def test_profile_command_selects_html_format(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "data.csv"
    path.write_text("status\nactive\nactive\n", encoding="utf-8")

    exit_code = main(["profile", str(path), "--format", "html"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.startswith("<!DOCTYPE html>")
    assert "constant_column" in captured.out
    assert captured.err == ""


def test_profile_command_handles_missing_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "missing.csv"

    exit_code = main(["profile", str(path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: CSV file does not exist" in captured.err
    assert "Traceback" not in captured.err


def test_profile_command_handles_invalid_input(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "malformed.csv"
    path.write_text('name,description\nAlice,"unterminated\n', encoding="utf-8")

    exit_code = main(["profile", str(path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: CSV file is malformed" in captured.err
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    "filename, contents, message",
    [
        (
            "duplicate.csv",
            "name,name\nAlice,Smith\n",
            "duplicate column names",
        ),
        (
            "short.csv",
            "name,score\nAlice\n",
            "too few fields",
        ),
        (
            "extra.csv",
            "name,score\nAlice,10,unexpected\n",
            "too many fields",
        ),
    ],
)
def test_profile_command_handles_structural_input_errors(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    filename: str,
    contents: str,
    message: str,
) -> None:
    path = tmp_path / filename
    path.write_text(contents, encoding="utf-8")

    exit_code = main(["profile", str(path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: " in captured.err
    assert message in captured.err
    assert captured.out == ""
    assert "Traceback" not in captured.err


def test_main_help_output(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exception:
        main(["--help"])

    captured = capsys.readouterr()
    assert exception.value.code == 0
    assert "usage: dataset-doctor" in captured.out
    assert "profile" in captured.out


def test_profile_help_output(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exception:
        main(["profile", "--help"])

    captured = capsys.readouterr()
    assert exception.value.code == 0
    assert "usage: dataset-doctor profile" in captured.out
    assert "Path to the CSV file." in captured.out
