"""
Fetch indicators from the World Bank API (World Development Indicators).
Generic, registry-driven: one function handles any WB indicator code.

The World Bank API is a clean, stable JSON endpoint that uses ISO-3 country
codes (matching our PEER_CODES) and is openly licensed (CC-BY 4.0). It is the
tidiest source for a few series that OECD only exposes awkwardly — e.g. gross
fixed capital formation as % of GDP, and military expenditure as % of GDP
(which the WB sources from SIPRI and covers for all 17 peers, not just NATO).
"""

import requests
import pandas as pd
from pipeline.config import PEER_CODES, PEER_COUNTRIES
from pipeline.metadata import save_metadata
import logging

logger = logging.getLogger(__name__)

WB_BASE = "https://api.worldbank.org/v2"


def fetch_worldbank_indicator(ind):
    """Generic World Bank fetch driven by an Indicator (source='worldbank').

    Emits the same [country_code, country_name, year, <value_col>] shape as the
    OECD fetcher, so the chart builders work unchanged.
    """
    logger.info(f"World Bank indicator: {ind.id} ({ind.title})")
    codes = ";".join(PEER_CODES)
    url = f"{WB_BASE}/country/{codes}/indicator/{ind.wb_indicator}"
    try:
        r = requests.get(url, params={"format": "json", "per_page": "20000",
                                      "date": f"{ind.start_period}:2026"}, timeout=120)
        r.raise_for_status()
        js = r.json()
    except Exception as e:
        logger.error(f"  Failed World Bank fetch {ind.wb_indicator}: {e}")
        return None

    if not isinstance(js, list) or len(js) < 2 or not js[1]:
        logger.warning(f"  {ind.id}: World Bank returned no data")
        return None

    rows = [{"country_code": d["countryiso3code"], "year": int(d["date"]),
             ind.value_col: d["value"]}
            for d in js[1] if d.get("value") is not None]
    df = pd.DataFrame(rows)
    if df.empty:
        return None

    df = df[df["country_code"].isin(PEER_CODES)].copy()
    df["country_name"] = df["country_code"].map(PEER_COUNTRIES)
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)
    if ind.transform:
        df = ind.transform(df)
    df = df[["country_code", "country_name", "year", ind.value_col]]

    out_path = ind.out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="World Bank (World Development Indicators)",
        source_table=ind.source_table,
        frequency=ind.frequency, unit=ind.unit,
        transformations=[f"World Bank indicator {ind.wb_indicator}, filtered to 17 OECD peers"])
    logger.info(f"  saved {len(df)} rows -> {out_path.name}")
    return df
