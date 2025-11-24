from pandas import DataFrame
import streamlit as st

from .data import run_query


@st.cache_data(show_spinner=False)
def get_region_dim() -> DataFrame:
    """
    Return the full dim_region_substation table, or a subset of columns
    used for filters and labels.
    """
    sql = """
        SELECT *
        FROM dim_region_substation
        ORDER BY "region_id", "substation_id"
    """
    return run_query(sql)


@st.cache_data(show_spinner=False)
def get_season_dim() -> DataFrame:
    """
    Return the dim_month_season table, or just distinct season labels.
    """
    sql = """
        SELECT *
        FROM dim_month_season
        ORDER BY "season"
    """
    return run_query(sql)


@st.cache_data(show_spinner=False)
def get_date_dim() -> DataFrame:
    """
    Return the dim_date table for date-related filters and labeling.
    """
    sql = """
        SELECT *
        FROM dim_date
        ORDER BY "date_key"
    """
    return run_query(sql)


def get_daily_region_usage(
    region_id: str | None,
    date_start: str | None,
    date_end: str | None,
) -> DataFrame:
    """
    Query daily_region_usage for a given region and optional date range.
    date_* strings are expected to be in ISO format (YYYY-MM-DD).
    """
    sql = """
        SELECT *
        FROM daily_region_usage
        WHERE 1 = 1
    """
    params: dict[str, object] = {}

    if region_id is not None:
        sql += ' AND "region_id" = %(region_id)s'
        params["region_id"] = region_id

    if date_start is not None:
        sql += ' AND "obs_date" >= %(date_start)s'
        params["date_start"] = date_start

    if date_end is not None:
        sql += ' AND "obs_date" <= %(date_end)s'
        params["date_end"] = date_end

    sql += ' ORDER BY "obs_date", "region_id"'

    return run_query(sql, params if params else None)


def get_hourly_region_usage(
    region_id: str | None,
    date_start: str | None,
    date_end: str | None,
) -> DataFrame:
    """
    Query hourly_region_usage for detailed time series analysis.
    Filters using obs_date, since this table does not contain a timestamp column.
    """
    sql = """
        SELECT *
        FROM hourly_region_usage
        WHERE 1 = 1
    """
    params: dict[str, object] = {}

    if region_id is not None:
        sql += ' AND "region_id" = %(region_id)s'
        params["region_id"] = region_id

    if date_start is not None:
        sql += ' AND "obs_date" >= %(date_start)s'
        params["date_start"] = date_start

    if date_end is not None:
        sql += ' AND "obs_date" <= %(date_end)s'
        params["date_end"] = date_end

    sql += ' ORDER BY "obs_date", "obs_hour_utc"'

    return run_query(sql, params if params else None)


def get_hourly_profile_by_season(
    region_id: str | None,
    season: str | None,
) -> DataFrame:
    """
    Query hourly_load_profile_by_season for a given region and optional season.
    Returns 24-row profiles (one per hour_of_day) possibly grouped by season.
    """
    sql = """
        SELECT *
        FROM hourly_load_profile_by_season
        WHERE 1 = 1
    """
    params: dict[str, object] = {}

    if region_id is not None:
        sql += ' AND "region_id" = %(region_id)s'
        params["region_id"] = region_id

    if season is not None:
        sql += ' AND "season" = %(season)s'
        params["season"] = season

    sql += ' ORDER BY "season", "hour_of_day"'

    return run_query(sql, params if params else None)


def get_hourly_profile_by_segment(
    region_id: str | None,
    season: str | None,
) -> DataFrame:
    """
    Query hourly_load_profile_by_segment (e.g., fall_weekday, fall_weekend)
    for the selected region and optional season.
    """
    sql = """
        SELECT *
        FROM hourly_load_profile_by_segment
        WHERE 1 = 1
    """
    params: dict[str, object] = {}

    if region_id is not None:
        sql += ' AND "region_id" = %(region_id)s'
        params["region_id"] = region_id

    if season is not None:
        sql += ' AND "segment" LIKE %(season)s'
        params["season"] = season

    sql += ' ORDER BY "segment", "hour_of_day"'

    return run_query(sql, params if params else None)


def get_temp_bin_load_stats(
    region_id: str | None,
) -> DataFrame:
    """
    Query temp_bin_load_stats for temperature sensitivity analysis.
    """
    sql = """
        SELECT *
        FROM temp_bin_load_stats
        WHERE 1 = 1
    """
    params: dict[str, object] = {}

    if region_id is not None:
        sql += ' AND "region_id" = %(region_id)s'
        params["region_id"] = region_id

    sql += ' ORDER BY "temp_bin"'

    return run_query(sql, params if params else None)


def get_solar_impact_on_load() -> DataFrame:
    """
    Query solar_impact_on_load, returning joined solar and load metrics
    suitable for scatter plots and trend analysis.
    """
    sql = """
        SELECT *
        FROM solar_impact_on_load
    """
    return run_query(sql, None)


def get_data_coverage_summary(
    region_id: str | None,
    date_start: str | None,
    date_end: str | None,
) -> DataFrame:
    """
    Query data_coverage_summary to assess completeness across time and station/region.
    """
    sql = """
        SELECT *
        FROM data_coverage_summary
        WHERE 1 = 1
    """
    params: dict[str, object] = {}

    if region_id is not None:
        sql += ' AND "region_id" = %(region_id)s'
        params["region_id"] = region_id

    if date_start is not None:
        sql += ' AND "date" >= %(date_start)s'
        params["date_start"] = date_start

    if date_end is not None:
        sql += ' AND "date" <= %(date_end)s'
        params["date_end"] = date_end

    sql += ' ORDER BY "date", "region_id"'

    return run_query(sql, params if params else None)


def get_extreme_event_days(
    region_id: str | None,
    date_start: str | None,
    date_end: str | None,
) -> DataFrame:
    """
    Query extreme_event_days to retrieve flagged anomalous days in the dataset.
    """
    sql = """
        SELECT *
        FROM extreme_event_days
        WHERE 1 = 1
    """
    params: dict[str, object] = {}

    if region_id is not None:
        sql += ' AND "region_id" = %(region_id)s'
        params["region_id"] = region_id

    if date_start is not None:
        sql += ' AND "date" >= %(date_start)s'
        params["date_start"] = date_start

    if date_end is not None:
        sql += ' AND "date" <= %(date_end)s'
        params["date_end"] = date_end

    sql += ' ORDER BY "date", "region_id"'

    return run_query(sql, params if params else None)
