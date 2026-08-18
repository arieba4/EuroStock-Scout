# EuroStock Scout v3.3

v3.2 expands the daily universe to **110 stocks**:
- 60 major European stocks listed in EUR
- 50 major Canadian/TSX stocks

## New in v3.3: action-first rankings + All Markets Top 5
The Suggestions tab ranks the five strongest actionable setups for the selected market. A new **Suggestions · Top 5 All Markets** tab combines the full Europe + Canada universe with no market quota. BUY ZONE candidates rank ahead of WAIT, which rank ahead of AVOID; ties are resolved with a new Opportunity Score.

This is **not a promise or forecast**. The Near-term score rewards:
- bullish price/SMA20/SMA50 structure;
- RSI in a constructive range rather than overbought;
- positive 20-day momentum;
- beta close to the user's selected target;
- manageable ATR volatility;
- non-negative benchmark correlation.

A stock can appear in the Top 5 as `WAIT` if the setup is strong but the entry is stretched.

The stricter `Trade plan` remains unchanged: capital is allocated only to `BUY ZONE` stocks.

## After uploading v3.2
Replace the existing v3.0 files with the v3.2 files, including `scripts/update_data.py`.

Then run:
**Actions → Update market data → Run workflow**

After the workflow succeeds, reload the app and open **Suggestions · Top 5**.

## v3.2 decision-layer changes
- Preferred beta: 0.7 to 1.3 in 0.1 increments.
- Minimum reward/risk: Poor (>=0.75x), Neutral (>=1.25x), High (>=1.75x).
- BUY ZONE now respects the selected minimum reward/risk.
- Plain-language labels for reward/risk, relative volatility and correlation.
- Top 5 ranking rewards better reward/risk and penalizes unusually high relative volatility.
- Raw diagnostics remain visible.
