"""Human-readable terminal rendering for dataset profiles."""

from dataset_doctor.models import DatasetProfile


def render_terminal(profile: DatasetProfile) -> str:
    """Render a dataset profile as a human-readable ASCII report."""
    lines = [
        "Dataset Profile",
        "===============",
        f"Rows: {profile.row_count}",
        f"Columns: {profile.column_count}",
        f"Duplicate rows: {profile.duplicate_row_count}",
        "",
        "Column statistics",
        "------------------",
    ]

    headers = ("Column", "Dtype", "Missing", "Missing %", "Constant")
    rows = [
        (
            statistics.name,
            statistics.dtype,
            str(statistics.missing_count),
            f"{statistics.missing_percentage:.2f}%",
            "yes" if statistics.is_constant else "no",
        )
        for statistics in profile.columns
    ]
    widths = [
        max([len(headers[index])] + [len(row[index]) for row in rows])
        for index in range(len(headers))
    ]

    lines.append(_format_table_row(headers, widths))
    lines.append(_format_table_separator(widths))
    if rows:
        lines.extend(_format_table_row(row, widths) for row in rows)
    else:
        lines.append("(no columns)")

    constant_columns = ", ".join(profile.constant_columns) or "none"
    lines.extend(
        [
            "",
            f"Constant columns: {constant_columns}",
            "",
            "Findings",
            "--------",
        ]
    )
    if profile.findings:
        for finding in profile.findings:
            location = f" (column: {finding.column})" if finding.column else ""
            lines.append(
                f"[{finding.severity.upper()}] {finding.finding_id}{location}"
            )
            lines.append(f"  {finding.description}")
            if finding.details:
                details = "; ".join(
                    f"{key}={value}" for key, value in finding.details.items()
                )
                lines.append(f"  Evidence: {details}")
    else:
        lines.append("No findings")

    return "\n".join(lines)


def _format_table_row(values: tuple[str, ...], widths: list[int]) -> str:
    """Format one row using the supplied column widths."""
    return " | ".join(value.ljust(width) for value, width in zip(values, widths))


def _format_table_separator(widths: list[int]) -> str:
    """Format the separator below the table header."""
    return "-+-".join("-" * width for width in widths)
