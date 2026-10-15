"""Standalone HTML rendering for dataset profiles."""

from html import escape

from dataset_doctor.models import DatasetProfile, Finding


class HTMLRenderError(ValueError):
    """Raised when a dataset profile cannot be rendered as HTML."""


def render_html(profile: DatasetProfile) -> str:
    """Render a complete, standalone HTML document for a dataset profile."""
    try:
        column_rows = "\n".join(
            _column_row(
                statistics.name,
                statistics.dtype,
                statistics.missing_count,
                statistics.missing_percentage,
                statistics.is_constant,
            )
            for statistics in profile.columns
        )
        if not column_rows:
            column_rows = (
                '<tr><td colspan="5" class="empty-state">No columns</td></tr>'
            )

        findings_markup = _findings_markup(profile)
        constant_columns = ", ".join(profile.constant_columns) or "None"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dataset Doctor Report</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      color: #172033;
      background: #f4f7fb;
    }}
    body {{
      margin: 0;
      padding: 2rem 1rem;
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
    }}
    h1, h2 {{
      color: #102a43;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
      margin: 1.5rem 0;
    }}
    .summary-card, .findings, .table-panel {{
      background: #ffffff;
      border: 1px solid #c9d5e3;
      border-radius: 0.5rem;
      box-shadow: 0 1px 2px rgba(16, 42, 67, 0.08);
    }}
    .summary-card {{
      padding: 1rem;
    }}
    .summary-label {{
      display: block;
      color: #486581;
      font-size: 0.875rem;
    }}
    .summary-value {{
      display: block;
      color: #102a43;
      font-size: 1.5rem;
      font-weight: 700;
      margin-top: 0.25rem;
    }}
    .table-panel {{
      overflow-x: auto;
    }}
    table {{
      border-collapse: collapse;
      min-width: 680px;
      width: 100%;
    }}
    th, td {{
      border-bottom: 1px solid #d9e2ec;
      padding: 0.75rem;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #e9f0f7;
      color: #102a43;
      font-weight: 700;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .findings {{
      padding: 1rem;
      margin-top: 1.5rem;
    }}
    .finding {{
      border-left: 0.3rem solid #486581;
      border-bottom: 1px solid #d9e2ec;
      padding: 0.75rem 0.75rem 0.75rem 1rem;
    }}
    .finding:last-child {{
      border-bottom: 0;
    }}
    .finding.warning {{
      border-left-color: #9c6500;
    }}
    .finding.error {{
      border-left-color: #b42318;
    }}
    .severity {{
      font-weight: 700;
      letter-spacing: 0.03em;
    }}
    .evidence {{
      color: #486581;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      margin-top: 0.35rem;
    }}
    .empty-state {{
      color: #486581;
      text-align: center;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Dataset Doctor Report</h1>
    <section class="summary" aria-label="Dataset summary">
      <div class="summary-card">
        <span class="summary-label">Rows</span>
        <span class="summary-value">{profile.row_count}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Columns</span>
        <span class="summary-value">{profile.column_count}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Duplicate rows</span>
        <span class="summary-value">{profile.duplicate_row_count}</span>
      </div>
    </section>

    <section class="table-panel" aria-labelledby="columns-heading">
      <h2 id="columns-heading">Column statistics</h2>
      <table>
        <thead>
          <tr>
            <th scope="col">Column</th>
            <th scope="col">Dtype</th>
            <th scope="col">Missing</th>
            <th scope="col">Missing %</th>
            <th scope="col">Constant</th>
          </tr>
        </thead>
        <tbody>
{column_rows}
        </tbody>
      </table>
    </section>
    <p><strong>Constant columns:</strong> {escape(constant_columns)}</p>

    <section class="findings" aria-labelledby="findings-heading">
      <h2 id="findings-heading">Findings</h2>
{findings_markup}
    </section>
  </main>
</body>
</html>"""
    except (TypeError, ValueError) as error:
        raise HTMLRenderError(
            "Dataset profile contains values that cannot be rendered as HTML."
        ) from error


def _column_row(
    name: str,
    dtype: str,
    missing_count: int,
    missing_percentage: float,
    is_constant: bool,
) -> str:
    """Render one escaped column-statistics row."""
    values = (
        name,
        dtype,
        str(missing_count),
        f"{missing_percentage:.2f}%",
        "Yes" if is_constant else "No",
    )
    return "          <tr>" + "".join(
        f"<td>{escape(value)}</td>" for value in values
    ) + "</tr>"


def _findings_markup(profile: DatasetProfile) -> str:
    """Render the findings section without recalculating findings."""
    if not profile.findings:
        return '      <p class="empty-state">No findings</p>'

    return "\n".join(_finding_markup(finding) for finding in profile.findings)


def _finding_markup(finding: Finding) -> str:
    """Render one escaped finding."""
    if finding.severity not in {"info", "warning", "error"}:
        raise HTMLRenderError(
            f"Unsupported finding severity: {finding.severity!r}"
        )

    location = (
        f" — column: {escape(finding.column)}" if finding.column is not None else ""
    )
    evidence = ""
    if finding.details:
        details = "; ".join(
            f"{escape(str(key))}={escape(str(value))}"
            for key, value in finding.details.items()
        )
        evidence = f'\n          <div class="evidence">Evidence: {details}</div>'

    heading = (
        f"{finding.severity.upper()} — "
        f"{escape(finding.finding_id)}{location}"
    )
    return f"""      <article class="finding {finding.severity}">
        <div class="severity">{heading}</div>
        <div>{escape(finding.description)}</div>{evidence}
      </article>"""
