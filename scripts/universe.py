"""Broad Europe/Canada universe construction for EuroStock Scout.

The updater combines liquid constituents from major national indices.  Remote
tables are deliberately best-effort: when a source changes, the last generated
dataset remains usable and the curated core universe in update_data.py keeps
the workflow operational.
"""

from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO
import re
from typing import Iterable
from urllib.request import Request, urlopen

import pandas as pd


@dataclass(frozen=True)
class IndexSource:
    market: str
    url: str
    suffix: str = ""
    symbol_columns: tuple[str, ...] = ("Ticker", "Ticker symbol", "Symbol")
    name_columns: tuple[str, ...] = ("Company", "Company name", "Constituent")


# Together these indices normally yield roughly 450-550 unique securities.
SOURCES = (
    IndexSource("Europe", "https://en.wikipedia.org/wiki/CAC_40", ".PA"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/CAC_Next_20", ".PA"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/DAX", ".DE"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/MDAX", ".DE"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/AEX_index", ".AS"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/AMX_index", ".AS"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/BEL_20", ".BR"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/IBEX_35", ".MC"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/FTSE_MIB", ".MI"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/Swiss_Market_Index", ".SW"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/OMX_Stockholm_30", ".ST"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/OMX_Helsinki_25", ".HE"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/OBX_Index", ".OL"),
    IndexSource("Europe", "https://en.wikipedia.org/wiki/OMX_Copenhagen_25", ".CO"),
    IndexSource("Canada", "https://en.wikipedia.org/wiki/S%26P/TSX_Composite_Index", ".TO"),
)


def _flat(value: object) -> str:
    if isinstance(value, tuple):
        return " ".join(str(x) for x in value if "Unnamed" not in str(x)).strip()
    return str(value).strip()


def _find_column(columns: Iterable[object], candidates: tuple[str, ...]) -> object | None:
    normalized = {re.sub(r"\s+", " ", _flat(c)).lower(): c for c in columns}
    for candidate in candidates:
        key = candidate.lower()
        for label, original in normalized.items():
            if label == key or key in label:
                return original
    return None


def _ticker(raw: object, suffix: str) -> str | None:
    text = re.sub(r"\[[^]]*]", "", str(raw)).strip().upper()
    text = text.replace(" ", "-")
    if not text or text in {"NAN", "NONE", "—", "-"}:
        return None
    # Wikipedia sometimes includes exchange prefixes or footnotes.
    text = text.split(":")[-1]
    text = re.sub(r"[^A-Z0-9.\-]", "", text)
    if not text:
        return None
    if suffix and not text.endswith(suffix):
        text += suffix
    return text


def fetch_source(source: IndexSource) -> list[tuple[str, str]]:
    request = Request(source.url, headers={"User-Agent": "EuroStock-Scout/3.4 (GitHub Actions; research screener)"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
    for table in pd.read_html(StringIO(html)):
        symbol_col = _find_column(table.columns, source.symbol_columns)
        if symbol_col is None:
            continue
        name_col = _find_column(table.columns, source.name_columns)
        rows: list[tuple[str, str]] = []
        for _, row in table.iterrows():
            ticker = _ticker(row[symbol_col], source.suffix)
            if ticker:
                name = str(row[name_col]).strip() if name_col is not None else ticker
                rows.append((name, ticker))
        if len(rows) >= 10:
            return rows
    raise ValueError("no constituent table found")


def currency_for_ticker(ticker: str, market: str) -> str:
    if market == "Canada":
        return "CAD"
    return {
        ".L": "GBP", ".SW": "CHF", ".ST": "SEK", ".HE": "EUR",
        ".OL": "NOK", ".CO": "DKK",
    }.get(next((s for s in (".L", ".SW", ".ST", ".HE", ".OL", ".CO") if ticker.endswith(s)), ""), "EUR")


def broad_universe(core: dict[str, list[tuple[str, str]]]) -> tuple[dict[str, list[tuple[str, str, str]]], list[str]]:
    gathered = {market: list(rows) for market, rows in core.items()}
    warnings: list[str] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        jobs = {pool.submit(fetch_source, source): source for source in SOURCES}
        completed: dict[IndexSource, list[tuple[str, str]]] = {}
        for job in as_completed(jobs):
            source = jobs[job]
            try:
                completed[source] = job.result()
            except Exception as exc:
                warnings.append(f"{source.url}: {exc}")
    # Apply results in source order so the 360-name Europe cap is stable.
    for source in SOURCES:
        gathered.setdefault(source.market, []).extend(completed.get(source, []))

    result: dict[str, list[tuple[str, str, str]]] = {}
    for market, rows in gathered.items():
        unique: dict[str, str] = {}
        for name, ticker in rows:
            unique.setdefault(ticker, name)
        # Keep workflow duration predictable while still screening roughly
        # 500-600 stocks in total. Core names retain first priority.
        limit = 360 if market == "Europe" else 220
        result[market] = [(name, ticker, currency_for_ticker(ticker, market)) for ticker, name in list(unique.items())[:limit]]
    return result, warnings
