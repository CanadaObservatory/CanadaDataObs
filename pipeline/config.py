"""
Central configuration for DataCan data pipeline.
Defines peer groups, data source IDs, and shared constants.
"""

from pathlib import Path
from datetime import date

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Date stamp for chart annotations
DATA_DATE = date.today().isoformat()

# --- OECD Peer Group ---
# Broader than G7: includes all comparable advanced economies

PEER_COUNTRIES = {
    # G7
    "CAN": "Canada",
    "USA": "United States",
    "GBR": "United Kingdom",
    "DEU": "Germany",
    "FRA": "France",
    "ITA": "Italy",
    "JPN": "Japan",
    # Extended peers
    "AUS": "Australia",
    "KOR": "South Korea",
    "NLD": "Netherlands",
    "SWE": "Sweden",
    "CHE": "Switzerland",
    "NOR": "Norway",
    "DNK": "Denmark",
    "FIN": "Finland",
    "ISR": "Israel",
    "AUT": "Austria",
    "BEL": "Belgium",
    "IRL": "Ireland",
    "NZL": "New Zealand",
}

PEER_CODES = list(PEER_COUNTRIES.keys())

# Country to highlight in charts
HIGHLIGHT_COUNTRY = "CAN"

# --- Statistics Canada Table IDs ---
STATCAN_TABLES = {
    "population_quarterly": "17-10-0009-01",  # Population estimates, quarterly
    "population_components": "17-10-0014-01",  # Components of population growth
    "cpi": "18-10-0004-01",  # Consumer Price Index, monthly
}

# --- OECD Dataset IDs ---
OECD_DATASETS = {
    "rd_expenditure": {
        "agency": "OECD",
        "id": "MSTI_PUB",  # Main Science and Technology Indicators
        "description": "Gross domestic expenditure on R&D as % of GDP",
    },
    "gdp_per_capita": {
        "agency": "OECD",
        "id": "SNA_TABLE1",
        "description": "GDP per capita, current prices, PPP",
    },
}

# --- OECD Rate Limiting ---
OECD_MAX_REQUESTS_PER_HOUR = 60
OECD_REQUEST_DELAY_SECONDS = 2  # Conservative delay between requests

# --- Chart Styling ---
CANADA_COLOR = "#d62728"  # Red for Canada
PEER_COLOR = "#7f7f7f"    # Grey for peers
OECD_AVG_COLOR = "#1f77b4"  # Blue for OECD average
HIGHLIGHT_WIDTH = 3
PEER_WIDTH = 1.5
