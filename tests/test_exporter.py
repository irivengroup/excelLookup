from pathlib import Path

from excel_host_lookup.exporters import CsvExporter
from excel_host_lookup.models import LookupResult


def test_sheet_spaces_are_removed(tmp_path: Path) -> None:
    exporter = CsvExporter()
    assert exporter.sheet_filename("Production Servers") == "ProductionServers"


def test_global_export(tmp_path: Path) -> None:
    result = LookupResult(
        hostname="srv01",
        ips={"10.0.0.1"},
        fqdns={"srv01.example.com"},
    )

    exporter = CsvExporter()
    exporter.export_global([result], tmp_path, "inventory")

    assert (tmp_path / "inventory_RESULTATS.csv").is_file()
