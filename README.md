# EuroStock Scout v2.7

v2.7 adds transparent beta validation without loosening the trading rules.

For each stock it displays:
- beta;
- aligned observation count;
- correlation to the regional benchmark;
- annualized stock volatility;
- annualized benchmark volatility;
- stock/benchmark volatility ratio.

For aligned daily returns, beta is approximately:

`correlation × (stock volatility / benchmark volatility)`

This version also fixes the stale yellow banner that still mentioned v2.5.

Everything from v2.6 remains: Europe/Canada, real regional benchmarks, Scout Grade, RSI, SMA20/50, momentum, ATR, dividends, Morningstar research links, entry/target/stop and 24-hour caching.

Replace the same six files in GitHub, commit, and confirm the app heading says v2.7.
