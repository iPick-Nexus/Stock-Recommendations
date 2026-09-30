import dataclasses
import json
from datetime import date, datetime

import pandas as pd
import pytest

from contracts import types
from contracts.types import (
    DominanceFinding,
    Holding,
    Pick,
    PortfolioInput,
    PortfolioReport,
    Recommendation,
    Reward,
    TrackAssignment,
    to_json,
)

AS_OF = date(2026, 9, 25)

HOLDING = Holding(ticker="BRK.B", shares=-10.0, avg_cost=None, source="csv")
FINDING = DominanceFinding(
    ticker="AAA",
    dominated_by="BBB",
    track="Cloud Software",
    dominator_held=False,
    metrics={"AAA": {"1y_return": 0.05}, "BBB": {"1y_return": 0.25}},
    explanation="BBB beat AAA on return and risk.",
)

SAMPLES = [
    Recommendation(ticker="MSFT", as_of=AS_OF, rank=1, score=0.91, track="Cloud Software",
                   model_version="xgb-0", reasons=["momentum"]),
    Recommendation(ticker="XYZ", as_of=AS_OF, rank=5, score=0.1, track=None, model_version="xgb-0"),
    HOLDING,
    PortfolioInput(holdings=[HOLDING], cash=1234.5, unrecognized=["NOPE"], warnings=["w"]),
    TrackAssignment(ticker="MSFT", track="Cloud Software", normalized_track="cloud software",
                    method="lookup"),
    TrackAssignment(ticker="ZZZ", track=None, normalized_track=None, method="llm", confidence=0.4),
    FINDING,
    PortfolioReport(as_of=AS_OF, holdings=[{"ticker": "AAA", "risk_level": "high"}],
                    dominance=[FINDING],
                    recommendations=[{"action": "trim", "ticker": "AAA", "reason": "r"}],
                    risk={"beta": 1.2, "flags": ["concentration"]}, narrative=None,
                    policy_version="p1"),
    Pick(pick_id=f"short_target:TSLA:{AS_OF.isoformat()}", agent="short_target", ticker="TSLA",
         as_of=AS_OF, entry_price=250.0, weight_pct=1.0, horizon_days=20, direction=-1, score=0.7,
         context={"rsi": 80.0}),
    Reward(pick_id=f"short_target:TSLA:{AS_OF.isoformat()}", exit_date=date(2026, 10, 23),
           exit_price=240.0, raw_return=0.04, benchmark_return=0.01, reward=0.03),
]


def _expected(value):
    """What the backend should receive: asdict() with dates as ISO strings."""
    if dataclasses.is_dataclass(value):
        return _expected(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {k: _expected(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_expected(v) for v in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def test_samples_cover_every_dataclass():
    all_types = {obj for obj in vars(types).values()
                 if isinstance(obj, type) and dataclasses.is_dataclass(obj)}
    assert all_types == {type(s) for s in SAMPLES}


@pytest.mark.parametrize("sample", SAMPLES, ids=lambda s: type(s).__name__)
def test_round_trips_through_to_json(sample):
    assert json.loads(to_json(sample)) == _expected(sample)


def test_list_round_trips_through_to_json():
    assert json.loads(to_json(SAMPLES)) == _expected(SAMPLES)


def test_to_json_rejects_unknown_types():
    with pytest.raises(TypeError):
        to_json({"x": object()})


# --- fixtures ---------------------------------------------------------------

def test_universe(load_parquet):
    df = load_parquet("universe.parquet")
    assert {"ticker", "companyName", "industry", "tradable", "asset_type"} <= set(df.columns)
    assert pd.api.types.is_bool_dtype(df["tradable"])
    assert df["ticker"].is_unique
    assert (df["asset_type"] == "").any()


def test_ticker_track(load_json):
    data = load_json("ticker_track.json")
    assert isinstance(data, dict) and data
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in data.items())


YF_INFO_FIELDS = {
    "marketCap", "revenueGrowth", "profitMargins", "netIncomeToCommon", "trailingPE", "forwardPE",
    "beta", "averageVolume", "floatShares", "sharesOutstanding", "heldPercentInstitutions",
    "shortPercentOfFloat", "sector", "industry", "currency",
}


def test_yf_info_snapshot(load_parquet):
    df = load_parquet("yf_info_snapshot.parquet")
    tickers = df["ticker"] if "ticker" in df.columns else df.index.to_series()
    assert tickers.is_unique
    assert YF_INFO_FIELDS <= set(df.columns)


def test_usd_currency_ratio(load_json):
    data = load_json("usd_currency_ratio.json")
    assert isinstance(data, dict) and data
    assert all(isinstance(v, (int, float)) and v > 0 for v in data.values())


def _return_fields(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(k, str) and k.endswith(" return"):
                yield k, v
            else:
                yield from _return_fields(v)
    elif isinstance(node, list):
        for v in node:
            yield from _return_fields(v)


def test_track_table_sample(load_json):
    data = load_json("track_table_sample.json")
    returns = list(_return_fields(data))
    assert returns, "expected fields like '1y return'"
    for key, value in returns:
        assert isinstance(value, list) and len(value) == 2, key
        assert isinstance(value[0], str) and value[0].endswith("%"), key


POSITION_KEYS = {"symbol", "shares", "price", "total_value", "profit_loss", "weight",
                 "todays_gain_loss", "avg_cost"}


def test_positions_sample(load_json):
    rows = load_json("positions_sample.json")
    assert isinstance(rows, list) and rows
    for row in rows:
        assert POSITION_KEYS <= set(row), row
        assert 0 <= row["weight"] <= 100
    assert any(row["symbol"] == "CASH" for row in rows)


def test_manifest_copy_matches(load_json):
    from importlib.resources import files

    fixture_manifest = load_json("MANIFEST.json")
    packaged = files("contracts") / "MANIFEST.json"
    assert packaged.is_file(), "contracts/MANIFEST.json must be a copy of fixtures/MANIFEST.json"
    assert json.loads(packaged.read_text()) == fixture_manifest
