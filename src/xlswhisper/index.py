from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .detector import ColumnDetector
from .models import HostRecord
from .normalization import fqdn, hostname, ipv4
from .xlsx_reader import XlsxReader


class InventoryIndex:
    def __init__(self) -> None:
        self._by_host: dict[str, list[HostRecord]] = defaultdict(list)
        self._by_fqdn: dict[str, list[HostRecord]] = defaultdict(list)

    def add(self, record: HostRecord) -> None:
        key = hostname(record.hostname)
        if not key:
            return
        self._by_host[key].append(record)
        if record.fqdn:
            self._by_fqdn[fqdn(record.fqdn)].append(record)

    def find(self, value: str) -> list[HostRecord]:
        key = hostname(value)
        if not key:
            return []
        records = list(self._by_host.get(key, []))
        for record in self._by_fqdn.get(key, []):
            if record not in records:
                records.append(record)
        return records

    def hosts(self) -> list[str]:
        return sorted(self._by_host)


class InventoryLoader:
    def __init__(self, reader: XlsxReader | None = None) -> None:
        self.reader = reader or XlsxReader()
        self.detector = ColumnDetector()

    def load(self, path: Path) -> InventoryIndex:
        index = InventoryIndex()
        for sheet_name, rows in self.reader.iter_sheets(path):
            try:
                headers = next(rows)
            except StopIteration:
                continue
            columns = self.detector.detect(headers)
            if columns.host is None and columns.dns is None:
                continue

            for row_number, row in enumerate(rows, start=2):
                host = self._value(row, columns.host)
                dns = self._value(row, columns.dns)
                host_key = hostname(host) or hostname(dns)
                if not host_key:
                    continue
                index.add(
                    HostRecord(
                        hostname=host_key,
                        ip=ipv4(self._value(row, columns.ip)),
                        fqdn=fqdn(dns) if dns else None,
                        sheet=sheet_name,
                        row=row_number,
                    )
                )
        return index

    @staticmethod
    def _value(row: list[str], index: int | None) -> str:
        if index is None or index >= len(row):
            return ""
        return row[index].strip()
