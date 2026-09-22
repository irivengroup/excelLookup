from excel_host_lookup.models import HostRecord
from excel_host_lookup.services import HostLookupService


def test_lookup_ok() -> None:
    index = {
        "srv01": [
            HostRecord(
                "srv01",
                "10.0.0.1",
                "srv01.example.com",
                "Production Servers",
                2,
            )
        ]
    }

    result = HostLookupService(index).lookup("srv01")

    assert result.status == "OK"
    assert result.as_dict()["IP_Trouvee"] == "10.0.0.1"
    assert result.as_dict()["FQDN_Trouve"] == "srv01.example.com"


def test_lookup_ip_conflict() -> None:
    index = {
        "srv01": [
            HostRecord("srv01", "10.0.0.1", "srv01.example.com", "A", 2),
            HostRecord("srv01", "10.0.0.2", "srv01.example.com", "B", 3),
        ]
    }

    result = HostLookupService(index).lookup("srv01")

    assert result.status == "CONFLIT"
    assert result.ip_conflict


def test_lookup_not_found() -> None:
    result = HostLookupService({}).lookup("unknown")

    assert result.status == "NON_TROUVE"
