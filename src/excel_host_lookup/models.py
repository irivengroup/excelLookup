from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class HostRecord:
    hostname: str
    ip: str
    fqdn: str
    sheet: str
    row: int


@dataclass(frozen=True, slots=True)
class SheetColumns:
    hostname: str | None = None
    ip: str | None = None
    dns_name: str | None = None


@dataclass(slots=True)
class LookupResult:
    hostname: str
    ips: set[str] = field(default_factory=set)
    fqdns: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)

    @property
    def found(self) -> bool:
        return bool(self.ips or self.fqdns)

    @property
    def ip_conflict(self) -> bool:
        return len(self.ips) > 1

    @property
    def fqdn_conflict(self) -> bool:
        return len(self.fqdns) > 1

    @property
    def status(self) -> str:
        if not self.found:
            return "NON_TROUVE"
        if self.ip_conflict or self.fqdn_conflict:
            return "CONFLIT"
        return "OK"

    def as_dict(self) -> dict[str, str]:
        return {
            "Hostname": self.hostname,
            "IP_Trouvee": ";".join(sorted(self.ips)) or "Non trouvé",
            "FQDN_Trouve": ";".join(sorted(self.fqdns)) or "Non trouvé",
            "Statut": self.status,
            "Conflit_IP": "OUI" if self.ip_conflict else "",
            "Conflit_FQDN": "OUI" if self.fqdn_conflict else "",
            "Sources": ";".join(sorted(self.sources)),
        }
