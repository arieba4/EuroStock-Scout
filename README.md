# EuroStock Scout v2.5

## Fix in v2.5
v2.4 successfully downloaded Marketstack EOD prices but could fail during beta alignment.

v2.5 calculates beta directly from daily returns:
- each stock's daily return series is calculated by trading date;
- the market benchmark is the equal-weight average return of the successfully downloaded stocks for each trading session;
- each stock is aligned directly to that daily market-return series;
- beta requires at least 30 aligned sessions;
- the app shows how many aligned sessions the benchmark contains.

All v2.4 response parsing and fallback logic remains.

## Features
Europe / Canada, Marketstack EOD, €5,000 / C$5,000 portfolio, beta target near 1, RSI, SMA20, SMA50, momentum, ATR, Scout Grade, BUY ZONE / WAIT / AVOID, 3–4% target, entry/stop, dividends when available, Morningstar research links and 24-hour caching.

## Install
Replace the same six files in your existing GitHub repository and commit them. Confirm the heading says v2.5 before testing.

This is a decision-support prototype, not individualized investment advice.
