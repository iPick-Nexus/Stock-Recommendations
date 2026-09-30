import json
import os
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Fixture folder: $IPICK_ML_FIXTURES if set, else <repo>/fixtures."""
    return Path(os.environ.get("IPICK_ML_FIXTURES") or REPO_ROOT / "fixtures")


@pytest.fixture(scope="session")
def fixture_path(fixtures_dir):
    """Return the path of a fixture file, skipping the test if it is missing."""
    def get(name: str) -> Path:
        path = fixtures_dir / name
        if not path.exists():
            pytest.skip(f"{path} not present (fixtures not imported yet)")
        return path
    return get


@pytest.fixture(scope="session")
def load_json(fixture_path):
    def load(name: str):
        return json.loads(fixture_path(name).read_text())
    return load


@pytest.fixture(scope="session")
def load_parquet(fixture_path):
    def load(name: str) -> pd.DataFrame:
        return pd.read_parquet(fixture_path(name))
    return load
