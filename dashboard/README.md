# Streamlit App Plan: Multipage Layout & Code Organization

## App Structure Overview

The app will be organized into multiple pages, exposed via Streamlit’s sidebar navigation:

1. **Overview**
2. **Load Patterns**
3. **Weather & Solar Impact**
4. **Events & Reliability**
5. **Data & Pipeline (About)**

---

## Page 1 – Overview

**Purpose:** Provide a high-level introduction to the dataset and platform pipeline.

### Content

- Context text:
  - Data sources: SMART-DS, solar site, NOAA ISD
  - Time range: *2016 (historical, static dataset)*
  - Pipeline summary: Databricks → S3 → Snowflake → Streamlit

### Global Filters

- Region selector
- Optional substation selector
- Season or date range selector

### KPI Cards

- Average daily load (2016)
- Peak hourly load (value + date/time)
- Total energy (MWh) in 2016
- Number of days with valid data

### Main Charts

- Daily load trend (with optional 7-day smoothing)
- Hourly profile preview for current region/season

### Notes

- Clear statement that data is historical, not live

---

## Page 2 – Load Patterns

**Purpose:** Explore demand behavior across time of day, seasons, and weekday/weekend segments.

### Filters

- Region (required)
- Season (optional)
- Toggle: season vs. segment view
- Optional substation filter

### Sections

#### Hourly Profile by Season

- Multi-line plot:
  - X: hour_of_day
  - Y: avg_kw
  - One line per season

#### Segment Comparison

- Based on `_by_segment` table (e.g., `fall_weekday`)
- Options:
  - One season with weekday vs weekend
  - Grid of seasonal comparisons

#### Distribution View (Optional)

- Based on `hourly_region_usage`
- Boxplot or bar showing mean vs p90 by hour_of_day

---

## Page 3 – Weather & Solar Impact

**Purpose:** Show how temperature and solar irradiance relate to load.

### Filters

- Region (required)
- Season (optional)
- Optional month or temperature range filter

### Sections

#### Temperature Sensitivity Curve

- From `temp_bin_load_stats`
- X: temperature bin
- Y: load metric

#### Solar vs Load Scatter

- From `solar_impact_on_load`
- X: irradiance
- Y: load
- Color/facet by season
- Optional trendline

#### Overlay Example (Optional)

- Time-based comparison of load vs temperature/solar over a selected period

### Notes

- Frame insights as historical context
- Mention how this framework supports real-time dashboards in future

---

## Page 4 – Events & Reliability

**Purpose:** Demonstrate data completeness and highlight unusual days.

### Filters

- Region
- Date range
- Event type filters

### Sections

#### Extreme Events Table

- From `extreme_event_days`
- Columns such as:
  - date
  - region/substation
  - event type
  - peak values

#### Data Coverage Summary

- From `data_coverage_summary`
- Suggested visuals:
  - Calendar heatmap
  - Coverage by month or station

#### Reliability KPIs

- % of days with high coverage
- Best/worst stations
- Most problematic months

### Narrative

- Emphasize automated quality metrics in the pipeline

---

## Page 5 – Data & Pipeline (About)

**Purpose:** Explain the engineering behind the dashboard.

### Sections

#### Data Model Overview

- Facts:
  - daily_region_usage
  - hourly_region_usage
  - hourly_load_profile_by_*
  - temp_bin_load_stats
  - solar_impact_on_load
  - extreme_event_days
  - data_coverage_summary
- Dimensions:
  - dim_date
  - dim_month_season
  - dim_region_substation
  - dim_station
  - dim_solar_site

#### Pipeline Overview

- Bronze: raw ingestion
- Silver: cleaned, hourly aligned
- Gold: curated metrics
- Export to S3 → Load to Snowflake → Streamlit frontend

#### Limitations & Future Work

- Only 2016 data
- Potential extensions:
  - Multi-year support
  - Regular refresh
  - Forecasting / anomaly detection

---

## Code Organization Recommendations

### Option 2: True Multipage Using `pages/` Directory


```
energy-analytics-dashboard/
├─ streamlit_app.py
├─ pages/
│ ├─ 1_Load_Patterns.py
│ ├─ 2_Weather_and_Solar.py
│ ├─ 3_Events_and_Reliability.py
│ └─ 4_Data_and_Pipeline.py
└─ src/
├─ data.py
├─ queries.py
├─ charts.py
└─ layout.py
```

**Pros**

- Clean separation
- Easy to navigate
- Recruiter-friendly

**Cons**

- More moving parts
- Shared filters require structure