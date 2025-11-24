# src/filters.py

from typing import Any

from pandas import DataFrame
import streamlit as st

from .queries import (
    get_region_dim,
    get_season_dim,
    get_date_dim,
)


@st.cache_data(show_spinner=False)
def get_region_options() -> list[str]:
    """
    Return a sorted list of region_ids for use in a selectbox.
    """
    dim_region: DataFrame = get_region_dim()

    if "region_id" not in dim_region.columns:
        return []

    region_ids = (
        dim_region["region_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    region_ids.sort()
    return region_ids


@st.cache_data(show_spinner=False)
def get_substation_options(region_id: str | None) -> list[str]:
    """
    Return a sorted list of substation_ids, optionally filtered by region_id.
    """
    dim_region: DataFrame = get_region_dim()

    if "substation_id" not in dim_region.columns:
        return []

    df = dim_region
    if region_id is not None and "region_id" in dim_region.columns:
        df = df[df["region_id"] == region_id]

    substation_ids = (
        df["substation_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    substation_ids.sort()
    return substation_ids


@st.cache_data(show_spinner=False)
def get_season_options() -> list[str]:
    """
    Return the list of available seasons (e.g., 'winter', 'spring', 'summer', 'fall').
    """
    dim_season: DataFrame = get_season_dim()

    # Prefer a simple "season" column if present.
    if "season" in dim_season.columns:
        seasons = (
            dim_season["season"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    else:
        # Fallback: take any column that looks like a season label
        seasons = []
        for col in dim_season.columns:
            if "season" in str(col).lower():
                seasons = (
                    dim_season[col]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
                break

    seasons.sort()
    return seasons


@st.cache_data(show_spinner=False)
def get_date_range_defaults() -> tuple[str, str]:
    """
    Return a (start_date, end_date) tuple representing the full coverage
    of the dataset (e.g., '2016-01-01', '2016-12-31').
    """
    dim_date: DataFrame = get_date_dim()

    if "date" not in dim_date.columns or dim_date.empty:
        # Sensible fallback; you can override in code if needed.
        return ("2016-01-01", "2016-12-31")

    # Ensure it's treated as a datetime-like for min/max.
    date_series = dim_date["date_key"]
    
    # If it's not already datetime, pandas will try to parse it.
    date_series = date_series.astype("datetime64[ns]")

    start_date = date_series.min()
    end_date = date_series.max()

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    return (start_str, end_str)


def build_region_label_map(dim_region_df: DataFrame) -> dict:
    """
    Build a mapping from region_id to human-readable label, based on dim_region_substation.

    Heuristics:
      - If a 'region_name' column exists, use "region_name".
      - Else if 'city' exists, use "region_id - city".
      - Else fall back to just "region_id".
    """
    label_map: dict[str, str] = {}

    if "region_id" not in dim_region_df.columns:
        return label_map

    # Drop duplicates to avoid overwriting labels unnecessarily
    unique_regions = dim_region_df.drop_duplicates(subset=["region_id"])

    for _, row in unique_regions.iterrows():
        region_id_value = str(row["region_id"])

        label: str
        if "region_name" in dim_region_df.columns and not isinstance(row.get("region_name"), float):
            region_name = str(row["region_name"])
            label = region_name
        elif "city" in dim_region_df.columns and not isinstance(row.get("city"), float):
            city = str(row["city"])
            label = f"{region_id_value} – {city}"
        else:
            label = region_id_value

        label_map[region_id_value] = label

    return label_map


def build_season_label_map(dim_season_df: DataFrame) -> dict:
    """
    Build a mapping from season code to human-readable label.

    Heuristics:
      - If a 'season_label' column exists, map 'season' -> 'season_label'.
      - Else use 'season' and title-case it.
    """
    label_map: dict[str, str] = {}

    if "season" not in dim_season_df.columns:
        return label_map

    # Use a single row per season
    unique_seasons = dim_season_df.drop_duplicates(subset=["season"])

    has_season_label = "season_label" in dim_season_df.columns

    for _, row in unique_seasons.iterrows():
        season_code = str(row["season"])

        if has_season_label and not isinstance(row.get("season_label"), float):
            season_label = str(row["season_label"])
        else:
            season_label = season_code.title()

        label_map[season_code] = season_label

    return label_map
