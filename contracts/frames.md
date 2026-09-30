# Frames

Exact shapes of the DataFrames passed across public boundaries. Owned by PMs; changes need PM approval.

All frames use a default `RangeIndex` (keys are columns, not the index). String columns use the NumPy `object` dtype holding Python `str` (or `None` where nullable), not the pandas `string` extension dtype. Datetimes are timezone-naive `datetime64[ns]` at midnight.

## PriceFrame

Long format: one row per (trading day, ticker).

| column    | dtype            | nullable | notes |
|-----------|------------------|----------|-------|
| date      | `datetime64[ns]` | no       | naive, trading days only |
| ticker    | `object` (str)   | no       | iPick ticker (`BRK.B`, not Yahoo's `BRK-B`) |
| adj_close | `float64`        | yes      | split- and dividend-adjusted close |
| close     | `float64`        | yes      | raw close |
| volume    | `float64`        | yes      | shares traded; float so missing days can be NaN |

- Unique on (`date`, `ticker`).
- Sorted by `ticker`, then `date`.
- `SPY` is always present as the benchmark.
- Convert tickers with `vendor/yf_symbols.py get_ticker_yf()` when talking to Yahoo; the frame always holds the iPick ticker.

## FeatureFrame

One row per (as-of date, ticker).

| column           | dtype            | nullable | notes |
|------------------|------------------|----------|-------|
| as_of            | `datetime64[ns]` | no       | naive; every feature uses only data dated on or before `as_of` |
| ticker           | `object` (str)   | no       | iPick ticker |
| track            | `object` (str)   | yes      | track display name from ticker_track; `None` when the lookup is `"-"` or missing |
| normalized_track | `object` (str)   | yes      | `vendor/util_track.py normalize(track)`; `None` when `track` is `None` |
| eligible         | `bool`           | no       | tradable, empty `asset_type`, not crypto (ticker ending in `USD`) |
| *features*       | see `features.md`| —        | columns listed in `contracts/features.md` |

- Unique on (`as_of`, `ticker`).
- No column may come from `fixtures/yf_info_snapshot.parquet` (today's snapshot; lookahead).
- Forward-looking labels are not part of FeatureFrame; they come from `forward_*` functions.
