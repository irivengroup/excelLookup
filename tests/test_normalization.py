from excel_host_lookup.normalization import Normalizer


def test_hostname_is_normalized() -> None:
    assert Normalizer.hostname("  SRV01.EXAMPLE.COM  ") == "srv01.example.com"


def test_excel_numeric_suffix_is_removed() -> None:
    assert Normalizer.hostname("123.0") == "123"


def test_invalid_hostname_is_rejected() -> None:
    assert Normalizer.hostname("bad host") == ""


def test_ipv4_validation() -> None:
    assert Normalizer.ipv4("10.20.30.40") == "10.20.30.40"
    assert Normalizer.ipv4("999.999.999.999") == ""


def test_fqdn_trailing_dot_is_removed() -> None:
    assert Normalizer.fqdn("srv01.example.com.") == "srv01.example.com"
