# EuroStock Scout v3.1

v3.1 expands the daily universe to **110 stocks**:
- 60 major European stocks listed in EUR
- 50 major Canadian/TSX stocks

## New: Suggestions · Top 5
A third tab ranks the five strongest near-term technical setups for the selected market.

This is **not a promise or forecast**. The Near-term score rewards:
- bullish price/SMA20/SMA50 structure;
- RSI in a constructive range rather than overbought;
- positive 20-day momentum;
- beta close to the user's selected target;
- manageable ATR volatility;
- non-negative benchmark correlation.

A stock can appear in the Top 5 as `WAIT` if the setup is strong but the entry is stretched.

The stricter `Trade plan` remains unchanged: capital is allocated only to `BUY ZONE` stocks.

## After uploading v3.1
Replace the existing v3.0 files with the v3.1 files, including `scripts/update_data.py`.

Then run:
**Actions → Update market data → Run workflow**

After the workflow succeeds, reload the app and open **Suggestions · Top 5**.
