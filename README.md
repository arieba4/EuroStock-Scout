# EuroStock Scout v2.3

## Why v2.3 exists
v2.2 used an exchange query parameter with the generic EOD endpoint. Marketstack documents an exchange-specific EOD route (`/exchanges/{MIC}/eod`). v2.3 now uses that route.

## v2.3 data flow
1. Uses the expected ticker and exchange MIC.
2. Checks a persistent local ticker mapping.
3. If no mapping exists, uses Marketstack's ticker search endpoint.
4. Selects the result matching the expected exchange MIC.
5. Saves that mapping locally.
6. Downloads EOD history from `/exchanges/{MIC}/eod`.
7. Calculates beta, RSI, moving averages, momentum, ATR, Scout Grade and entry/exit levels.
8. Checks dividends for only the top candidates.
9. Saves the completed market scan for 24 hours.

## Features
- European and Canadian market buttons.
- €5,000 / C$5,000 portfolio modes.
- Beta target near 1.
- 3–4% target.
- BUY ZONE / WAIT / AVOID.
- Scout Grade A+–F.
- Dividend status and trailing yield when available.
- Morningstar research links.
- Persistent Marketstack ticker mappings.
- 24-hour scan cache.

## Updating GitHub
Replace the same six files in your existing repository with the six v2.3 files. Commit the changes. After GitHub Pages deploys, hard refresh or clear the old PWA/service-worker cache if v2.2 is still shown.

## Marketstack
The Marketstack Free plan currently includes 100 requests/month, EOD data, one year of history, splits/dividends, ticker info, exchange info and HTTPS.

This app is decision support, not individualized investment advice.
