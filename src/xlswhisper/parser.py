from pathlib import Path

from .detector import ColumnDetector
from .limits import Limits
from .models import SearchHost
from .normalization import parse_host_list
from .xlsx_reader import XlsxReader


class SearchInputParser:
    def __init__(self, limits: Limits | None = None) -> None:
        self.limits = limits or Limits()
        self.reader = XlsxReader(self.limits)
        self.detector = ColumnDetector()

    def parse_string(self, value: str) -> list[SearchHost]:
        hosts = [SearchHost(hostname=h) for h in parse_host_list(value)]
        self._check_count(hosts)
        return hosts

    def parse_txt(self, path: Path) -> list[SearchHost]:
        path = path.resolve(strict=True)
        if path.suffix.lower() != ".txt":
            raise ValueError("Le fichier direct doit être un .txt.")
        if path.stat().st_size > self.limits.max_member_bytes:
            raise ValueError("Fichier TXT trop volumineux.")
        return self.parse_string(path.read_text(encoding="utf-8-sig"))

    def parse_excel(self, path: Path) -> list[SearchHost]:
        result: list[SearchHost] = []
        for sheet_name, rows in self.reader.iter_sheets(path):
            try:
                headers = next(rows)
            except StopIteration:
                continue
            columns = self.detector.detect(headers)
            column = columns.host if columns.host is not None else columns.dns
            if column is None:
                continue

            for row_number, row in enumerate(rows, start=2):
                if column >= len(row):
                    continue
                for host in parse_host_list(row[column]):
                    result.append(
                        SearchHost(host, sheet_name, row_number)
                    )
                    self._check_count(result)
        return result

    def _check_count(self, hosts: list[SearchHost]) -> None:
        if len(hosts) > self.limits.max_search_hosts:
            raise ValueError("Nombre de hosts recherchés dépassant la limite.")
