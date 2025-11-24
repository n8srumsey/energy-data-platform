import streamlit as st

from src.layouts import render_page_header, render_footer_note


def main() -> None:
    render_page_header(
        "Data & Pipeline",
        "How Databricks, Snowflake, and Streamlit fit together in this project",
    )

    st.markdown("### Data Model Overview")

    st.markdown(
        """
This dashboard is powered by **Gold-layer** tables modeled for analysis in Snowflake.

**Fact tables (metrics over time):**

- `daily_region_usage`  
  Daily energy and load metrics by region (and optionally substation).
- `hourly_region_usage`  
  Hourly load, reactive power, and weather/solar attributes by region and station.
- `hourly_load_profile_by_season`  
  Typical hourly shapes by season and region.
- `hourly_load_profile_by_segment`  
  Typical hourly shapes by season and weekday/weekend (and other segments if defined).
- `temp_bin_load_stats`  
  Load statistics binned by temperature to capture heating/cooling sensitivity.
- `solar_impact_on_load`  
  Aggregated solar irradiance vs load, used to quantify solar-load relationships.
- `extreme_event_days`  
  Days flagged as anomalous or extreme based on load and/or weather criteria.
- `data_coverage_summary`  
  Coverage and completeness metrics across dates, regions, and stations.

**Dimension tables (lookup and structure):**

- `dim_date` – calendar dates, day-of-week, holidays, etc.  
- `dim_month_season` – seasons and month-to-season mapping.  
- `dim_region_substation` – regions, substations, and descriptive attributes.  
- `dim_station` – weather station metadata (location, elevation, etc.).  
- `dim_solar_site` – solar site metadata for the irradiance measurements.
        """
    )

    st.markdown("### Pipeline Overview")

    st.markdown(
        """
The end-to-end pipeline is designed as a **lakehouse-style architecture**:

1. **Bronze (Raw Ingestion in Databricks)**  
   - Ingest SMART-DS electric load data (building/substation-level usage).  
   - Ingest solar irradiance measurements (GHI/DNI/DHI) from a California site.  
   - Ingest NOAA ISD airport weather data (temperature, wind, precipitation, etc.).  
   - Store raw or lightly processed data as Delta tables in Unity Catalog.

2. **Silver (Cleaned & Standardized in Databricks)**  
   - Align all datasets to a common **hourly** timeline.  
   - Clean units (e.g., °C, W/m², kWh) and handle missing or inconsistent values.  
   - Aggregate as appropriate:  
     - Load: aggregate from fine-grained points to region/substation.  
     - Solar: align and aggregate irradiance at the relevant spatial resolution.  
     - Weather: unify ISD variables into a consistent schema.  
   - Produce **cleaned usage**, **cleaned solar**, and **cleaned weather** tables, plus a unified hourly joined dataset.

3. **Gold (Curated Analytics in Databricks → Snowflake)**  
   - From the Silver layer, compute curated analytics tables:  
     - Daily and hourly usage summaries.  
     - Hourly profiles by season and segment.  
     - Temperature-bin load statistics.  
     - Solar-load impact summaries.  
     - Extreme event flags and coverage metrics.  
   - Write these Gold tables as Delta in Unity Catalog.  
   - Export Gold tables as Parquet to S3 at:  
     `s3://energy-data-platform-project/export/<table_name>/`.

4. **Snowflake (Serving & BI Layer)**  
   - Define an external stage pointing at the S3 export location.  
   - Use `INFER_SCHEMA` + `USING TEMPLATE` to create internal Snowflake tables for each Gold export.  
   - `COPY INTO` these internal tables from the Parquet files in S3.  
   - Expose Gold tables through a **read-only role** designed for dashboards and applications.

5. **Streamlit (Dashboard Application)**  
   - A Streamlit app connects to Snowflake using the read-only role.  
   - Queries Gold tables (via Snowflake connector) to power:  
     - Overview KPIs and daily/hourly trends.  
     - Load pattern exploration by season and segment.  
     - Weather and solar sensitivity views.  
     - Events & reliability summaries.

Together, this demonstrates a complete path from **real-world raw data** to **curated analytical views**.
        """
    )

    st.markdown("### Limitations & Future Work")

    st.markdown(
        """
This project intentionally focuses on a single historical year (**2016**) to show the
end-to-end architecture without adding complex operational concerns.

**Current limitations:**

- Only one year of data (2016) is included.  
- No automated schedule for refreshing Bronze/Silver/Gold layers.  
- No advanced forecasting or anomaly detection models are deployed yet.  

**Future extensions:**

- **Multi-year support:**  
  Ingest and process multiple years of SMART-DS, solar, and NOAA ISD data; extend the Gold tables and dashboards accordingly.

- **Incremental updates:**  
  Convert full-refresh loads into incremental pipelines, using partitioned S3 exports and incremental `COPY` or `MERGE` operations into Snowflake.

- **Forecasting and planning:**  
  Add load forecasting models (e.g., temperature-based regressions, gradient boosting, or neural nets) and surface forecast vs actuals in Snowflake and Streamlit.

- **Operational monitoring:**  
  Build alerting dashboards around extreme events and data coverage metrics to monitor the health of the data feeds in near real-time.

Even in its current form, the project shows a realistic pattern:
use Databricks for heavy ETL, Snowflake for serving curated analytics, and Streamlit
for lightweight, interactive applications.
        """
    )

    render_footer_note(
        "This page is intended as a technical overview for reviewers and collaborators. "
        "The full implementation is split across Databricks notebooks, Snowflake SQL, "
        "and this Streamlit app."
    )


if __name__ == "__main__":
    main()
