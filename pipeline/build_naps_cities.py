"""
ANNUAL builder (NOT part of the weekly registry) for the city air-quality
dashboard — analogous to build_wait_times.py / build_geography.py.

Source: Environment and Climate Change Canada's National Air Pollution
Surveillance (NAPS) program — the **Annual Summaries** product, which publishes
per-station validated *annual and 12 monthly means* (so we never touch the raw
hourly files). Open Government Licence – Canada.

Per pollutant per year, ECCC posts one CSV with five averaging-basis blocks
(1HR / 8HR / 24HR / DMAX1HR / DAILYMEAN). We read the **1HR** block — the plain
mean concentration — and aggregate the stations of each major city.

Output (committed CSVs, re-run each spring when validated NAPS lands):
  data/environment/naps_city_annual.csv    city, pollutant, unit, year, value, n_stations
  data/environment/naps_city_monthly.csv   city, pollutant, unit, year, month, date, value

Run:  python -m pipeline.build_naps_cities
"""

import io
import csv
import re
import requests
import openpyxl
import pandas as pd
from datetime import date
from pipeline.config import DATA_DIR
from pipeline.metadata import save_metadata
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_UA = {"User-Agent": "Mozilla/5.0 (DataCan pipeline; +https://canadaobservatory.github.io)"}
_FILE = "https://data-donnees.az.ec.gc.ca/api/file?path="
_NAPS = ("/air/monitor/national-air-pollution-surveillance-naps-program/Data-Donnees")

START_YEAR = 2005   # AnnualSummaries (per-station means) begin here
# Continuous pollutants to chart: token in filename -> (display, units)
POLLUTANTS = {
    "PM25": ("PM2.5", "µg/m³"),
    "O3":   ("O3", "ppb"),
    "NO2":  ("NO2", "ppb"),
    "SO2":  ("SO2", "ppb"),
    "CO":   ("CO", "ppm"),
}

# Curated major cities (CMA-level). Each: display -> (province set, match substrings).
# Province-gated so e.g. Windsor (ON) doesn't catch "Grand Falls - Windsor" (NL).
# A city with no NAPS data simply won't appear in the output.
CANONICAL = [
    ("Toronto",            {"ON"}, ["toronto"]),
    ("Montréal",           {"QC"}, ["montréal", "montreal"]),
    ("Vancouver",          {"BC"}, ["vancouver"]),          # incl. "Metro Vancouver - *"
    ("Calgary",            {"AB"}, ["calgary"]),
    ("Edmonton",           {"AB"}, ["edmonton"]),
    ("Ottawa–Gatineau",    {"ON", "QC"}, ["ottawa", "gatineau"]),
    ("Winnipeg",           {"MB"}, ["winnipeg"]),
    ("Québec City",        {"QC"}, ["québec", "quebec"]),
    ("Hamilton",           {"ON"}, ["hamilton"]),
    ("Kitchener–Waterloo", {"ON"}, ["kitchener", "waterloo"]),
    ("London",             {"ON"}, ["london"]),
    ("Windsor",            {"ON"}, ["windsor"]),
    ("St. Catharines–Niagara", {"ON"}, ["catharines", "niagara"]),
    ("Sudbury",            {"ON"}, ["sudbury"]),
    ("Thunder Bay",        {"ON"}, ["thunder bay"]),
    ("Halifax",            {"NS"}, ["halifax", "dartmouth"]),
    ("Saint John",         {"NB"}, ["saint john"]),
    ("Fredericton",        {"NB"}, ["fredericton"]),
    ("Moncton",            {"NB"}, ["moncton"]),
    ("Charlottetown",      {"PE"}, ["charlottetown"]),
    ("St. John's",         {"NL"}, ["st. john's", "st john's", "mount pearl"]),
    ("Victoria",           {"BC"}, ["victoria"]),
    ("Kelowna",            {"BC"}, ["kelowna"]),
    ("Abbotsford",         {"BC"}, ["abbotsford"]),
    ("Regina",             {"SK"}, ["regina"]),
    ("Saskatoon",          {"SK"}, ["saskatoon"]),
    ("Sherbrooke",         {"QC"}, ["sherbrooke"]),
    ("Saguenay",           {"QC"}, ["saguenay", "jonquière", "chicoutimi"]),
    ("Trois-Rivières",     {"QC"}, ["trois-rivières", "trois-rivieres"]),
    ("Whitehorse",         {"YT"}, ["whitehorse"]),
    ("Yellowknife",        {"NT"}, ["yellowknife"]),
]


def _canon(city, pt):
    cl = str(city or "").lower()
    for display, provs, pats in CANONICAL:
        if pt in provs and any(p in cl for p in pats):
            return display
    return None


def _fnum(x):
    try:
        v = float(x)
        return v if v > -999 else None
    except (TypeError, ValueError):
        return None


def _parse_1hr_block(text):
    """Return (header_index_map, list-of-raw-rows) for the 1HR block, or (None, [])."""
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if re.search(r"\*{3,}\s*1HR\s*\*{3,}", l)]
    if not starts:
        return None, []
    h = starts[0] + 1
    ends = [i for i, l in enumerate(lines)
            if i > h and re.search(r"\*{3,}\s*(8HR|24HR|DMAX1HR|DAILYMEAN)\s*\*{3,}", l)]
    end = ends[0] if ends else len(lines)
    hdr = next(csv.reader([lines[h]]))
    ci = {n.strip(): i for i, n in enumerate(hdr)}
    if "City" not in ci or "Mean" not in ci or "P/T" not in ci:
        return None, []
    rows = [r for r in csv.reader(lines[h + 1:end]) if r and r[0].strip()]
    return ci, rows


