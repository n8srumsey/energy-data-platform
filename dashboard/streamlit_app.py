import streamlit as st

from src.layouts import render_page_header, render_footer_note


# Important: call this once, near the top
st.set_page_config(
    page_title="Energy Analytics – 2016 Load & Weather",
    layout="wide",
)


def main() -> None:
    # Top header
    render_page_header(
        "Energy Analytics Platform",
        "Databricks → S3 → Snowflake → Streamlit (2016 historical dataset)",
    )

    st.markdown(
        """
Welcome to the **Energy Analytics Platform** demo.

This app showcases an end-to-end pipeline:

- **Databricks (Bronze/Silver/Gold)** for ingesting and transforming:
  - SMART-DS electric load near San Francisco
  - Solar irradiance (GHI/DNI/DHI)
  - NOAA ISD airport weather
- **S3** as the export location for Gold-layer Parquet files
- **Snowflake** as the serving / analytics warehouse
- **Streamlit** as the interactive dashboard layer

Use the pages in the left sidebar to explore:

1. **Overview** – High-level KPIs, daily trends, and representative days  
2. **Load Patterns** – Hourly shapes by season, segment, and distribution  
3. **Weather & Solar Impact** – Temperature sensitivity and solar–load relationships  
4. **Events & Reliability** – Extreme event days and data coverage metrics  
5. **Data & Pipeline** – Technical overview of the lakehouse and serving architecture
        """
    )

    st.markdown("---")

    st.markdown(
        """
### How this app is wired

- All charts and queries are backed by **Gold tables in Snowflake**.
- The app reads Snowflake connection details from `st.secrets["snowflake"]`.
- Shared logic (queries, charts, layouts) lives in the `src/` package.
- Each analytical page is implemented as a separate file in the `pages/` folder.
        """
    )

    render_footer_note(
        "This is a portfolio and practice project using 2016 data. "
        "In a production deployment, the same architecture could be extended to "
        "multi-year and near real-time analytics."
    )


if __name__ == "__main__":
    main()
