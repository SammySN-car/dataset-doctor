import pandas as pd

from dataset_doctor.models import Finding
from dataset_doctor.profiler import profile_dataframe


def test_detects_partial_missing_values_with_numeric_evidence() -> None:
    dataframe = pd.DataFrame(
        {"score": [10, None, 30, None], "name": ["A", "B", "C", "D"]}
    )
    profile = profile_dataframe(dataframe)

    missing = [
        finding
        for finding in profile.findings
        if finding.finding_id == "missing_values"
    ]

    assert missing == [
        Finding(
            "missing_values",
            "warning",
            "Column 'score' contains 2 missing values.",
            "score",
            {"missing_count": 2, "missing_percentage": 50.0},
        )
    ]


def test_detects_all_missing_column_without_constant_redundancy() -> None:
    dataframe = pd.DataFrame({"empty": [None, None], "value": [1, 2]})
    profile = profile_dataframe(dataframe)

    findings = [finding for finding in profile.findings if finding.column == "empty"]

    assert [finding.finding_id for finding in findings] == ["all_missing_column"]
    assert findings[0].severity == "error"
    assert findings[0].details == {"missing_count": 2, "missing_percentage": 100.0}


def test_detects_partially_missing_constant_column_with_two_findings() -> None:
    dataframe = pd.DataFrame(
        {"status": ["active", None, "active"], "id": [1, 2, 3]}
    )
    profile = profile_dataframe(dataframe)

    assert [finding.finding_id for finding in profile.findings] == [
        "missing_values",
        "constant_column",
    ]


def test_detects_duplicate_rows_beyond_first_occurrences() -> None:
    dataframe = pd.DataFrame({"id": [1, 1, 1], "value": ["a", "a", "a"]})
    profile = profile_dataframe(dataframe)

    assert profile.findings[-1] == Finding(
        "duplicate_rows",
        "warning",
        "Dataset contains duplicate rows beyond the first occurrence.",
        None,
        {"duplicate_row_count": 2},
    )


def test_duplicate_rows_with_missing_values_are_detected() -> None:
    dataframe = pd.DataFrame({"id": [1, 1], "value": [None, None]})
    profile = profile_dataframe(dataframe)

    duplicate_findings = [
        finding
        for finding in profile.findings
        if finding.finding_id == "duplicate_rows"
    ]
    assert len(duplicate_findings) == 1
    assert duplicate_findings[0].details["duplicate_row_count"] == 1


def test_empty_and_zero_column_dataframes_have_no_findings() -> None:
    empty_rows = pd.DataFrame({"value": pd.Series(dtype="object")})
    zero_columns = pd.DataFrame(index=[0, 1])

    assert profile_dataframe(empty_rows).findings == ()
    assert profile_dataframe(zero_columns).findings == ()


def test_findings_are_deterministic_and_preserve_column_order() -> None:
    dataframe = pd.DataFrame(
        {
            "second": [None, "x"],
            "first": ["same", "same"],
            "third": [1, 1],
            "row": [1, 2],
        }
    )
    profile = profile_dataframe(dataframe)

    assert [(finding.finding_id, finding.column) for finding in profile.findings] == [
        ("missing_values", "second"),
        ("constant_column", "second"),
        ("constant_column", "first"),
        ("constant_column", "third"),
    ]
