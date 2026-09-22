from __future__ import annotations

from pathlib import Path

from .detector import ColumnDetector
from .exporters import CsvExporter
from .repositories import ExcelIndexer, ExcelRepository, HostRepository, LookupError
from .services import HostLookupService


class Application:
    def __init__(
        self,
        excel: Path | None,
        hosts: Path | None,
        output_dir: Path,
    ) -> None:
        self.excel = excel
        self.hosts = hosts
        self.output_dir = output_dir
        self.detector = ColumnDetector()

    def run(self) -> int:
        try:
            repository = (
                ExcelRepository(self.excel)
                if self.excel
                else ExcelRepository.discover(Path.cwd())
            )
            excel_data = repository.load()

            host_repository = HostRepository(self.hosts)
            hosts = host_repository.load(excel_data, self.detector)
            if not hosts:
                raise LookupError("Aucun hostname à rechercher.")

            index, columns = ExcelIndexer(self.detector).build(excel_data)

            for sheet, detected in columns.items():
                print(
                    f"[{sheet}] HOST={detected.hostname!r} "
                    f"IP={detected.ip!r} DNS_NAME={detected.dns_name!r}"
                )

            results = HostLookupService(index).lookup_many(hosts)

            exporter = CsvExporter()
            exporter.export_by_sheet(
                results, index, excel_data.keys(),
                self.output_dir, repository.path.stem
            )
            exporter.export_global(
                results, self.output_dir, repository.path.stem
            )

            ok = sum(r.status == "OK" for r in results)
            conflicts = sum(r.status == "CONFLIT" for r in results)
            missing = sum(r.status == "NON_TROUVE" for r in results)

            print(f"OK={ok} CONFLITS={conflicts} NON_TROUVES={missing}")
            print(f"Résultats: {self.output_dir.resolve()}")
            return 0
        except LookupError as exc:
            print(f"ERREUR: {exc}")
            return 1
