from datetime import date

import altair as alt
import streamlit as st
from pandas import DataFrame

from src.layouts import (
    render_page_header,
    render_kpi_row,
    render_overview_filters,
    render_footer_note,
)
from src.filters import (
    get_date_range_defaults,
    get_substation_options,
)
from src.queries import (
    get_daily_region_usage,
    get_hourly_region_usage,
    get_hourly_profile_by_season,
)
from src.charts import (
    build_daily_load_trend_chart,
    build_hourly_profile_by_season_chart,
)


def _compute_kpis(daily_df: DataFrame, hourly_df: DataFrame) -> list[dict]:
    """
    Compute KPI values from daily and hourly data.

    - Average daily load (from daily avg_kw if available)
    - Peak hourly load (from hourly max_kw or avg_kw)
    - Total energy (MWh) (from daily total columns or hourly_kwh)
    - Number of valid days (from daily date count)
    """
    # Defaults
    avg_daily_str = "–"
    peak_value_str = "–"
    peak_date_str = None
    total_mwh_str = "–"
    valid_days_str = "–"

    # Average daily load + total energy + valid days from daily_df
    if daily_df is not None and not daily_df.empty:
        if "avg_kw" in daily_df.columns:
            avg_daily = float(daily_df["avg_kw"].mean())
            avg_daily_str = f"{avg_daily:.1f} kW"

        # Total energy: prefer pre-aggregated daily energy if present
        total_kwh = None
        for candidate in ["total_daily_kwh", "total_kwh", "hourly_kwh"]:
            if candidate in daily_df.columns:
                total_kwh = float(daily_df[candidate].sum())
                break

        # If daily table doesn’t have energy, try hourly_kwh in hourly_df
        if total_kwh is None and hourly_df is not None and not hourly_df.empty:
            if "hourly_kwh" in hourly_df.columns:
                total_kwh = float(hourly_df["hourly_kwh"].sum())

        if total_kwh is not None:
            total_mwh_str = f"{total_kwh / 1000.0:.1f}"

        if "date" in daily_df.columns:
            valid_days = int(daily_df["date"].nunique())
            valid_days_str = str(valid_days)

    # Peak hourly load from hourly_df
    if hourly_df is not None and not hourly_df.empty:
        # Prefer max_kw, fallback to avg_kw
        load_col = None
        for candidate in ["max_kw", "avg_kw"]:
            if candidate in hourly_df.columns:
                load_col = candidate
                break

        if load_col is not None:
            peak_row = hourly_df.sort_values(load_col, ascending=False).iloc[0]
            peak_value = float(peak_row[load_col])
            peak_value_str = f"{peak_value:.1f} kW"

            # Construct a date string if obs_date exists
            if "obs_date" in hourly_df.columns:
                peak_date_val = peak_row["obs_date"]
                # obs_date is likely a datetime64; convert to date then isoformat
                if isinstance(peak_date_val, (date,)):
                    peak_date_str = peak_date_val.isoformat()
                else:
                    try:
                        peak_date_str = str(peak_date_val)[:10]
                    except Exception:
                        peak_date_str = None

    kpis = [
        {"label": "Average Daily Load", "value": avg_daily_str},
        {"label": "Peak Hourly Load", "value": peak_value_str, "delta": peak_date_str},
        {"label": "Total Energy (MWh)", "value": total_mwh_str},
        {"label": "Valid Days", "value": valid_days_str},
    ]

    return kpis


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


def _build_representative_day_options(daily_df: DataFrame) -> dict:
    """
    Compute representative day candidates from daily_df.

    Returns a dict with keys:
      - "peak_day"
      - "typical_day"
    Values are ISO date strings or None.
    """
    result: dict[str, str | None] = {
        "peak_day": None,
        "typical_day": None,
    }

    if daily_df is None or daily_df.empty:
        return result

    if "date" not in daily_df.columns or "avg_kw" not in daily_df.columns:
        return result

    # Ensure date sorted and unique by date
    df = daily_df.copy().sort_values("date")

    # Peak day = highest avg_kw
    peak_row = df.sort_values("avg_kw", ascending=False).iloc[0]
    peak_date_val = peak_row["date"]
    if isinstance(peak_date_val, date):
        result["peak_day"] = peak_date_val.isoformat()
    else:
        try:
            result["peak_day"] = str(peak_date_val)[:10]
        except Exception:
            result["peak_day"] = None

    # Typical day = closest to median avg_kw
    median_load = float(df["avg_kw"].median())
    df["abs_diff"] = (df["avg_kw"] - median_load).abs()
    typical_row = df.sort_values("abs_diff").iloc[0]
    typical_date_val = typical_row["date"]
    if isinstance(typical_date_val, date):
        result["typical_day"] = typical_date_val.isoformat()
    else:
        try:
            result["typical_day"] = str(typical_date_val)[:10]
        except Exception:
            result["typical_day"] = None

    return result


