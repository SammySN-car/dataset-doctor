"""Command-line interface for Dataset Doctor."""

import argparse
import sys
from collections.abc import Sequence

from dataset_doctor.loader import CSVLoadError, load_csv
from dataset_doctor.profiler import profile_dataframe
from dataset_doctor.renderers.html import HTMLRenderError, render_html
from dataset_doctor.renderers.json import JSONRenderError, render_json
from dataset_doctor.renderers.terminal import render_terminal


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Dataset Doctor command-line interface."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        dataframe = load_csv(args.path)
    except CSVLoadError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    profile = profile_dataframe(dataframe)
    try:
        report = (
            render_json(profile)
            if args.format == "json"
            else render_html(profile)
            if args.format == "html"
            else render_terminal(profile)
        )
    except (HTMLRenderError, JSONRenderError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(report)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="dataset-doctor",
        description="Diagnose CSV dataset quality and ML readiness.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    profile_parser = subparsers.add_parser(
        "profile",
        help="Profile a CSV dataset.",
        description="Load and profile a CSV dataset.",
    )
    profile_parser.add_argument("path", help="Path to the CSV file.")
    profile_parser.add_argument(
        "--format",
        choices=("terminal", "json", "html"),
        default="terminal",
        help="Report format (default: terminal).",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
