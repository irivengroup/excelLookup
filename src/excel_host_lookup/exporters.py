from __future__ import annotations

import re
from pathlib import Path
from collections.abc import Iterable

import pandas as pd

from .models import HostRecord, LookupResult


class CsvExporter:
    COLUMNS = [
        "Hostname",
        "IP_Trouvee",
        "FQDN_Trouve",
        "Statut",
        "Conflit_IP",
        "Conflit_FQDN",
        "Sources",
    ]

    @staticmethod
    def sheet_filename(sheet: str) -> str:
        name = re.sub(r"\s+", "", sheet)
        return re.sub(r'[<>:"/\\|?*]', "_", name) or "Sheet"

    def export_by_sheet(
        self,
        results: list[LookupResult],
        index: dict[str, list[HostRecord]],
        sheets: Iterable[str],
        output_dir: Path,
        base_name: str,
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        by_host = {result.hostname: result for result in results}

        for sheet in sheets:
            hosts = {
                record.hostname
                for records in index.values()
                for record in records
                if record.sheet == sheet
            }
            rows = [by_host[h].as_dict() for h in by_host if h in hosts]
            path = output_dir / f"{base_name}_{self.sheet_filename(sheet)}.csv"
            pd.DataFrame(rows, columns=self.COLUMNS).to_csv(
                path, index=False, encoding="utf-8-sig"
            )

    def export_global(
        self,
        results: list[LookupResult],
        output_dir: Path,
        base_name: str,
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{base_name}_RESULTATS.csv"
        pd.DataFrame([r.as_dict() for r in results], columns=self.COLUMNS).to_csv(
            path, index=False, encoding="utf-8-sig"
        )
