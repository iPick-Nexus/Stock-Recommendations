# Features (Team 1)

Feature columns of the FeatureFrame (see `frames.md`), beyond the key columns `as_of, ticker, track, normalized_track, eligible`.

**Placeholder:** Team 1 fills this in as features are added. Every feature needs a row here before it ships. Changes after a release tag need PM approval, because Teams 2 and 3 read these columns.

| column | dtype | nullable | window / lookback | definition | source |
|--------|-------|----------|-------------------|------------|--------|
| _TBD_  |       |          |                   |            |        |

Rules:
- Point-in-time only: computed from data dated on or before `as_of`.
- Never sourced from `fixtures/yf_info_snapshot.parquet`.
- Returns are fractions (0.20 = 20%), not percents.
