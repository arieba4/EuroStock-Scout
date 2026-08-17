# EuroStock Scout v2

A mobile-first Progressive Web App (PWA) for screening a curated European large-cap universe.

## What changed from v1
- Live daily market-data support through Twelve Data
- 48-stock European watchlist across Paris, Xetra, Amsterdam, Madrid, Milan, Brussels, Copenhagen and Stockholm
- Historical beta calculated locally against EXSA (iShares STOXX Europe 600 UCITS ETF) as a European-market proxy
- RSI(14), SMA20, SMA50, 20-session momentum and ATR(14)
- Explainable 0–100 ranking
- BUY ZONE / WAIT / AVOID classification
- €5,000 default position allocation across the best qualifying names
- 3.0%, 3.5% or 4.0% gross profit objective
- ATR-based stop/risk line
- Installable PWA shell and offline app UI
- Demo mode when no data key is available

## Live-data setup
1. Create a Twelve Data API key.
2. Host this folder over HTTPS (GitHub Pages, Netlify, Vercel, Cloudflare Pages, etc.).
3. Open the app and paste the key in Live data.
4. Select scan size and tap "Scan European stocks".
5. On iPhone Safari: Share -> Add to Home Screen.

For a public/production deployment, DO NOT expose a paid provider key in the browser. Proxy the Twelve Data calls through your own backend or serverless function.

## Important limitations
- EXSA is used as a practical European-market proxy for beta, not as the only possible definition of "European market beta."
- The stock universe is curated, not every listed European company.
- Technical indicators are backward-looking.
- Corporate-event/news gating is not enabled in this static build because that requires reliable entitlement to a news/earnings data feed and is best done server-side.
- Stops and targets can be skipped by market gaps.
- Currency allocation currently restricts the portfolio builder to instruments reported by the provider in EUR.
- API access, symbol entitlements and rate limits depend on the user's data-provider plan.

## Strategy weights
- Beta fit: 30%
- Trend: 25%
- RSI: 20%
- 20-day momentum: 15%
- ATR risk: 10%

This project is decision support, not individualized investment advice, and a 3–4% target is not guaranteed.
