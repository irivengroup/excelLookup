from __future__ import annotations

import argparse
from pathlib import Path

from .app import Application


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lookup local Hostname -> IPv4/FQDN depuis Excel."
    )
    parser.add_argument("excel", nargs="?", type=Path)
    parser.add_argument("hosts", nargs="?", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("csv_results"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return Application(
        excel=args.excel,
        hosts=args.hosts,
        output_dir=args.output_dir,
    ).run()
