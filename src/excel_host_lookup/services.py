from __future__ import annotations

from collections.abc import Iterable

from .models import HostRecord, LookupResult


class HostLookupService:
    def __init__(self, index: dict[str, list[HostRecord]]) -> None:
        self.index = index

    def lookup(self, hostname: str) -> LookupResult:
        result = LookupResult(hostname)
        for record in self.index.get(hostname, []):
            if record.ip:
                result.ips.add(record.ip)
            if record.fqdn:
                result.fqdns.add(record.fqdn)
            result.sources.add(f"{record.sheet}:L{record.row}")
        return result

    def lookup_many(self, hosts: Iterable[str]) -> list[LookupResult]:
        return [self.lookup(host) for host in hosts]
