from pathlib import Path

import tomllib


def test_no_runtime_dependencies():
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["dependencies"] == []