def _build_representative_day_chart(hourly_df: DataFrame, title: str) -> alt.Chart:
    """
    Build a simple hourly profile chart for a single representative day,
    using obs_hour_local or obs_hour_utc and avg_kw.
    """
    if hourly_df is None or hourly_df.empty:
        return alt.Chart().mark_text(text="No hourly data for selected day").properties(height=200)

    x_col = "obs_hour_local" if "obs_hour_local" in hourly_df.columns else (
        "obs_hour_utc" if "obs_hour_utc" in hourly_df.columns else None
    )
    if x_col is None or "avg_kw" not in hourly_df.columns:
        return alt.Chart().mark_text(text="Missing hour or load columns").properties(height=200)

    chart = (
        alt.Chart(hourly_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{x_col}:Q", title="Hour of Day"),
            y=alt.Y("avg_kw:Q", title="Average Load (kW)"),
            tooltip=[f"{x_col}:Q", "avg_kw:Q"],
        )
        .properties(title=title, height=250)
    )
    return chart


def main():
    # ---- Header ----
    render_page_header(
        "Energy Overview",
        "2016 historical load, solar, and weather data",
    )

    # ---- Global date range (based on dim_date) ----
    default_start, default_end = get_date_range_defaults()

    # ---- Region & season filters (sidebar) ----
    selected_region, selected_season = render_overview_filters(
        default_region=None,
        default_season=None,
    )

    # ---- Substation filter (optional, depends on region) ----
    selected_substation: str | None = None
    substation_options = get_substation_options(selected_region)
    if substation_options:
        substation_labels = ["All substations"] + substation_options
        substation_index = 0
        selected_sub_label = st.sidebar.selectbox(
            "Substation",
            substation_labels,
            index=substation_index,
        )
        if selected_sub_label != "All substations":
            selected_substation = selected_sub_label

    # ---- Data queries ----
    daily_df = get_daily_region_usage(
        region_id=selected_region,
        date_start=default_start,
        date_end=default_end,
    )
    hourly_df = get_hourly_region_usage(
        region_id=selected_region,
        date_start=default_start,
        date_end=default_end,
    )

    # Apply substation filter where possible
    daily_df = _apply_substation_filter(daily_df, selected_substation)
    hourly_df = _apply_substation_filter(hourly_df, selected_substation)

    # ---- KPI Row (using daily & hourly) ----
    kpis = _compute_kpis(daily_df, hourly_df)
    render_kpi_row(kpis)

    # ---- Daily Load Trend (with smoothing toggle) ----
    st.subheader("Daily Load Trend")

    smooth = st.checkbox("Apply 7-day rolling average", value=True)

    daily_chart_df = daily_df.copy() if daily_df is not None else None
    if (
        smooth
        and daily_chart_df is not None
        and not daily_chart_df.empty
        and "date" in daily_chart_df.columns
        and "avg_kw" in daily_chart_df.columns
    ):
        daily_chart_df = daily_chart_df.sort_values("date").copy()
        daily_chart_df["avg_kw"] = (
            daily_chart_df["avg_kw"]
            .rolling(window=7, min_periods=1)
            .mean()
        )

    daily_chart = build_daily_load_trend_chart(daily_chart_df)
    st.altair_chart(daily_chart, use_container_width=True)

    # ---- Hourly Profile Preview (aggregated by season) ----
    st.subheader("Hourly Profile Preview (by Season)")

    profile_df = get_hourly_profile_by_season(
        region_id=selected_region,
        season=selected_season,
    )
    profile_df = _apply_substation_filter(profile_df, selected_substation)

    profile_chart = build_hourly_profile_by_season_chart(profile_df)
    st.altair_chart(profile_chart, use_container_width=True)

    # ---- Representative Day Selector & Chart ----
    st.subheader("Representative Day")

    rep_candidates = _build_representative_day_options(daily_df)

    rep_modes = ["None", "Peak day", "Typical day"]
    mode = st.radio("Highlight a representative day", rep_modes, index=0, horizontal=True)

    rep_date_iso: str | None = None
    rep_label: str | None = None

    if mode == "Peak day":
        rep_date_iso = rep_candidates.get("peak_day")
        rep_label = "Peak day hourly profile"
    elif mode == "Typical day":
        rep_date_iso = rep_candidates.get("typical_day")
        rep_label = "Typical day hourly profile"

    if rep_date_iso is not None and rep_label is not None:
        st.caption(f"Selected representative day: **{rep_date_iso}**")

        rep_hourly_df = get_hourly_region_usage(
            region_id=selected_region,
            date_start=rep_date_iso,
            date_end=rep_date_iso,
        )
        rep_hourly_df = _apply_substation_filter(rep_hourly_df, selected_substation)

        rep_chart = _build_representative_day_chart(rep_hourly_df, title=rep_label)
        st.altair_chart(rep_chart, use_container_width=True)

    # ---- Footer note about static data ----
    render_footer_note(
        "This dashboard is based on a static 2016 dataset. "
        "The same pipeline can be wired to live feeds for real-time monitoring in a production setting."
    )


if __name__ == "__main__":
    main()
