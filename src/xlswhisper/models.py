from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class HostRecord:
    hostname: str
    ip: str | None
    fqdn: str | None
    sheet: str
    row: int


@dataclass(frozen=True, slots=True)
class SearchHost:
    hostname: str
    sheet: str | None = None
    row: int | None = None


@dataclass(frozen=True, slots=True)
class LookupResult:
    search: SearchHost
    ip: str | None
    fqdn: str | None
    status: str
    conflict_ip: bool
    conflict_fqdn: bool
    sources: tuple[str, ...] = field(default_factory=tuple)
