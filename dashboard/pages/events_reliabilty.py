from datetime import date

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
    get_date_range_defaults,
)
from src.queries import (
    get_data_coverage_summary,
    get_extreme_event_days,
)
from src.charts import (
    build_coverage_heatmap_chart,
    build_extreme_events_timeline_chart,
)


def _compute_reliability_kpis(coverage_df: DataFrame) -> list[dict]:
    """
    Compute simple reliability KPIs from data_coverage_summary.

    Assumes coverage_df has:
      - date
      - region_id or station_id
      - coverage_pct (0–100) or coverage (0–1)
    """
    if coverage_df is None or coverage_df.empty:
        return [
            {"label": "% Days with High Coverage", "value": "–"},
            {"label": "Best Region/Station", "value": "–"},
            {"label": "Worst Region/Station", "value": "–"},
            {"label": "Lowest-Coverage Month", "value": "–"},
        ]

    df = coverage_df.copy()

    # Normalize coverage metric to 0–100
    cov_col = None
    for candidate in ["coverage_pct", "coverage"]:
        if candidate in df.columns:
            cov_col = candidate
            break

    if cov_col is None:
        return [
            {"label": "% Days with High Coverage", "value": "–"},
            {"label": "Best Region/Station", "value": "–"},
            {"label": "Worst Region/Station", "value": "–"},
            {"label": "Lowest-Coverage Month", "value": "–"},
        ]

    coverage_series = df[cov_col].astype(float)
    # If values look like proportions 0–1, scale to percent
    if coverage_series.max() <= 1.0:
        df["coverage_pct_norm"] = coverage_series * 100.0
    else:
        df["coverage_pct_norm"] = coverage_series

    # % days with coverage >= 95%
    high_cov_threshold = 95.0
    # Count per-date coverage by averaging across regions/stations
    if "date" in df.columns:
        daily_cov = (
            df.groupby("date")["coverage_pct_norm"]
            .mean()
            .reset_index()
        )
        if not daily_cov.empty:
            high_cov_days = (daily_cov["coverage_pct_norm"] >= high_cov_threshold).sum()
            total_days = len(daily_cov)
            pct_high_cov = 100.0 * high_cov_days / total_days if total_days > 0 else 0.0
            high_cov_str = f"{pct_high_cov:.1f}%"
        else:
            high_cov_str = "–"
    else:
        high_cov_str = "–"

    # Best / worst region or station by average coverage
    id_col = "region_id" if "region_id" in df.columns else (
        "station_id" if "station_id" in df.columns else None
    )

    best_label = "–"
    worst_label = "–"

    if id_col is not None:
        grp = (
            df.groupby(id_col)["coverage_pct_norm"]
            .mean()
            .reset_index()
        )
        if not grp.empty:
            best_row = grp.sort_values("coverage_pct_norm", ascending=False).iloc[0]
            worst_row = grp.sort_values("coverage_pct_norm", ascending=True).iloc[0]

            best_label = f"{best_row[id_col]} ({best_row['coverage_pct_norm']:.1f}%)"
            worst_label = f"{worst_row[id_col]} ({worst_row['coverage_pct_norm']:.1f}%)"

    # Lowest-coverage month
    month_label = "–"
    if "date" in df.columns:
        # Ensure datetime
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])

        df["year_month"] = df["date"].dt.to_period("M").dt.to_timestamp()
        month_grp = (
            df.groupby("year_month")["coverage_pct_norm"]
            .mean()
            .reset_index()
        )
        if not month_grp.empty:
            worst_month = month_grp.sort_values("coverage_pct_norm", ascending=True).iloc[0]
            # Format as YYYY-MM
            month_label = worst_month["year_month"].strftime("%Y-%m") + f" ({worst_month['coverage_pct_norm']:.1f}%)"

    kpis = [
        {"label": "% Days with High Coverage (>=95%)", "value": high_cov_str},
        {"label": "Best Region/Station", "value": best_label},
        {"label": "Worst Region/Station", "value": worst_label},
        {"label": "Lowest-Coverage Month", "value": month_label},
    ]

    return kpis


