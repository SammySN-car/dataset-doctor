"""JSON rendering for dataset profiles."""

import json
from typing import Any

from dataset_doctor.models import DatasetProfile


class JSONRenderError(ValueError):
    """Raised when a dataset profile cannot be represented as valid JSON."""


def render_json(profile: DatasetProfile) -> str:
    """Render a complete dataset profile as deterministic, readable JSON."""
    document: dict[str, Any] = {
        "row_count": profile.row_count,
        "column_count": profile.column_count,
        "columns": [
            {
                "name": statistics.name,
                "dtype": statistics.dtype,
                "missing_count": statistics.missing_count,
                "missing_percentage": statistics.missing_percentage,
                "is_constant": statistics.is_constant,
            }
            for statistics in profile.columns
        ],
        "duplicate_row_count": profile.duplicate_row_count,
        "constant_columns": list(profile.constant_columns),
        "findings": [
            {
                "finding_id": finding.finding_id,
                "severity": finding.severity,
                "description": finding.description,
                "column": finding.column,
                "details": dict(finding.details),
            }
            for finding in profile.findings
        ],
    }

    try:
        return json.dumps(document, indent=2, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise JSONRenderError(
            "Dataset profile contains values that cannot be represented as "
            "standard JSON."
        ) from error
