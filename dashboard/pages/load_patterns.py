import altair as alt
import numpy as np
import streamlit as st
from pandas import DataFrame

from src.layouts import (
    render_page_header,
    render_footer_note,
    render_date_range_filter,
)
from src.filters import (
    get_region_options,
    get_season_options,
    get_substation_options,
    get_date_range_defaults,
)
from src.queries import (
    get_hourly_profile_by_season,
    get_hourly_profile_by_segment,
    get_hourly_region_usage,
)
from src.charts import (
    build_hourly_profile_by_season_chart,
    build_hourly_profile_by_segment_chart,
)


def _apply_substation_filter(df: DataFrame, substation_id: str | None) -> DataFrame:
    """
    If substation_id is provided and the DataFrame has a substation_id column,
    filter accordingly. Otherwise return df unchanged.
    """
    if df is None or df.empty:
        return df

    if substation_id is None:
        return df

    if "substation_id" not in df.columns:
        return df

    return df[df["substation_id"] == substation_id]


def _build_hourly_distribution_chart(hourly_df: DataFrame) -> alt.Chart:
    """
    Build a distribution view: mean and 90th percentile of avg_kw by hour_of_day.
    Uses obs_hour_local if available, else obs_hour_utc.
    """
    if hourly_df is None or hourly_df.empty:
        return alt.Chart().mark_text(text="No hourly data for distribution view").properties(height=200)

    if "avg_kw" not in hourly_df.columns:
        return alt.Chart().mark_text(text="Missing avg_kw column").properties(height=200)

    hour_col = "obs_hour_local" if "obs_hour_local" in hourly_df.columns else (
        "obs_hour_utc" if "obs_hour_utc" in hourly_df.columns else None
    )
    if hour_col is None:
        return alt.Chart().mark_text(text="Missing hour column").properties(height=200)

    # Aggregate: mean and 90th percentile
    grouped = (
        hourly_df
        .groupby(hour_col)["avg_kw"]
        .agg(
            mean_kw="mean",
            p90_kw=lambda s: float(np.quantile(s, 0.9)),
        )
        .reset_index()
    )

    if grouped.empty:
        return alt.Chart().mark_text(text="No data after aggregation").properties(height=200)

    # Base chart for mean
    base = alt.Chart(grouped).encode(
        x=alt.X(f"{hour_col}:Q", title="Hour of Day"),
    )

    mean_line = base.mark_line(point=True).encode(
        y=alt.Y("mean_kw:Q", title="Load (kW)"),
        tooltip=[
            alt.Tooltip(f"{hour_col}:Q", title="Hour"),
            alt.Tooltip("mean_kw:Q", title="Mean (kW)"),
            alt.Tooltip("p90_kw:Q", title="P90 (kW)"),
        ],
        color=alt.value("#1f77b4"),
    )

    p90_line = base.mark_line(strokeDash=[4, 4]).encode(
        y="p90_kw:Q",
        color=alt.value("#ff7f0e"),
    )

    chart = (mean_line + p90_line).properties(
        height=300,
        title="Hourly Load Distribution (Mean and 90th Percentile)",
    )

    return chart


def main() -> None:
    # ---- Header ----
    render_page_header(
        "Load Patterns",
        "Explore hourly shapes by season, segment, and hour-of-day statistics",
    )

    st.sidebar.markdown("### Filters")

    # ---- Region (required) ----
    region_options = get_region_options()
    if not region_options:
        st.error("No regions available.")
        return

    region_index = 0
    selected_region = st.sidebar.selectbox(
        "Region",
        region_options,
        index=region_index,
    )

    # ---- Season (optional) ----
    season_options = get_season_options()
    season_labels = ["All seasons"] + season_options
    season_index = 0
    selected_season_label = st.sidebar.selectbox(
        "Season (optional)",
        season_labels,
        index=season_index,
    )
    selected_season: str | None
    if selected_season_label == "All seasons":
        selected_season = None
    else:
        selected_season = selected_season_label

    # ---- Substation filter (optional) ----
    selected_substation: str | None = None
    substation_options = get_substation_options(selected_region)
    if substation_options:
        substation_labels = ["All substations"] + substation_options
        substation_index = 0
        selected_sub_label = st.sidebar.selectbox(
            "Substation (optional)",
            substation_labels,
            index=substation_index,
        )
        if selected_sub_label != "All substations":
            selected_substation = selected_sub_label

    # ---- View mode toggle (season vs segment emphasis) ----
    view_mode = st.sidebar.radio(
        "Primary view",
        ["Season profiles", "Segment profiles"],
        index=0,
    )

    # ---- Date range for distribution view ----
    default_start, default_end = get_date_range_defaults()
    st.sidebar.markdown("### Distribution Date Range")
    dist_start, dist_end = render_date_range_filter(default_start, default_end)

    # ---- Section: Hourly Profile by Season ----
    st.subheader("Hourly Profile by Season")

    season_profile_df = get_hourly_profile_by_season(
        region_id=selected_region,
        season=selected_season if view_mode == "Season profiles" else None,
    )
    season_profile_df = _apply_substation_filter(season_profile_df, selected_substation)

    season_chart = build_hourly_profile_by_season_chart(season_profile_df)
    st.altair_chart(season_chart, use_container_width=True)

    # ---- Section: Segment Comparison ----
    st.subheader("Segment Comparison (Weekday/Weekend by Season)")

    segment_df = get_hourly_profile_by_segment(
        region_id=selected_region,
        season=selected_season if view_mode == "Segment profiles" else None,
    )
    segment_df = _apply_substation_filter(segment_df, selected_substation)

    segment_chart = build_hourly_profile_by_segment_chart(segment_df)
    st.altair_chart(segment_chart, use_container_width=True)

    # ---- Section: Distribution View (Mean vs P90) ----
    st.subheader("Hourly Load Distribution (Mean vs 90th Percentile)")

    hourly_df = get_hourly_region_usage(
        region_id=selected_region,
        date_start=dist_start,
        date_end=dist_end,
    )
    hourly_df = _apply_substation_filter(hourly_df, selected_substation)

    distribution_chart = _build_hourly_distribution_chart(hourly_df)
    st.altair_chart(distribution_chart, use_container_width=True)

    # ---- Narrative / Footer ----
    render_footer_note(
        "This page focuses on recurring patterns in the 2016 dataset — "
        "seasonal shapes, weekday/weekend differences, and hourly variability. "
        "In a live system, the same views could be driven by refreshed Gold-layer tables."
    )


if __name__ == "__main__":
    main()