def _parse_xlsx_1hr(content):
    """Pre-2016 years ship as .xlsx with one sheet per averaging basis. Read the
    '1hr' sheet -> (header_index_map, list-of-row-lists)."""
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    sheet = next((s for s in wb.sheetnames if s.lower() == "1hr"), None)
    if sheet is None:
        return None, []
    rows = list(wb[sheet].iter_rows(values_only=True))
    for i, r in enumerate(rows):
        cells = [str(c).strip() if c is not None else "" for c in r]
        if "City" in cells and "Mean" in cells and "P/T" in cells:
            ci = {n: j for j, n in enumerate(cells)}
            data = [list(rr) for rr in rows[i + 1:] if rr and rr[ci["City"]] is not None]
            return ci, data
    return None, []


def _rows_for(tok, year):
    """Fetch one pollutant-year's 1-hour station table, trying the modern CSV
    (2016+) then the older .xlsx. Returns (header_index_map, rows) or (None, [])."""
    base = (f"{_FILE}{_NAPS}/{year}/ContinuousData-DonneesContinu/"
            f"AnnualSummaries-SommairesAnnuels/{year}_Annual{tok}")
    r = requests.get(base + "_EN.csv", headers=_UA, timeout=60)
    if r.status_code == 200:
        return _parse_1hr_block(r.content.decode("utf-8-sig", errors="replace"))
    r = requests.get(base + ".xlsx", headers=_UA, timeout=90)
    if r.status_code == 200:
        return _parse_xlsx_1hr(r.content)
    return None, []


def build_naps_cities():
    end_year = date.today().year
    # accumulators: {(city, poll): {year: [means]}} and monthly {(city,poll,year,month):[vals]}
    ann = {}      # (city, poll) -> {year: [station means]}
    mon = {}      # (city, poll, year, monthnum) -> [station monthly means]
    units = {}

    for tok, (poll, unit) in POLLUTANTS.items():
        units[poll] = unit
        got_years = 0
        for year in range(START_YEAR, end_year + 1):
            try:
                ci, rows = _rows_for(tok, year)
            except Exception as e:
                logger.warning(f"  {poll} {year}: {e}")
                continue
            if ci is None:
                continue
            mean_i = ci["Mean"]
            month_idx = list(range(mean_i - 12, mean_i))   # 12 cols before Mean = Jan..Dec
            for r in rows:
                try:
                    pt = str(r[ci["P/T"]] or "").strip()
                    city = _canon(r[ci["City"]], pt)
                except (IndexError, KeyError):
                    continue
                if city is None:
                    continue
                m = _fnum(r[mean_i]) if mean_i < len(r) else None
                if m is not None:
                    ann.setdefault((city, poll), {}).setdefault(year, []).append(m)
                for mi, col in enumerate(month_idx, start=1):
                    v = _fnum(r[col]) if col < len(r) else None
                    if v is not None:
                        mon.setdefault((city, poll, year, mi), []).append(v)
            got_years += 1
        logger.info(f"  {poll}: read {got_years} years")

    # ---- annual frame ----
    a_rows = []
    for (city, poll), yd in ann.items():
        for year, vals in yd.items():
            a_rows.append({"city": city, "pollutant": poll, "unit": units[poll],
                           "year": year, "value": round(sum(vals) / len(vals), 2),
                           "n_stations": len(vals)})
    adf = pd.DataFrame(a_rows).sort_values(["pollutant", "city", "year"]).reset_index(drop=True)

    # ---- monthly frame ----
    m_rows = []
    for (city, poll, year, mi), vals in mon.items():
        m_rows.append({"city": city, "pollutant": poll, "unit": units[poll],
                       "year": year, "month": mi,
                       "date": f"{year}-{mi:02d}-01",
                       "value": round(sum(vals) / len(vals), 2)})
    mdf = pd.DataFrame(m_rows).sort_values(["pollutant", "city", "year", "month"]).reset_index(drop=True)

    if adf.empty:
        logger.error("NAPS city build produced no data")
        return None

    (DATA_DIR / "environment").mkdir(parents=True, exist_ok=True)
    a_out = DATA_DIR / "environment" / "naps_city_annual.csv"
    m_out = DATA_DIR / "environment" / "naps_city_monthly.csv"
    adf.to_csv(a_out, index=False)
    mdf.to_csv(m_out, index=False)
    for out, df in [(a_out, adf), (m_out, mdf)]:
        save_metadata(out, df=df, latest_observation_date=str(int(adf["year"].max())),
            source="Environment and Climate Change Canada",
            source_table="ECCC National Air Pollution Surveillance (NAPS) — Annual Summaries (1-hour basis)",
            frequency="annual", unit="µg/m³ (PM) / ppb (gases) / ppm (CO)",
            transformations=["1HR-block station means aggregated to major cities",
                             "annual mean + 12 monthly means, 2005–latest"])
    logger.info(f"  cities: {adf.city.nunique()} | annual rows {len(adf)} | monthly rows {len(mdf)}")
    logger.info(f"  saved -> {a_out.name}, {m_out.name}")
    return adf, mdf


if __name__ == "__main__":
    build_naps_cities()
