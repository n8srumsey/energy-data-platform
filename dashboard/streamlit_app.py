import streamlit as st
import pandas as pd
import snowflake.connector

@st.cache_resource
def get_snowflake_conn():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        role=st.secrets["snowflake"]["role"],           # e.g. ENERGY_APP_RO
        warehouse=st.secrets["snowflake"]["warehouse"], # e.g. WH_BI
        database="ENERGY_DATA",
        schema="GOLD",
    )

def run_query(sql, params=None):
    conn = get_snowflake_conn()
    cur = conn.cursor()
    try:
        cur.execute(sql, params or {})
        df = cur.fetch_pandas_all()
    finally:
        cur.close()
    return df

st.title("Hourly Load Profile by Region & Season")

# Simple selectors
regions = run_query("SELECT DISTINCT region_id FROM dim_region_substation ORDER BY region_id")
region = st.selectbox("Region", regions["REGION_ID"])

seasons = run_query("SELECT DISTINCT season FROM dim_month_season ORDER BY season")
season = st.selectbox("Season", seasons["SEASON"])

# Example query: hourly load profile by season + region
sql = """
SELECT
  h.hour_of_day,
  AVG(h.load_mw) AS avg_load_mw
FROM hourly_load_profile_by_season h
JOIN dim_region_substation r
  ON h.region_id = r.region_id
JOIN dim_month_season s
  ON h.month = s.month
WHERE r.region_id = %(region)s
  AND s.season = %(season)s
GROUP BY h.hour_of_day
ORDER BY h.hour_of_day;
"""

df = run_query(sql, {"region": region, "season": season})

st.line_chart(
    df.set_index("HOUR_OF_DAY")["AVG_LOAD_MW"],
)
