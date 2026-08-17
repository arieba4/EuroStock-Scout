# EuroStock Scout v2.2

## Main change
v2.2 replaces Twelve Data with **Marketstack** for end-of-day historical stock prices.

Marketstack currently offers a free plan with 100 market-data requests per month and up to 12 months of historical EOD data. The app batches tickers by exchange and stores successful scans in browser local storage for 24 hours to preserve quota.

## Features
- Separate Europe and Canada market buttons.
- European and TSX stock universes.
- Historical beta from the selected regional scan basket.
- RSI(14), SMA20, SMA50, 20-day momentum and ATR(14).
- Scout Grade A+ to F.
- BUY ZONE / WAIT / AVOID.
- €5,000 or C$5,000 portfolio allocation.
- 3%, 3.5%, or 4% gross target.
- ATR-based stop.
- Dividend history attempted for only the top four ranked stocks to preserve API quota.
- Morningstar research links; no fabricated Morningstar star rating.
- 24-hour scan cache.
- PWA / Add to Home Screen support.

## Setup
1. Create a Marketstack account and obtain an API key.
2. Replace the six files in your existing GitHub repository with the six files from this package.
3. Wait for GitHub Pages to redeploy.
4. Open the app, paste the Marketstack API key and save it locally.
5. Start with Quick / 8 stocks.
6. Tap Test API connection, then Scan selected market.

## Important
Marketstack's free plan is end-of-day, not true intraday live pricing. Dividend access can depend on the provider plan. If the dividend endpoint is unavailable, the main scan continues and shows N/A for dividend yield.

Marketstack counts each ticker requested toward monthly quota even if multiple tickers are sent in one HTTP request. With Quick / 8 stocks, a price scan consumes approximately 8 symbol requests, plus optional dividend queries. The 24-hour cache avoids repeating those calls.

Morningstar star ratings are proprietary licensed research and are not reproduced by this app.

This is decision support, not individualized investment advice.
