import json

import pytest

from dataset_doctor.models import ColumnStatistics, DatasetProfile, Finding
from dataset_doctor.renderers.json import JSONRenderError, render_json


def test_render_json_contains_complete_profile_and_findings() -> None:
    profile = DatasetProfile(
        row_count=2,
        column_count=1,
        columns=[ColumnStatistics("score", "float64", 1, 50.0, False)],
        duplicate_row_count=1,
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

    document = json.loads(render_json(profile))

    assert document["row_count"] == 2
    assert document["column_count"] == 1
    assert document["columns"] == [
        {
            "name": "score",
            "dtype": "float64",
            "missing_count": 1,
            "missing_percentage": 50.0,
            "is_constant": False,
        }
    ]
    assert document["duplicate_row_count"] == 1
    assert document["constant_columns"] == []
    assert document["findings"][0] == {
        "finding_id": "missing_values",
        "severity": "warning",
        "description": "Column 'score' contains 1 missing value.",
        "column": "score",
        "details": {"missing_count": 1, "missing_percentage": 50.0},
    }


def test_render_json_is_deterministic_and_indented() -> None:
    profile = DatasetProfile(0, 0, [], 0, [])

    first = render_json(profile)
    second = render_json(profile)

    assert first == second
    assert "\n  " in first


def test_render_json_handles_empty_findings() -> None:
    document = json.loads(render_json(DatasetProfile(0, 0, [], 0, [])))

    assert document["findings"] == []


def test_render_json_rejects_non_json_numeric_values() -> None:
    profile = DatasetProfile(
        1,
        1,
        [ColumnStatistics("value", "float64", 0, 0.0, False)],
        0,
        [],
        (Finding("test", "info", "invalid", details={"value": float("nan")}),),
    )

    with pytest.raises(JSONRenderError, match="standard JSON"):
        render_json(profile)
