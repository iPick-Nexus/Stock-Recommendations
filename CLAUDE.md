# Stock-Recommendations (Team 1)

Part of the iPick ML build, which is split across three repos:
- Stock-Recommendations (this repo, Team 1): package stock_recs (stock_recs/data: prices and features; stock_recs/recommend: XGBoost top 5). It also ships the shared packages contracts/ and vendor/.
- Portfolio-Analysis (Team 2): package portfolio_analysis. Installs this repo as a pinned dependency.
- Portfolio-Reinforcement-Learning (Team 3): package pick_agents (agents and backtest). Installs this repo as a pinned dependency.

The private iPick Flask backend (iPickAI_flask) installs all three as pip packages pinned to git tags. Code here NEVER reads or writes iPick's S3, database, Flask app or user data. The backend passes data in and stores whatever comes out.

## Folders
- stock_recs/data and stock_recs/recommend: Team 1. Teams 2 and 3 import stock_recs.data, so its public functions are a contract too: don't rename or change a signature without telling them.
- contracts/, vendor/, fixtures/: owned by PMs. Don't edit them; open an issue and tag a PM. They're packaged with this repo so Teams 2 and 3 get the exact same copies.
- examples/: example JSON outputs for the backend.
- tests/team1 and tests/contract (PM-owned).
- Team 3's backtest harness (pick_agents.backtest) is used only by scripts in scripts/, never by stock_recs. Install it with `pip install --no-deps "pick-agents @ git+ssh://git@github.com/iPickAI/Portfolio-Reinforcement-Learning.git@TAG"`. Never add it to pyproject.toml; that would make the two repos depend on each other.

## Rules
- Write pure functions and classes. Inputs are pandas DataFrames, dicts or the dataclasses in contracts/types.py. Outputs are JSON-serializable dataclasses or DataFrames that match contracts/.
- The only network access allowed: price downloads in stock_recs/data/prices.py (yfinance), and LLM calls through the LLMClient protocol the caller passes in. Tests never touch the network; mock both.
- Never hard-code paths, bucket names, credentials, API keys or model names. Take them as arguments.
- Point-in-time: every function that computes something "as of" a date takes `as_of` explicitly and uses only data dated on or before it. Labels and rewards are the only things that look forward, and they live in functions whose names say so (forward_*, settle_*).
- Put tunable thresholds in the JSON block of skills/NAME/SKILL.md. Load and validate them at import, following vendor/track_leader.py load_leader_policy(). Fail loudly on a bad policy.
- Versions must match production: Python 3.11 (PM: fill in), pandas==2.3.0, numpy==1.26.4. Add dependencies only to pyproject.toml, pinned, and compatible with these.
- Every public function gets a pytest test that uses fixtures/. CI must pass before merging. Keep PRs small.

## Data facts from production
- fixtures/universe.parquet: ticker, companyName, industry, tradable (bool), asset_type ("" for common stock; otherwise ETF, Mutual Fund, Closed Fund, ...). About 11,000 rows. Tickers ending in "USD" are crypto. Stock recommendations and agent candidate lists use only tradable rows with an empty asset_type and no crypto.
- iPick tickers use "." for share classes (BRK.B). Yahoo uses "-". Always convert with vendor/yf_symbols.py get_ticker_yf(); never write your own mapping.
- fixtures/ticker_track.json maps ticker -> track display name (about 1,500 tracks). The value "-" means no track. Compare and group tracks only through vendor/util_track.py normalize(name).
- fixtures/yf_info_snapshot.parquet: one row per ticker, holding Yahoo Finance info fields (marketCap, revenueGrowth, profitMargins, netIncomeToCommon, trailingPE, forwardPE, beta, averageVolume, floatShares, sharesOutstanding, heldPercentInstitutions, shortPercentOfFloat, sector, industry, currency). revenueGrowth is latest-quarter year-over-year growth as a fraction (0.20 = 20%). THIS IS TODAY'S SNAPSHOT: never use it as a feature in training or backtests (that would be lookahead). Use it only for live filters and display.
- For ETFs and funds, size is totalAssets, and the fundamental fields are None.
- Non-USD companies report marketCap in their own currency. fixtures/usd_currency_ratio.json gives currency -> units per 1 USD. Divide by the ratio to get USD.
- fixtures/track_table_sample.json holds track rows in the backend's shape. Returns look like "1y return": ["25.00%", 25], where the first element is a percent string. Parse them with vendor/track_leader.py period_return().
- The track leader rule is vendor/track_leader.py select_track_leader(stocks, expected_count). Call it; never reimplement it. Live code receives leaders as a dict {normalized_track: ticker} from the caller.
- fixtures/positions_sample.json (synthetic) has the backend's portfolio shape: a list of {symbol, shares, price, total_value, profit_loss, weight, todays_gain_loss, avg_cost}. weight is a PERCENT from 0 to 100. There is a "CASH" row.

## Frames (see contracts/frames.md for exact dtypes)
- PriceFrame (long format): date (datetime64, naive, trading days only), ticker (iPick ticker), adj_close, close, volume. Unique on (date, ticker). SPY is always included as the benchmark.
- FeatureFrame: as_of, ticker, track, normalized_track, eligible, plus the feature columns listed in contracts/features.md (Team 1). Unique on (as_of, ticker).

## Types
contracts/types.py: Recommendation, Holding, PortfolioInput, TrackAssignment, DominanceFinding, PortfolioReport, Pick, Reward, LLMClient. Use these exact types at every public boundary.
