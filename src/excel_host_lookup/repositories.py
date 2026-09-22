from __future__ import annotations

from pathlib import Path

import pandas as pd

from .detector import ColumnDetector
from .models import HostRecord, SheetColumns
from .normalization import Normalizer


class LookupError(Exception):
    """Erreur fonctionnelle."""


class ExcelRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    @classmethod
    def discover(cls, directory: Path) -> ExcelRepository:
        files = sorted(
            p for p in directory.iterdir()
            if p.is_file() and p.suffix.lower() in {".xlsx", ".xls"}
        )
        if not files:
            raise LookupError("Aucun fichier Excel trouvé.")
        return cls(files[0])

    def load(self) -> dict[str, pd.DataFrame]:
        try:
            return pd.read_excel(self.path, sheet_name=None)
        except Exception as exc:
            raise LookupError(f"Impossible de lire {self.path}: {exc}") from exc


class HostRepository:
    def __init__(self, path: Path | None) -> None:
        self.path = path

    def load(
        self,
        excel_data: dict[str, pd.DataFrame],
        detector: ColumnDetector,
    ) -> list[str]:
        return self._from_file() if self.path else self._from_excel(
            excel_data, detector
        )

    def _from_file(self) -> list[str]:
        assert self.path is not None
        if not self.path.is_file():
            raise LookupError(f"Fichier hosts introuvable: {self.path}")
        hosts: list[str] = []
        seen: set[str] = set()
        with self.path.open("r", encoding="utf-8-sig", errors="replace") as fh:
            for line in fh:
                for token in line.split("#", 1)[0].split():
                    host = Normalizer.hostname(token)
                    if host and host not in seen:
                        seen.add(host)
                        hosts.append(host)
        return hosts

    @staticmethod
    def _from_excel(
        excel_data: dict[str, pd.DataFrame],
        detector: ColumnDetector,
    ) -> list[str]:
        hosts: list[str] = []
        seen: set[str] = set()
        for df in excel_data.values():
            if df.empty:
                continue
            columns = detector.detect(df)
            if not columns.hostname:
                continue
            for value in df[columns.hostname]:
                host = Normalizer.hostname(value)
                if host and host not in seen:
                    seen.add(host)
                    hosts.append(host)
        return hosts


class ExcelIndexer:
    def __init__(self, detector: ColumnDetector) -> None:
        self.detector = detector

    def build(
        self,
        excel_data: dict[str, pd.DataFrame],
    ) -> tuple[dict[str, list[HostRecord]], dict[str, SheetColumns]]:
        index: dict[str, list[HostRecord]] = {}
        columns_by_sheet: dict[str, SheetColumns] = {}

        for sheet, df in excel_data.items():
            if df.empty:
                continue
            columns = self.detector.detect(df)
            columns_by_sheet[sheet] = columns
            if not columns.hostname:
                continue

            host_pos = df.columns.get_loc(columns.hostname)
            ip_pos = df.columns.get_loc(columns.ip) if columns.ip else None
            dns_pos = (
                df.columns.get_loc(columns.dns_name)
                if columns.dns_name else None
            )

            for row_number, row in enumerate(
                df.itertuples(index=False, name=None), start=2
            ):
                host = Normalizer.hostname(row[host_pos])
                if not host:
                    continue
                ip = Normalizer.ipv4(row[ip_pos]) if ip_pos is not None else ""
                fqdn = Normalizer.fqdn(row[dns_pos]) if dns_pos is not None else ""
                if not ip and not fqdn:
                    continue
                index.setdefault(host, []).append(
                    HostRecord(host, ip, fqdn, sheet, row_number)
                )

        return index, columns_by_sheet
