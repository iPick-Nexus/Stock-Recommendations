"""Types shared by ipick-ml and the iPick backend. Changes need PM approval."""
from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal, Protocol

AgentName = Literal["power_pick", "hidden_gem", "short_target"]


class LLMClient(Protocol):
    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str: ...


@dataclass(frozen=True)
class Recommendation:
    ticker: str
    as_of: date
    rank: int                      # 1..k
    score: float
    track: str | None
    model_version: str
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Holding:
    ticker: str
    shares: float                  # negative = short
    avg_cost: float | None
    source: Literal["ib", "csv", "manual"]


@dataclass(frozen=True)
class PortfolioInput:
    holdings: list[Holding]
    cash: float
    unrecognized: list[str]        # symbols not in the universe; never silently dropped
    warnings: list[str]


@dataclass(frozen=True)
class TrackAssignment:
    ticker: str
    track: str | None
    normalized_track: str | None
    method: Literal["lookup", "llm", "fund", "unknown"]
    confidence: float | None = None


@dataclass(frozen=True)
class DominanceFinding:
    ticker: str                    # the dominated holding
    dominated_by: str
    track: str
    dominator_held: bool           # True if the user already owns dominated_by
    metrics: dict[str, dict[str, float]]   # {ticker: {metric: value}}
    explanation: str


@dataclass(frozen=True)
class PortfolioReport:
    as_of: date
    holdings: list[dict]           # per-holding metrics and risk level
    dominance: list[DominanceFinding]
    recommendations: list[dict]    # {action: "remove"|"trim"|"review", ticker, reason}
    risk: dict                     # portfolio-level metrics and flags
    narrative: str | None
    policy_version: str


@dataclass(frozen=True)
class Pick:
    pick_id: str                   # f"{agent}:{ticker}:{as_of.isoformat()}"
    agent: AgentName
    ticker: str
    as_of: date
    entry_price: float
    weight_pct: float              # 1.0 = 1% of portfolio
    horizon_days: int              # trading days
    direction: Literal[1, -1]      # -1 for short targets
    score: float
    context: dict[str, float]


@dataclass(frozen=True)
class Reward:
    pick_id: str
    exit_date: date
    exit_price: float
    raw_return: float
    benchmark_return: float
    reward: float


def to_json(obj) -> str:
    """Serialize any contract type (or list of them) for the backend."""
    def default(value):
        if dataclasses.is_dataclass(value):
            return dataclasses.asdict(value)
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        raise TypeError(f"{type(value).__name__} is not serializable")
    return json.dumps(obj, default=default)
