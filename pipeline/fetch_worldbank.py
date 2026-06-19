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
from pipeline.config import PEER_CODES, PEER_COUNTRIES, DATA_DIR
from pipeline.metadata import save_metadata
import logging

logger = logging.getLogger(__name__)

WB_BASE = "https://api.worldbank.org/v2"


def fetch_world_population():
    """Population of every country (World Bank SP.POP.TOTL, most recent year per
    country) for the "Canada isn't a small country" global-context chart.

    Unlike the peer-only generic fetcher, this keeps ALL countries — but first
    pulls the WB country metadata to drop the regional/income aggregates (region
    == 'Aggregates'; e.g. "World", "High income", "Sub-Saharan Africa"), which
    would otherwise dwarf every real country. `mrnev=1` returns each country's
    most-recent non-empty value.
    """
    logger.info("Fetching World Bank population for all countries...")
    try:
        meta = requests.get(f"{WB_BASE}/country",
                            params={"format": "json", "per_page": "400"},
                            timeout=60).json()
        real = {c["id"]: c["name"] for c in meta[1]
                if c.get("region", {}).get("value") != "Aggregates"}
        js = requests.get(f"{WB_BASE}/country/all/indicator/SP.POP.TOTL",
                          params={"format": "json", "per_page": "20000", "mrnev": "1"},
                          timeout=120).json()
    except Exception as e:
        logger.error(f"  Failed World Bank population fetch: {e}")
        return None

    if not isinstance(js, list) or len(js) < 2 or not js[1]:
        logger.warning("  World Bank returned no population data")
        return None

    seen, rows = set(), []
    for d in js[1]:
        code = d.get("countryiso3code")
        if code in real and d.get("value") is not None and code not in seen:
            seen.add(code)
            rows.append({"country_code": code, "country_name": real[code],
                         "year": int(d["date"]), "population": int(d["value"])})
    df = pd.DataFrame(rows)
    if df.empty or "CAN" not in set(df["country_code"]):
        logger.warning("  population data missing Canada or empty")
        return None
    df = df.sort_values("population", ascending=False).reset_index(drop=True)

    out_path = DATA_DIR / "population" / "worldbank_population.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="World Bank (World Development Indicators)",
        source_table="SP.POP.TOTL",
        frequency="annual", unit="people",
        transformations=["all countries (WB aggregates removed), most recent year each"])
    logger.info(f"  saved {len(df)} countries -> {out_path.name}")
    return df


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
