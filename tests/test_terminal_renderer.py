from dataset_doctor.models import ColumnStatistics, DatasetProfile
from dataset_doctor.renderers.terminal import render_terminal


def test_render_terminal_includes_dataset_summary_and_column_table() -> None:
    profile = DatasetProfile(
        row_count=3,
        column_count=2,
        columns=[
            ColumnStatistics("age", "int64", 0, 0.0, False),
            ColumnStatistics("name", "string", 0, 0.0, False),
        ],
        duplicate_row_count=1,
        constant_columns=[],
    )

    output = render_terminal(profile)

    assert "Rows: 3" in output
    assert "Columns: 2" in output
    assert "Duplicate rows: 1" in output
    assert "Column" in output
    assert "Dtype" in output
    assert "Missing" in output
    assert "Missing %" in output
    assert "Constant" in output
    assert "age" in output and "int64" in output and "0.00%" in output
    assert "name" in output and "string" in output


def test_render_terminal_displays_missing_values() -> None:
    profile = DatasetProfile(
        row_count=4,
        column_count=1,
        columns=[ColumnStatistics("score", "float64", 2, 50.0, False)],
        duplicate_row_count=0,
        constant_columns=[],
    )

    output = render_terminal(profile)

    assert "score" in output
    assert "float64" in output
    assert "2" in output
    assert "50.00%" in output


def test_render_terminal_displays_constant_columns() -> None:
    profile = DatasetProfile(
        row_count=2,
        column_count=2,
        columns=[
            ColumnStatistics("status", "string", 0, 0.0, True),
            ColumnStatistics("value", "int64", 0, 0.0, False),
        ],
        duplicate_row_count=0,
        constant_columns=["status"],
    )

    output = render_terminal(profile)

    assert "status" in output
    assert "string" in output
    assert "yes" in output
    assert "Constant columns: status" in output


def test_render_terminal_preserves_long_column_names() -> None:
    long_name = "column_name_that_is_longer_than_a_typical_terminal_width"
    profile = DatasetProfile(
        row_count=1,
        column_count=1,
        columns=[ColumnStatistics(long_name, "string", 0, 0.0, True)],
        duplicate_row_count=0,
        constant_columns=[long_name],
    )

    output = render_terminal(profile)

    assert long_name in output
    assert "(no columns)" not in output


def test_render_terminal_handles_zero_column_profile() -> None:
    profile = DatasetProfile(
        row_count=0,
        column_count=0,
        columns=[],
        duplicate_row_count=0,
        constant_columns=[],
    )

    output = render_terminal(profile)

    assert "Rows: 0" in output
    assert "Columns: 0" in output
    assert "(no columns)" in output
    assert "Constant columns: none" in output
    assert "Findings" in output
    assert "No findings" in output


def test_render_terminal_displays_findings_and_evidence() -> None:
    from dataset_doctor.models import Finding

    profile = DatasetProfile(
        row_count=2,
        column_count=1,
        columns=[ColumnStatistics("score", "float64", 1, 50.0, False)],
        duplicate_row_count=0,
        constant_columns=[],
        findings=(
            Finding(
                "missing_values",
                "warning",
                "Column 'score' contains 1 missing value.",
                "score",
                {"missing_count": 1, "missing_percentage": 50.0},
            ),
        ),
    )

    output = render_terminal(profile)

    assert "[WARNING] missing_values (column: score)" in output
    assert "Column 'score' contains 1 missing value." in output
    assert "Evidence: missing_count=1; missing_percentage=50.0" in output
