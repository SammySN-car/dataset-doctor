import pandas as pd

from dataset_doctor.models import ColumnStatistics, DatasetProfile
from dataset_doctor.profiler import profile_dataframe


def test_profile_dataframe_reports_numeric_and_text_columns() -> None:
    dataframe = pd.DataFrame(
        {"age": [30, 40], "name": ["Alice", "Bob"]}
    )

    profile = profile_dataframe(dataframe)

    assert profile == DatasetProfile(
        row_count=2,
        column_count=2,
        columns=[
            ColumnStatistics("age", str(dataframe["age"].dtype), 0, 0.0, False),
            ColumnStatistics("name", str(dataframe["name"].dtype), 0, 0.0, False),
        ],
        duplicate_row_count=0,
        constant_columns=[],
    )


def test_profile_dataframe_calculates_missing_counts_and_percentages() -> None:
    dataframe = pd.DataFrame(
        {"age": [30, None, 40, None], "name": ["Alice", "Bob", None, "Dana"]}
    )

    profile = profile_dataframe(dataframe)

    assert profile.columns[0].missing_count == 2
    assert profile.columns[0].missing_percentage == 50.0
    assert profile.columns[1].missing_count == 1
    assert profile.columns[1].missing_percentage == 25.0


def test_profile_dataframe_counts_rows_beyond_first_duplicate() -> None:
    dataframe = pd.DataFrame({"value": [1, 1, 1, 2, 2, 3]})

    profile = profile_dataframe(dataframe)

    assert profile.duplicate_row_count == 3


def test_profile_dataframe_identifies_constant_columns() -> None:
    dataframe = pd.DataFrame(
        {
            "repeated": ["x", "x", None],
            "varying": [1, 2, 1],
        }
    )

    profile = profile_dataframe(dataframe)

    assert profile.constant_columns == ["repeated"]
    assert profile.columns[0].is_constant is True
    assert profile.columns[1].is_constant is False


def test_profile_dataframe_marks_all_missing_column_as_constant() -> None:
    dataframe = pd.DataFrame({"unknown": [None, None]})

    profile = profile_dataframe(dataframe)

    assert profile.constant_columns == ["unknown"]
    assert profile.columns[0].is_constant is True


def test_profile_dataframe_preserves_column_order() -> None:
    dataframe = pd.DataFrame(
        {"third": [1], "first": ["a"], "second": [True]}
    )

    profile = profile_dataframe(dataframe)

    assert [column.name for column in profile.columns] == [
        "third",
        "first",
        "second",
    ]


def test_profile_dataframe_handles_zero_rows() -> None:
    dataframe = pd.DataFrame(
        {
            "number": pd.Series(dtype="int64"),
            "text": pd.Series(dtype="object"),
        }
    )

    profile = profile_dataframe(dataframe)

    assert profile.row_count == 0
    assert profile.column_count == 2
    assert [column.missing_percentage for column in profile.columns] == [
        0.0,
        0.0,
    ]
    assert profile.duplicate_row_count == 0
    assert profile.constant_columns == ["number", "text"]
    assert profile.findings == ()


def test_dataset_profile_findings_default_preserves_existing_construction() -> None:
    profile = DatasetProfile(0, 0, [], 0, [])

    assert profile.findings == ()
