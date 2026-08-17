# EuroStock Scout v2.4

## Fix in v2.4
Marketstack can return EOD results either as an array or wrapped inside an object such as `data.eod`. v2.3 assumed `data` was always an array, which caused:

`(d.data || []).filter is not a function`

v2.4 normalizes multiple response shapes before processing them. It also:
- tries the exchange-specific EOD endpoint first;
- falls back to the generic EOD endpoint using the resolved Marketstack symbol;
- normalizes dividend response shapes the same way;
- preserves ticker mappings and 24-hour scan caching;
- keeps separate Europe and Canada modes;
- keeps Scout Grade, dividends, Morningstar research links, beta, RSI, trend, entry, target and stop calculations.

## Install
Replace the same six files in your existing GitHub repository, commit, and wait for GitHub Pages to redeploy.

If the browser still shows v2.3, hard refresh or clear the site's service-worker/cache data.

Start with:
1. Europe
2. Quick / 8 stocks
3. Test API connection

This is a decision-support prototype, not individualized investment advice.
