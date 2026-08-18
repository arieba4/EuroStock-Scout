# EuroStock Scout v3.4

EuroStock Scout is an end-of-day swing-trading decision-support screener for European and Canadian equities. It is not a brokerage feed, forecast, or guarantee of returns.

## v3.4 screening funnel

The weekday GitHub Actions job builds a broad universe from major European national indices and the S&P/TSX Composite. The existing 110-stock curated universe remains a fallback when a constituent source is unavailable.

The pipeline is:

1. broad universe (normally about 400–600 symbols);
2. data-quality and hard liquidity filters;
3. trend and regional-market context filter;
4. complete Scout and Opportunity scoring;
5. Top 20 shortlist;
6. action-first Top 5.

`Scout Score` measures the technical quality of the stock. `Opportunity Score` measures whether entering now is attractive. A strong stock can therefore be marked `WAIT` when it is too close to resistance or has near-term earnings risk.

## Independent dimensions

- trend: SMA20, SMA50, SMA200 and distance from SMA200;
- momentum: RSI and 20-day momentum;
- relative strength: 20- and 60-day return versus the stock's regional benchmark;
- liquidity: 20-day average traded value (hard filter);
- confirmation: latest volume versus 20-day average;
- volatility: ATR, beta and stock/benchmark volatility;
- price structure: 20/50-day support and resistance;
- economics: modeled entry, target, stop and reward/risk;
- environment: benchmark regime and next-earnings warning.

Europe and Canada are normalized against their own benchmarks before the All Markets ranking. Earnings within seven days block a new `BUY ZONE` by default but can be allowed in the interface.

## Updating data

Run **Actions → Update market data → Run workflow** after installing this version. The workflow also runs weekdays at 22:37 UTC and commits only `data/market-data.json`.

The constituent-table fetch is best-effort. Source failures are recorded in `universe_warnings`; the workflow continues with the curated core and all sources that succeeded.
