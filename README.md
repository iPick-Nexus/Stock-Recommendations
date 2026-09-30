# Stock Recommendations (XGBoost)

Recommends 5 stocks per user out of the full universe of publicly traded companies, using an XGBoost model over cross-sectional stock features.

## Overview

The universe is ~11,000 publicly traded companies organized into ~1,000 investment tracks (expanding toward ~1,500). Rather than modeling every stock's time series, the problem is framed as a **recommendation problem**: the model scores each stock from a snapshot of tabular features and returns the top 5 per user.

**V1 scope:** user constraints (budget, risk tolerance) are ignored. Constraint-aware personalization lives in the separate Ranking System project.

## How it works

1. Assemble a feature table — one row per company, columns for fundamentals, momentum, track membership, etc. (`n_stocks × n_features`).
2. Define the target label (e.g. forward return over a fixed horizon).
3. Train the XGBoost model on the feature table.
4. Score every stock and take the top 5 per user.
5. Backtest the top-5 output against held-out data and iterate on features.
6. Serve the top-5 output through the iPick backend.

## Tech stack

- **Model:** XGBoost (gradient-boosted trees)
- **Data / feature engineering:** Python, pandas, NumPy
- **Training & evaluation:** scikit-learn
- **Serving:** existing iPick backend

## Getting started

Requires Python 3.11 (the production version; see `CLAUDE.md`). All dependencies are pinned in `pyproject.toml`; there is no `requirements.txt`.

```bash
git clone git@github.com:iPick-Nexus/Stock-Recommendations.git
cd Stock-Recommendations

python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest
```

Tests read fixtures from `fixtures/`, or from `$IPICK_ML_FIXTURES` if set. Tests never touch the network. Read `CLAUDE.md` before writing code: it has the rules (pure functions, point-in-time `as_of`, no hard-coded paths or keys) and the production data facts.

## Project structure

```
Stock-Recommendations/
├── stock_recs/             # Team 1 package
│   ├── data/               # prices (yfinance) and features; imported by Teams 2 and 3, so its API is a contract
│   └── recommend/          # XGBoost top-5 recommendations
├── contracts/              # PM-owned: types.py, frames.md, features.md, MANIFEST.json (shipped to Teams 2 and 3)
├── vendor/                 # PM-owned: code vendored from the iPick backend (track leader, ticker mapping, ...)
├── fixtures/               # PM-owned: production-shaped fixture data, no real user data
├── examples/               # example JSON outputs for the backend
├── tests/
│   ├── team1/              # Team 1 tests
│   └── contract/           # PM-owned contract tests
├── pyproject.toml          # packages stock_recs, contracts and vendor; pinned dependencies
└── CLAUDE.md               # shared rules for all three repos
```

Changes to `contracts/`, `vendor/`, `fixtures/`, `CLAUDE.md` or `tests/contract/` need PM review (see `.github/CODEOWNERS`). To request one, open an issue and tag a PM.

## Release process

1. **Merge by Friday.** Anything meant for the week's release must be merged to `main` with CI green by end of day Friday. Keep PRs small; never push to `main` directly.
2. **PMs tag `vX.Y.0`.** After the Friday cutoff, a PM tags the `main` commit and pushes the tag:
   ```bash
   git switch main && git pull
   git tag -a vX.Y.0 -m "Release vX.Y.0"
   git push origin vX.Y.0
   ```
   Patch releases (`vX.Y.1`, ...) are for urgent fixes only.
3. **Consumers pin the tag.** The iPick backend (iPickAI_flask), Portfolio-Analysis (Team 2) and Portfolio-Reinforcement-Learning (Team 3) install this repo pinned to that tag and never to a branch:
   ```
   stock-recommendations @ git+ssh://git@github.com/iPick-Nexus/Stock-Recommendations.git@vX.Y.0
   ```
   Consumers upgrade by bumping the tag in their own PR.

## Roadmap

- [ ] Build the feature pipeline
- [ ] Define and validate the target label
- [ ] Train baseline XGBoost model
- [ ] Top-5 scoring + backtest harness
- [ ] Wire output into the iPick backend

## Resources

- XGBoost — Get Started (official docs): https://xgboost.readthedocs.io/en/stable/get_started.html
- StatQuest — XGBoost video series + "XGBoost in Python from Start to Finish": https://www.youtube.com/watch?v=GrJP9FLV3FE
- scikit-learn — Getting Started (official): https://scikit-learn.org/stable/getting_started.html
- pandas / NumPy — freeCodeCamp "Data Analysis with Python" full course: https://www.freecodecamp.org/news/how-to-analyze-data-with-python-pandas/
