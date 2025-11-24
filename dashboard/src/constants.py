APP_TITLE: str = "Energy Analytics - 2016 Load & Weather"

OVERVIEW_PAGE_TITLE: str = "Overview"
LOAD_PATTERNS_PAGE_TITLE: str = "Load Patterns"
WEATHER_SOLAR_PAGE_TITLE: str = "Weather & Solar Impact"
EVENTS_RELIABILITY_PAGE_TITLE: str = "Events & Reliability"
ABOUT_PAGE_TITLE: str = "Data & Pipeline"

DEFAULT_REGION_ID: str = "SF_REGION_1"  # adjust to a real region_id
DEFAULT_SEASON: str = "summer"

DATE_FORMAT: str = "%Y-%m-%d"

# Column names used across charts (helps centralize rename logic if needed)
COL_DATE: str = "date"
COL_REGION_ID: str = "region_id"
COL_SUBSTATION_ID: str = "substation_id"
COL_HOUR_OF_DAY: str = "hour_of_day"
COL_AVG_KW: str = "avg_kw"
COL_TEMP_BIN: str = "temp_bin"
COL_GHI: str = "avg_ghi_w_m2"

# Friendly labels for display
SEASON_LABELS: dict = {
    "winter": "Winter",
    "spring": "Spring",
    "summer": "Summer",
    "fall": "Fall",
}
