"""Typed data structures for dataset profiles."""

from dataclasses import dataclass, field
from typing import Literal

FindingSeverity = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class ColumnStatistics:
    """Statistics for one dataset column."""

    name: str
    dtype: str
    missing_count: int
    missing_percentage: float
    is_constant: bool


@dataclass(frozen=True)
class Finding:
    """A data-quality issue detected in a dataset."""

    finding_id: str
    severity: FindingSeverity
    description: str
    column: str | None = None
    details: dict[str, int | float] = field(default_factory=dict)


@dataclass(frozen=True)
class DatasetProfile:
    """Summary statistics for a dataset."""

    row_count: int
    column_count: int
    columns: list[ColumnStatistics]
    duplicate_row_count: int
    constant_columns: list[str]
    findings: tuple[Finding, ...] = ()
