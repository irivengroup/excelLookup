from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Limits:
    max_xlsx_bytes: int = 256 * 1024 * 1024
    max_member_bytes: int = 128 * 1024 * 1024
    max_xml_bytes: int = 64 * 1024 * 1024
    max_sheets: int = 512
    max_rows: int = 1_000_000
    max_columns: int = 16_384
    max_cells_per_row: int = 16_384
    max_shared_strings: int = 2_000_000
    max_string_bytes: int = 1024 * 1024
    max_search_hosts: int = 2_000_000
    max_sources_per_host: int = 100_000
    max_compression_ratio: int = 200
