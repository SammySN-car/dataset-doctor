from dataset_doctor.models import ColumnStatistics, DatasetProfile, Finding
from dataset_doctor.renderers.html import render_html


def test_render_html_is_complete_and_contains_profile_data() -> None:
    profile = DatasetProfile(
        row_count=3,
        column_count=1,
        columns=[ColumnStatistics("score", "float64", 1, 33.333, False)],
        duplicate_row_count=1,
        constant_columns=[],
        findings=(
            Finding(
                "missing_values",
                "warning",
                "Column 'score' contains 1 missing value.",
                "score",
                {"missing_count": 1, "missing_percentage": 33.333},
            ),
        ),
    )

    output = render_html(profile)

    assert output.startswith("<!DOCTYPE html>")
    assert '<html lang="en">' in output
    assert '<meta name="viewport"' in output
    assert "<title>Dataset Doctor Report</title>" in output
    assert "Rows" in output and ">3<" in output
    assert "Columns" in output and ">1<" in output
    assert "Duplicate rows" in output and ">1<" in output
    assert "score" in output
    assert "33.33%" in output
    assert "WARNING" in output
    assert "missing_values" in output
    assert "missing_count=1" in output


def test_render_html_handles_empty_findings() -> None:
    output = render_html(DatasetProfile(0, 0, [], 0, []))

    assert "No findings" in output
    assert "No columns" in output


def test_render_html_escapes_untrusted_text() -> None:
    profile = DatasetProfile(
        row_count=1,
        column_count=1,
        columns=[
            ColumnStatistics(
                '<script>alert("column")</script>',
                "object",
                0,
                0.0,
                False,
            )
        ],
        duplicate_row_count=0,
        constant_columns=['<script>alert("constant")</script>'],
        findings=(
            Finding(
                "unsafe",
                "warning",
                '<img src=x onerror="alert(1)">',
                '<script>alert("finding-column")</script>',
                {"<b>evidence</b>": 1},
            ),
        ),
    )

    output = render_html(profile)

    assert "<script>" not in output
    assert "<img" not in output
    assert "&lt;script&gt;alert(&quot;column&quot;)&lt;/script&gt;" in output
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in output
    assert "&lt;b&gt;evidence&lt;/b&gt;=1" in output


def test_render_html_is_deterministic() -> None:
    profile = DatasetProfile(
        1,
        1,
        [ColumnStatistics("value", "int64", 0, 0.0, True)],
        0,
        ["value"],
    )

    assert render_html(profile) == render_html(profile)
