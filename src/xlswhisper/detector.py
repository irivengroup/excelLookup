from dataclasses import dataclass
import re
import unicodedata


def normalize_header(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


@dataclass(frozen=True, slots=True)
class Columns:
    host: int | None
    ip: int | None
    dns: int | None


class ColumnDetector:
    HOST = re.compile(
        r"\b(host|hostname|host name|computer|computer name|machine|vm|"
        r"machine name|server|server name|node|node name)\b"
    )
    IP = re.compile(r"\b(ip|ipv4|address|ip address|ipaddress)\b")
    DNS = re.compile(r"\b(dns|dns name|fqdn|domain name|domainname)\b")

    def detect(self, headers: list[str]) -> Columns:
        normalized = [normalize_header(h) for h in headers]
        return Columns(
            host=self._find(normalized, self.HOST),
            ip=self._find(normalized, self.IP),
            dns=self._find(normalized, self.DNS),
        )

    @staticmethod
    def _find(headers: list[str], pattern: re.Pattern[str]) -> int | None:
        for index, header in enumerate(headers):
            if pattern.search(header):
                return index
        return None
