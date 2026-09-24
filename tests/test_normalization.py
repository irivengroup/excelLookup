from excel_host_lookup.normalization import hostname, parse_host_list


def test_mixed_separators():
    assert parse_host_list("srv01,srv02;srv03|srv04 srv05") == [
        "srv01", "srv02", "srv03", "srv04", "srv05"
    ]


def test_deduplication():
    assert parse_host_list("SRV01,srv01; srv01") == ["srv01"]


def test_invalid_host():
    assert hostname("bad host") == ""
    assert hostname("srv01.example.com") == "srv01.example.com"
