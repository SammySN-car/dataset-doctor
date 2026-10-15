"""Pure data-quality finding detection."""

import pandas as pd

from dataset_doctor.models import DatasetProfile, Finding


def detect_findings(
    dataframe: pd.DataFrame, profile: DatasetProfile
) -> tuple[Finding, ...]:
    """Detect data-quality findings using a DataFrame and its profile."""
    if profile.row_count == 0:
        return ()

    findings: list[Finding] = []
    for statistics in profile.columns:
        if statistics.missing_count == profile.row_count:
            findings.append(
                Finding(
                    finding_id="all_missing_column",
                    severity="error",
                    description=(
                        f"Column '{statistics.name}' contains no non-missing "
                        "values."
                    ),
                    column=statistics.name,
                    details={
                        "missing_count": statistics.missing_count,
                        "missing_percentage": statistics.missing_percentage,
                    },
                )
            )
            continue

        if statistics.missing_count > 0:
            findings.append(
                Finding(
                    finding_id="missing_values",
                    severity="warning",
                    description=(
                        f"Column '{statistics.name}' contains "
                        f"{statistics.missing_count} missing values."
                    ),
                    column=statistics.name,
                    details={
                        "missing_count": statistics.missing_count,
                        "missing_percentage": statistics.missing_percentage,
                    },
                )
            )

        if statistics.is_constant:
            findings.append(
                Finding(
                    finding_id="constant_column",
                    severity="warning",
                    description=(
                        f"Column '{statistics.name}' has only one distinct "
                        "non-missing value."
                    ),
                    column=statistics.name,
                    details={"distinct_non_missing_values": 1},
                )
            )

    if profile.duplicate_row_count > 0:
        findings.append(
            Finding(
                finding_id="duplicate_rows",
                severity="warning",
                description=(
                    "Dataset contains duplicate rows beyond the first "
                    "occurrence."
                ),
                details={"duplicate_row_count": profile.duplicate_row_count},
            )
        )

    return tuple(findings)
