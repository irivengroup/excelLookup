from __future__ import annotations

import ipaddress
import re

import pandas as pd


_HOSTNAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")


class Normalizer:
    @staticmethod
    def string(value: object) -> str:
        if value is None or pd.isna(value):
            return ""
        text = str(value).strip()
        if text.endswith(".0") and text[:-2].isdigit():
            text = text[:-2]
        return text.lower()

    @classmethod
    def hostname(cls, value: object) -> str:
        text = cls.string(value)
        if not text or len(text) > 253:
            return ""
        return text if _HOSTNAME.fullmatch(text) else ""

    @classmethod
    def fqdn(cls, value: object) -> str:
        return cls.hostname(value).rstrip(".")

    @staticmethod
    def ipv4(value: object) -> str:
        if value is None or pd.isna(value):
            return ""
        try:
            address = ipaddress.ip_address(str(value).strip())
        except ValueError:
            return ""
        return str(address) if address.version == 4 else ""
