from excel_host_lookup.limits import Limits


def test_limits_are_positive():
    limits = Limits()
    assert limits.max_rows > 0
    assert limits.max_columns > 0
    assert limits.max_compression_ratio > 0