def _render_kpi_row_simple(kpis: list[dict]) -> None:
    """
    Render a simple KPI row without depending on the layouts KPI function,
    so we can show slightly richer labels if desired.
    """
    if not kpis:
        return

    cols = st.columns(len(kpis))
    for col, item in zip(cols, kpis):
        label = str(item.get("label", ""))
        value = str(item.get("value", ""))
        with col:
            st.metric(label=label, value=value)


def main() -> None:
    # ---- Header ----
    render_page_header(
        "Events & Reliability",
        "Extreme days, data coverage, and reliability metrics for the 2016 dataset",
    )

    st.sidebar.markdown("### Filters")

    # ---- Region (optional) ----
    region_options = get_region_options()
    region_labels = ["All regions"] + region_options
    region_index = 0
    selected_region_label = st.sidebar.selectbox(
        "Region (optional)",
        region_labels,
        index=region_index,
    )
    if selected_region_label == "All regions":
        selected_region: str | None = None
    else:
        selected_region = selected_region_label

    # ---- Date range ----
    default_start, default_end = get_date_range_defaults()
    st.sidebar.markdown("### Date Range")
    date_start, date_end = render_date_range_filter(default_start, default_end)

    # ---- Event type filter (if available) ----
    raw_events_df = get_extreme_event_days(
        region_id=selected_region,
        date_start=date_start,
        date_end=date_end,
    )

    selected_event_type: str | None = None
    if raw_events_df is not None and not raw_events_df.empty and "event_type" in raw_events_df.columns:
        types = (
            raw_events_df["event_type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        types.sort()
        type_labels = ["All types"] + types
        type_index = 0
        selected_type_label = st.sidebar.selectbox(
            "Event type (optional)",
            type_labels,
            index=type_index,
        )
        if selected_type_label != "All types":
            selected_event_type = selected_type_label

        if selected_event_type is not None:
            events_df = raw_events_df[raw_events_df["event_type"] == selected_event_type]
        else:
            events_df = raw_events_df
    else:
        events_df = raw_events_df

    # ---- Section: Extreme Events ----
    st.subheader("Extreme Event Days")

    if events_df is None or events_df.empty:
        st.info("No extreme events found for the selected filters.")
    else:
        # Timeline chart
        events_chart = build_extreme_events_timeline_chart(events_df)
        st.altair_chart(events_chart, use_container_width=True)

        st.caption(
            "Each mark represents a day flagged as an 'extreme' event based on "
            "load and/or weather criteria in the Gold-layer processing."
        )

        # Tabular view for detail
        st.markdown("#### Event Details")
        st.dataframe(events_df, use_container_width=True)

    # ---- Section: Data Coverage ----
    st.subheader("Data Coverage Summary")

    coverage_df = get_data_coverage_summary(
        region_id=selected_region,
        date_start=date_start,
        date_end=date_end,
    )

    if coverage_df is None or coverage_df.empty:
        st.info("No coverage data found for the selected filters.")
    else:
        cov_chart = build_coverage_heatmap_chart(coverage_df)
        st.altair_chart(cov_chart, use_container_width=True)

        st.caption(
            "Darker colors indicate higher data coverage across dates and regions/stations. "
            "This aggregates coverage metrics derived from the Gold-layer QA tables."
        )

        # Reliability KPI row
        st.markdown("#### Reliability KPIs")
        kpis = _compute_reliability_kpis(coverage_df)
        _render_kpi_row_simple(kpis)

    # ---- Footer / Narrative ----
    render_footer_note(
        "This page summarizes how complete the 2016 dataset is and highlights days with "
        "unusual load or weather behavior. In a production setting, these metrics could "
        "power alerts and data quality dashboards for live operations."
    )


if __name__ == "__main__":
    main()
