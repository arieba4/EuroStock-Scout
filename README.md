# EuroStock Scout v3.0

v3.0 removes browser-side market-data APIs from the critical path.

## Architecture
A GitHub Actions workflow downloads and calculates the market dataset on GitHub's server. It writes `data/market-data.json`. The phone/web app reads that same-repository JSON file, so opening or rescanning the app does not consume Marketstack-style monthly API credits.

Data retrieval uses the open-source `yfinance` Python library. yfinance is not an official Yahoo product and states that Yahoo Finance data is intended for personal use. Treat this build as a personal/research decision-support prototype, not a commercial market-data service or brokerage feed.

## Markets
Europe: 24 stocks; benchmark EXSA.DE (iShares STOXX Europe 600 UCITS ETF).
Canada: 24 TSX stocks; benchmark XIU.TO (iShares S&P/TSX 60 Index ETF).

## Generated metrics
Price, beta, aligned beta observations, correlation, annualized stock/benchmark volatility, volatility ratio, RSI(14), SMA20, SMA50, 20-day momentum, ATR(14), trailing dividend yield.

The app calculates Scout Grade, BUY ZONE / WAIT / AVOID, position sizes, entry zone, 3–4% target and ATR stop from the generated metrics.

## First-time GitHub setup
Upload the complete v3.0 folder structure to the existing repository. In particular, `.github/workflows/update-data.yml`, `scripts/update_data.py`, `requirements.txt`, and `data/market-data.json` are new.

Then:
1. Open the repository's **Actions** tab.
2. Choose **Update market data**.
3. Click **Run workflow** -> **Run workflow**.
4. Wait for the job to finish successfully.
5. It will commit a populated `data/market-data.json` back to the repository.
6. GitHub Pages will serve the updated dataset automatically.
7. Open EuroStock Scout and click **Reload latest GitHub data**.

The workflow is also scheduled for weekdays at 22:37 UTC. Scheduled GitHub Actions can run later than the exact cron time.

## Files
Root:
- index.html
- manifest.webmanifest
- sw.js
- icon-192.png
- icon-512.png
- README.md
- requirements.txt

Folders:
- `.github/workflows/update-data.yml`
- `scripts/update_data.py`
- `data/market-data.json`

## Morningstar
The app does not reproduce Morningstar's proprietary stock star rating. It retains a search button to open Morningstar research.

This is decision support, not individualized investment advice.
