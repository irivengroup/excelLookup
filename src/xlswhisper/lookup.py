from collections.abc import Iterable

from .index import InventoryIndex
from .limits import Limits
from .models import LookupResult, SearchHost


class HostLookupService:
    def __init__(
        self,
        index: InventoryIndex,
        limits: Limits | None = None,
    ) -> None:
        self.index = index
        self.limits = limits or Limits()

    def lookup(self, hosts: Iterable[SearchHost]) -> list[LookupResult]:
        results: list[LookupResult] = []
        for search in hosts:
            records = self.index.find(search.hostname)
            if len(records) > self.limits.max_sources_per_host:
                raise ValueError(
                    f"Trop de sources pour {search.hostname!r}."
                )

            ips = sorted({r.ip for r in records if r.ip})
            fqdns = sorted({r.fqdn for r in records if r.fqdn})
            conflict_ip = len(ips) > 1
            conflict_fqdn = len(fqdns) > 1
            status = (
                "NON_TROUVE" if not records
                else "CONFLIT" if conflict_ip or conflict_fqdn
                else "OK"
            )
            results.append(
                LookupResult(
                    search=search,
                    ip=ips[0] if ips else None,
                    fqdn=fqdns[0] if fqdns else None,
                    status=status,
                    conflict_ip=conflict_ip,
                    conflict_fqdn=conflict_fqdn,
                    sources=tuple(
                        f"{r.sheet}:L{r.row}" for r in records
                    ),
                )
            )
        return results
