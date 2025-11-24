# src/charts.py

from pandas import DataFrame
import altair as alt


def _empty_chart(message: str = "No data") -> alt.Chart:
    """
    Return a simple empty chart with a centered text message.
    """
    return alt.Chart().mark_text(text=message).properties(height=200)


def build_daily_load_trend_chart(daily_df: DataFrame) -> object:
    """
    Build a daily load trend chart (e.g., line chart of date vs load).
    Expects columns:
      - date (datetime or string)
      - avg_kw OR hourly_kwh OR total_daily_kwh
    """
    if daily_df is None or daily_df.empty:
        return _empty_chart("No daily data")

    # Pick a load metric
    y_col = None
    for candidate in ["avg_kw", "hourly_kwh", "total_kwh", "total_daily_kwh"]:
        if candidate in daily_df.columns:
            y_col = candidate
            break

    if y_col is None:
        return _empty_chart("No load column")

    chart = (
        alt.Chart(daily_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y(f"{y_col}:Q", title="Load (kW/kWh)"),
            tooltip=["date:T", alt.Tooltip(f"{y_col}:Q", title="Load")],
        )
        .properties(height=300)
    )

    return chart


def build_hourly_profile_by_season_chart(profile_df: DataFrame) -> object:
    """
    Build a chart showing hourly load profiles for one or more seasons.
    Expects columns:
      - hour_of_day
      - avg_kw
      - season
    """
    if profile_df is None or profile_df.empty:
        return _empty_chart("No hourly profile data")

    if "hour_of_day" not in profile_df.columns or "avg_kw" not in profile_df.columns:
        return _empty_chart("Missing required columns")

    chart = (
        alt.Chart(profile_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("hour_of_day:Q", title="Hour of Day"),
            y=alt.Y("avg_kw:Q", title="Average Load (kW)"),
            color=alt.Color("season:N", title="Season"),
            tooltip=["season:N", "hour_of_day:Q", "avg_kw:Q"],
        )
        .properties(height=300)
    )

    return chart


def build_hourly_profile_by_segment_chart(segment_df: DataFrame) -> object:
    """
    Build a chart comparing weekday vs weekend (and/or other segments) by hour_of_day.
    Expects:
      - hour_of_day
      - avg_kw
      - segment
    """
    if segment_df is None or segment_df.empty:
        return _empty_chart("No segment data")

    if "hour_of_day" not in segment_df.columns or "avg_kw" not in segment_df.columns:
        return _empty_chart("Missing required columns")

    if "segment" not in segment_df.columns:
        return _empty_chart("Missing segment column")

    chart = (
        alt.Chart(segment_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("hour_of_day:Q", title="Hour of Day"),
            y=alt.Y("avg_kw:Q", title="Average Load (kW)"),
            color=alt.Color("segment:N", title="Segment"),
            tooltip=["segment:N", "hour_of_day:Q", "avg_kw:Q"],
        )
        .properties(height=300)
    )

    return chart


def build_temp_sensitivity_chart(temp_df: DataFrame) -> object:
    """
    Build a temperature sensitivity chart (e.g., temp_bin vs avg load).
    Expects:
      - temp_bin
      - avg_kw
    """
    if temp_df is None or temp_df.empty:
        return _empty_chart("No temperature data")

    if "temp_bin" not in temp_df.columns or "avg_kw" not in temp_df.columns:
        return _empty_chart("Missing required columns")

    chart = (
        alt.Chart(temp_df)
        .mark_bar()
        .encode(
            x=alt.X("temp_bin:O", title="Temperature Bin (°C)"),
            y=alt.Y("avg_kw:Q", title="Average Load (kW)"),
            tooltip=["temp_bin:O", "avg_kw:Q"],
        )
        .properties(height=300)
    )

    return chart


def build_solar_vs_load_scatter_chart(solar_df: DataFrame) -> object:
    """
    Build a scatter plot of solar irradiance vs load, possibly colored by season.
    Expects:
      - avg_ghi_w_m2 OR ghi_w_m2
      - avg_kw OR hourly_kwh
      - season (optional)
    """
    if solar_df is None or solar_df.empty:
        return _empty_chart("No solar data")

    x_col = None
    for candidate in ["avg_ghi_w_m2", "ghi_w_m2"]:
        if candidate in solar_df.columns:
            x_col = candidate
            break

    y_col = None
    for candidate in ["avg_kw", "hourly_kwh"]:
        if candidate in solar_df.columns:
            y_col = candidate
            break

    if x_col is None or y_col is None:
        return _empty_chart("Missing irradiance/load columns")

    encode_kwargs = dict(
        x=alt.X(f"{x_col}:Q", title="Solar Irradiance (W/m²)"),
        y=alt.Y(f"{y_col}:Q", title="Load (kW/kWh)"),
        tooltip=[x_col, y_col],
    )

    if "season" in solar_df.columns:
        encode_kwargs["color"] = alt.Color("season:N", title="Season")

    chart = (
        alt.Chart(solar_df)
        .mark_circle(size=60, opacity=0.6)
        .encode(**encode_kwargs)
        .properties(height=300)
    )

    return chart


def build_coverage_heatmap_chart(coverage_df: DataFrame) -> object:
    """
    Build a heatmap or similar visualization from data_coverage_summary.
    Expects:
      - date
      - region_id or station_id
      - coverage or coverage_pct
    """
    if coverage_df is None or coverage_df.empty:
        return _empty_chart("No coverage data")

    y_col = "region_id" if "region_id" in coverage_df.columns else (
        "station_id" if "station_id" in coverage_df.columns else None
    )
    if y_col is None:
        return _empty_chart("Missing region/station column")

    value_col = None
    for candidate in ["coverage", "coverage_pct"]:
        if candidate in coverage_df.columns:
            value_col = candidate
            break

    if value_col is None:
        return _empty_chart("Missing coverage metric")

    chart = (
        alt.Chart(coverage_df)
        .mark_rect()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y(f"{y_col}:N", title="Region/Station"),
            color=alt.Color(f"{value_col}:Q", title="Coverage"),
            tooltip=["date:T", y_col, value_col],
        )
        .properties(height=300)
    )

    return chart


def build_extreme_events_timeline_chart(events_df: DataFrame) -> object:
    """
    Build a simple timeline or bar chart showing extreme events over time.
    Expects:
      - date
      - event_type OR region_id
    """
    if events_df is None or events_df.empty:
        return _empty_chart("No event data")

    if "date" not in events_df.columns:
        return _empty_chart("Missing date column")

    chart = (
        alt.Chart(events_df)
        .mark_tick(size=50, thickness=2)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("region_id:N", title="Region"),
            tooltip=["date:T", "region_id"],
            color=alt.Color("region_id:N", legend=None),
        )
        .properties(height=300)
    )

    return chart
