from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .exporter import CsvExporter
from .index import InventoryLoader
from .limits import Limits
from .lookup import HostLookupService
from .models import SearchHost
from .parser import SearchInputParser
from .xlsx_reader import XlsxError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="excel-host-lookup",
        description="Recherche robuste de hosts dans un inventaire XLSX.",
    )
    parser.add_argument("inventory", type=Path)
    parser.add_argument(
        "hosts", nargs="?",
        help="TXT ou liste séparée par , ; | ou espace.",
    )
    parser.add_argument("--hosts-excel", type=Path)
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("results"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.hosts and args.hosts_excel:
        parser.error("hosts et --hosts-excel sont mutuellement exclusifs.")

    try:
        inventory = args.inventory.resolve(strict=True)
        if inventory.suffix.lower() != ".xlsx":
            parser.error("L'inventaire doit être un fichier .xlsx.")

        limits = Limits()
        parser_input = SearchInputParser(limits)
        index = InventoryLoader().load(inventory)

        if args.hosts_excel:
            hosts = parser_input.parse_excel(
                args.hosts_excel.resolve(strict=True)
            )
        elif args.hosts:
            candidate = Path(args.hosts)
            if candidate.is_file():
                hosts = parser_input.parse_txt(candidate)
            else:
                hosts = parser_input.parse_string(args.hosts)
        else:
            hosts = [SearchHost(host) for host in index.hosts()]

        results = HostLookupService(index, limits).lookup(hosts)
        CsvExporter().export(results, args.output_dir)

        print(f"Inventaire       : {inventory}")
        print(f"Hosts recherchés : {len(hosts)}")
        print(f"Résultats        : {len(results)}")
        print(f"Sortie           : {args.output_dir.resolve()}")
        return 0

    except (OSError, ValueError, XlsxError) as exc:
        print(f"ERREUR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
