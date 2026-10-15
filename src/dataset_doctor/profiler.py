"""Dataset profiling independent of input/output concerns."""

from dataclasses import replace

import pandas as pd

from dataset_doctor.findings import detect_findings
from dataset_doctor.models import ColumnStatistics, DatasetProfile


def profile_dataframe(dataframe: pd.DataFrame) -> DatasetProfile:
    """Return deterministic structural and quality statistics for a DataFrame."""
    row_count = len(dataframe)
    column_statistics: list[ColumnStatistics] = []

    for name in dataframe.columns:
        column = dataframe[name]
        missing_count = int(column.isna().sum())
        missing_percentage = (
            missing_count / row_count * 100 if row_count else 0.0
        )
        is_constant = column.dropna().nunique() <= 1

        column_statistics.append(
            ColumnStatistics(
                name=str(name),
                dtype=str(column.dtype),
                missing_count=missing_count,
                missing_percentage=missing_percentage,
                is_constant=is_constant,
            )
        )

    constant_columns = [
        statistics.name
        for statistics in column_statistics
        if statistics.is_constant
    ]

    profile = DatasetProfile(
        row_count=row_count,
        column_count=len(dataframe.columns),
        columns=column_statistics,
        duplicate_row_count=int(dataframe.duplicated().sum()),
        constant_columns=constant_columns,
    )
    return replace(profile, findings=detect_findings(dataframe, profile))
