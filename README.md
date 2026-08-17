# EuroStock Scout v2.6

## Reliability change
v2.6 calculates beta against a real regional benchmark instead of the stocks being scanned.

- Europe: EXSA / iShares STOXX Europe 600 UCITS ETF (tries XETR then XFRA)
- Canada: XIU / iShares S&P/TSX 60 Index ETF (XTSE)

For each stock, beta is calculated from aligned daily returns against the benchmark. The app records the number of aligned observations as `Beta n=`.

If the benchmark cannot be downloaded, v2.6 stops and reports beta unavailable rather than fabricating values.

## Also changed
- Dividend history is attempted for up to 8 scanned stocks.
- Keeps Europe / Canada, Scout Grade, RSI, SMA20/50, momentum, ATR, entry/target/stop, Morningstar research link and 24-hour caching.

## Install
Replace the same six files in your GitHub repository, commit, and confirm the heading says v2.6.

Use Quick / 8 and ~1 year for the first test.

This is decision support, not individualized investment advice.
