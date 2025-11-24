from datetime import date

import streamlit as st

from .filters import (
    get_region_options,
    get_season_options,
    get_date_range_defaults,
)


def render_page_header(title: str, subtitle: str | None = None) -> None:
    """
    Render a standardized page header with optional subtitle.
    """
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def render_kpi_row(kpi_items: list[dict]) -> None:
    """
    Render a row of KPI cards. Each dict might contain keys like:
    {"label": str, "value": str, "delta": str | None}.
    """
    if not kpi_items:
        return

    cols = st.columns(len(kpi_items))

    for col, item in zip(cols, kpi_items):
        label = str(item.get("label", ""))
        value = str(item.get("value", ""))
        delta = item.get("delta")

        with col:
            if delta is not None:
                st.metric(label=label, value=value, delta=str(delta))
            else:
                st.metric(label=label, value=value)


def render_overview_filters(
    default_region: str | None,
    default_season: str | None,
) -> tuple[str | None, str | None]:
    """
    Render the standard filter controls for the Overview page and
    return the selected (region_id, season).

    Returns:
        (region_id_or_none, season_or_none)
    """
    region_options = get_region_options()
    season_options = get_season_options()

    # Region select
    region_labels: list[str] = ["All regions"] + region_options
    region_index = 0
    if default_region is not None and default_region in region_options:
        region_index = region_options.index(default_region) + 1

    selected_region_label = st.sidebar.selectbox(
        "Region",
        region_labels,
        index=region_index,
    )

    selected_region: str | None
    if selected_region_label == "All regions":
        selected_region = None
    else:
        selected_region = selected_region_label

    # Season select
    season_labels: list[str] = ["All seasons"] + season_options
    season_index = 0
    if default_season is not None and default_season in season_options:
        season_index = season_options.index(default_season) + 1

    selected_season_label = st.sidebar.selectbox(
        "Season",
        season_labels,
        index=season_index,
    )

    selected_season: str | None
    if selected_season_label == "All seasons":
        selected_season = None
    else:
        selected_season = selected_season_label

    return selected_region, selected_season


def render_date_range_filter(
    default_start: str,
    default_end: str,
) -> tuple[str, str]:
    """
    Render a date range selection control and return (start_date, end_date).

    default_start/default_end are ISO strings (YYYY-MM-DD).
    Returns ISO strings as well.
    """
    try:
        start_default = date.fromisoformat(default_start)
    except ValueError:
        # Fallback to full dataset if parsing fails
        ds, de = get_date_range_defaults()
        start_default = date.fromisoformat(ds)

    try:
        end_default = date.fromisoformat(default_end)
    except ValueError:
        ds, de = get_date_range_defaults()
        end_default = date.fromisoformat(de)

    date_range = st.sidebar.date_input(
        "Date range",
        value=(start_default, end_default),
    )

    # Streamlit returns:
    # - a single date if "range" mode is not used
    # - a tuple of (start, end) in range mode
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_selected, end_selected = date_range
    else:
        # If user picks a single date, use it as both start and end
        start_selected = date_range
        end_selected = date_range

    start_str = start_selected.isoformat()
    end_str = end_selected.isoformat()

    return start_str, end_str


def render_footer_note(note: str) -> None:
    """
    Render a small note at the bottom of the page, useful for caveats about
    static data, data sources, or methodology.
    """
    if not note:
        return

    st.markdown(
        f"<div style='margin-top: 1.5rem; font-size: 0.8rem; color: #666;'>{note}</div>",
        unsafe_allow_html=True,
    )
