from __future__ import annotations

import re
from collections.abc import Callable

import pandas as pd

from .models import SheetColumns
from .normalization import Normalizer


class ColumnDetector:
    HOST = re.compile(
        r"(hostname|host|machine|nom.*machine|server|serveur|nom|"
        r"client|ordinateur|device|equipement|équipement)",
        re.I,
    )
    IP = re.compile(r"(^ip$|ip.*address|adresse.*ip|ipv4)", re.I)
    DNS = re.compile(
        r"(^dns[\s_-]*name$|dns.*name|fqdn|fully.*qualified.*domain)",
        re.I,
    )

    def detect(self, df: pd.DataFrame) -> SheetColumns:
        host = self._header(df, self.HOST)
        excluded = {host} if host else set()
        ip = self._header(df, self.IP, excluded) or self._content(
            df, excluded, Normalizer.ipv4
        )
        if ip:
            excluded.add(ip)
        dns = self._header(df, self.DNS, excluded) or self._content(
            df,
            excluded,
            lambda value: "." in Normalizer.fqdn(value),
        )
        return SheetColumns(
            hostname=host,
            ip=ip,
            dns_name=dns,
        )

    @staticmethod
    def _header(
        df: pd.DataFrame,
        pattern: re.Pattern[str],
        excluded: set[str],
    ) -> str | None:
        for column in df.columns:
            name = str(column).strip()
            if name not in excluded and pattern.search(name):
                return name
        return None

    @staticmethod
    def _content(
        df: pd.DataFrame,
        excluded: set[str],
        validator: Callable[[object], object],
    ) -> str | None:
        best: tuple[float, str | None] = (0.0, None)
        for column in df.columns:
            name = str(column)
            if name in excluded:
                continue
            values = df[column].dropna()
            if values.empty:
                continue
            ratio = sum(bool(validator(v)) for v in values) / len(values)
            if ratio >= 0.5 and ratio > best[0]:
                best = (ratio, name)
        return best[1]
