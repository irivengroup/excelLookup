from __future__ import annotations

import ipaddress
import re

SEPARATORS = re.compile(r"[,;|\s]+")
COMMENT = re.compile(r"\s+#.*$")
HOST_LABEL = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]*$")
INVALID_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def clean(value: object) -> str:
    text = str(value).strip()
    if INVALID_CONTROL.search(text):
        return ""
    return text


def hostname(value: object) -> str:
    text = clean(value).rstrip(".").lower()
    if not text or len(text) > 253 or not HOST_LABEL.fullmatch(text):
        return ""
    labels = text.split(".")
    if any(not label or len(label) > 63 for label in labels):
        return ""
    return text


def fqdn(value: object) -> str:
    return hostname(value)


def ipv4(value: object) -> str | None:
    text = clean(value)
    if not text:
        return None
    try:
        address = ipaddress.ip_address(text)
    except ValueError:
        return None
    return str(address) if address.version == 4 else None


def parse_host_list(value: str) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for line in value.splitlines():
        line = COMMENT.sub("", line).strip()
        if not line:
            continue
        for token in SEPARATORS.split(line):
            normalized = hostname(token)
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
    return result
