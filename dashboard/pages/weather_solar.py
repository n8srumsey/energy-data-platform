from datetime import datetime, date, timedelta

import altair as alt
import pandas as pd
from pandas import DataFrame
import streamlit as st

from src.layouts import (
    render_page_header,
    render_footer_note,
    render_date_range_filter,
)
from src.filters import (
    get_region_options,
    get_season_options,
    get_date_range_defaults,
)
from src.queries import (
    get_temp_bin_load_stats,
    get_solar_impact_on_load,
    get_hourly_region_usage,
)
from src.charts import (
    build_temp_sensitivity_chart,
    build_solar_vs_load_scatter_chart,
)


def _build_overlay_timeseries_chart(hourly_df: DataFrame) -> alt.Chart:
    """
    Build a time-based overlay of load vs temperature/solar for a selected date range.

    Uses hourly_region_usage columns:
      - obs_date
      - obs_hour_local or obs_hour_utc
      - avg_kw (load)
      - temp_c
      - ghi_w_m2 (if available)

    Creates a combined time axis using obs_date + hour.
    """
    if hourly_df is None or hourly_df.empty:
        return alt.Chart().mark_text(text="No hourly data for overlay").properties(height=200)

    required_cols = ["obs_date", "avg_kw"]
    for col in required_cols:
        if col not in hourly_df.columns:
            return alt.Chart().mark_text(text="Missing required columns for overlay").properties(height=200)

    # Choose hour column
    hour_col = "obs_hour_local" if "obs_hour_local" in hourly_df.columns else (
        "obs_hour_utc" if "obs_hour_utc" in hourly_df.columns else None
    )
    if hour_col is None:
        return alt.Chart().mark_text(text="Missing hour column for overlay").properties(height=200)

    df = hourly_df.copy()

    # Build a synthetic timestamp column
    # obs_date may already be datetime64[ns]; if not, parse it.
    if not pd.api.types.is_datetime64_any_dtype(df["obs_date"]):
        df["obs_date"] = pd.to_datetime(df["obs_date"])

    df["timestamp"] = df["obs_date"] + pd.to_timedelta(df[hour_col].astype(int), unit="h")

    # We’ll build two vertically concatenated charts: load and temperature/solar
    base = alt.Chart(df).encode(
        x=alt.X("timestamp:T", title="Time"),
    )

    load_line = base.mark_line().encode(
        y=alt.Y("avg_kw:Q", title="Load (kW)"),
        tooltip=[
            alt.Tooltip("timestamp:T", title="Time"),
            alt.Tooltip("avg_kw:Q", title="Load (kW)"),
            alt.Tooltip("temp_c:Q", title="Temp (°C)", format=".1f",),
            alt.Tooltip("ghi_w_m2:Q", title="GHI (W/m²)", format=".0f",),
        ],
        color=alt.value("#1f77b4"),
    ).properties(
        height=200,
        title="Load Over Time",
    )

    # Temperature + optional solar
    temp_line = base.mark_line().encode(
        y=alt.Y("temp_c:Q", title="Temperature (°C)"),
        color=alt.value("#ff7f0e"),
    )

    # If GHI is present, add a secondary series; we’ll layer within the second panel
    if "ghi_w_m2" in df.columns:
        ghi_line = base.mark_line(strokeDash=[4, 4]).encode(
            y=alt.Y("ghi_w_m2:Q", title="GHI (W/m²)"),
            color=alt.value("#2ca02c"),
        )
        climate_chart = (temp_line + ghi_line).properties(
            height=200,
            title="Temperature and Solar Irradiance",
        )
    else:
        climate_chart = temp_line.properties(
            height=200,
            title="Temperature",
        )

    combined = alt.vconcat(load_line, climate_chart).resolve_scale(
        x="shared"
    )

    return combined


def _get_overlay_default_range() -> tuple[str, str]:
    """
    Pick a relatively short default range for the overlay (e.g., one representative week)
    based on the full dataset range, so the chart is readable.
    """
    full_start_str, full_end_str = get_date_range_defaults()
    try:
        full_start = date.fromisoformat(full_start_str)
        full_end = date.fromisoformat(full_end_str)
    except ValueError:
        # Fallback to a fixed week if parsing fails
        return "2016-06-01", "2016-06-07"

    # Choose a 7-day window centered-ish within the full range
    mid = full_start + (full_end - full_start) / 2
    mid = date.fromtimestamp(date.fromtimestamp(mid))  # ensure it's a date object

    start = mid - timedelta(days=3)
    end = mid + timedelta(days=3)

    # Clamp to full range
    if start < full_start:
        start = full_start
    if end > full_end:
        end = full_end

    return start.isoformat(), end.isoformat()


def main() -> None:
    # ---- Header ----
    render_page_header(
        "Weather & Solar Impact",
        "How temperature and solar irradiance relate to load in 2016",
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

    # ---- Section: Temperature Sensitivity ----
    st.subheader("Temperature Sensitivity")

    temp_df = get_temp_bin_load_stats(
        region_id=selected_region
    )
    temp_chart = build_temp_sensitivity_chart(temp_df)
    st.altair_chart(temp_chart, use_container_width=True)

    st.caption(
        "This chart shows how average load varies across temperature bins, "
        "highlighting heating/cooling behavior for the selected region and season."
    )

    # ---- Section: Solar vs Load Scatter ----
    st.subheader("Solar vs Load")

    solar_df = get_solar_impact_on_load()
    solar_chart = build_solar_vs_load_scatter_chart(solar_df)
    st.altair_chart(solar_chart, use_container_width=True)

    st.caption(
        "Each point represents aggregated conditions for a set of hours: "
        "solar irradiance on the x-axis and load on the y-axis, optionally colored by season."
    )

    # ---- Section: Time-based Overlay Example ----
    st.subheader("Time-based Overlay of Load, Temperature, and Solar")

    st.markdown(
        "Use the date range below to explore a specific period. "
        "The top panel shows load, while the bottom panel shows temperature and "
        "solar irradiance (where available)."
    )

    full_start, full_end = get_date_range_defaults()
    default_overlay_start, default_overlay_end = _get_overlay_default_range()

    # Reuse the date-range filter UI in the sidebar but scoped to overlay
    st.sidebar.markdown("### Overlay Date Range")
    overlay_start_str, overlay_end_str = render_date_range_filter(
        default_start=default_overlay_start,
        default_end=default_overlay_end,
    )

    overlay_hourly_df = get_hourly_region_usage(
        region_id=selected_region,
        date_start=overlay_start_str,
        date_end=overlay_end_str,
    )

    overlay_chart = _build_overlay_timeseries_chart(overlay_hourly_df)
    st.altair_chart(overlay_chart, use_container_width=True)

    # ---- Footer / Narrative ----
    render_footer_note(
        "All insights on this page are derived from the static 2016 dataset. "
        "In a production system, the same transformations and visual patterns "
        "could be applied to live data to monitor real-time weather and solar impacts on load."
    )


if __name__ == "__main__":
    main()
