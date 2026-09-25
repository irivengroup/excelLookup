import csv
import re
from pathlib import Path
from typing import ClassVar

from .models import LookupResult

INVALID_FILENAME = re.compile(r'[<>:"/\\\\|?*\x00-\x1f]')
MAX_FILENAME = 180


class CsvExporter:
    HEADER: ClassVar[list[str]] = [
        "Hostname",
        "IP_Trouvee",
        "FQDN_Trouve",
        "Statut",
        "Conflit_IP",
        "Conflit_FQDN",
        "Sources",
        "Feuille_Recherche",
        "Ligne_Recherche",
    ]

    def export(self, results: list[LookupResult], output_dir: Path) -> None:
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        grouped: dict[str, list[LookupResult]] = {}
        for result in results:
            grouped.setdefault(result.search.sheet or "LISTE", []).append(result)

        used: set[str] = set()
        for sheet, items in grouped.items():
            name = self._unique(self._safe(sheet), used)
            self._write(items, output_dir / f"{name}.csv")

        self._write(results, output_dir / "RESULTATS.csv")
        self._write(
            (r for r in results if r.sources),
            output_dir / "SOURCES.csv",
        )

    def _write(self, results, path: Path) -> None:
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(
                handle, delimiter=";", quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n"
            )
            writer.writerow(self.HEADER)
            for result in results:
                writer.writerow([
                    result.search.hostname,
                    result.ip or "",
                    result.fqdn or "",
                    result.status,
                    "OUI" if result.conflict_ip else "NON",
                    "OUI" if result.conflict_fqdn else "NON",
                    " | ".join(result.sources),
                    result.search.sheet or "",
                    result.search.row or "",
                ])

    @staticmethod
    def _safe(value: str) -> str:
        value = INVALID_FILENAME.sub("_", value.replace(" ", ""))
        value = value.strip(". ")
        return value[:MAX_FILENAME] or "LISTE"

    @staticmethod
    def _unique(name: str, used: set[str]) -> str:
        candidate = name
        counter = 2
        while candidate.lower() in {x.lower() for x in used}:
            suffix = f"_{counter}"
            candidate = f"{name[:MAX_FILENAME-len(suffix)]}{suffix}"
            counter += 1
        used.add(candidate)
        return candidate
