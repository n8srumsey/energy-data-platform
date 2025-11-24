from typing import Any

import pandas as pd
from pandas import DataFrame
import snowflake.connector
from snowflake.connector import SnowflakeConnection

import streamlit as st


# -------- Connection helpers --------

@st.cache_resource(show_spinner=False)
def get_snowflake_connection_from_secrets() -> SnowflakeConnection:
    """
    Create and return a Snowflake connection using Streamlit secrets.
    This is the single place that knows how to read st.secrets["snowflake"].

    Expected secrets layout:

    [snowflake]
    account   = "..."
    user      = "..."
    password  = "..."
    role      = "ENERGY_APP_RO"
    warehouse = "WH_BI"
    database  = "ENERGY_DATA"
    schema    = "GOLD"
    """
    cfg = st.secrets["snowflake"]

    # Explicitly pull known keys; ignore extras gracefully
    conn = snowflake.connector.connect(
        account=cfg["account"],
        user=cfg["user"],
        password=cfg["password"],
        role=cfg.get("role"),
        warehouse=cfg.get("warehouse"),
        database=cfg.get("database"),
        schema=cfg.get("schema"),
    )

    return conn


def get_snowflake_connection(config: dict) -> SnowflakeConnection:
    """
    Create and return a Snowflake connection using an explicit config dict.
    Useful for tests or non-Streamlit scripts.

    Expected keys include:
      account, user, password, role, warehouse, database, schema
    """
    conn = snowflake.connector.connect(
        account=config["account"],
        user=config["user"],
        password=config["password"],
        role=config.get("role"),
        warehouse=config.get("warehouse"),
        database=config.get("database"),
        schema=config.get("schema"),
    )
    return conn


def close_snowflake_connection(conn: SnowflakeConnection) -> None:
    """
    Safely close a Snowflake connection.
    """
    try:
        conn.close()
    except Exception:
        # Swallow errors on close; connection might already be closed.
        pass


# -------- Query helpers --------

def run_query(sql: str, params: dict  = None) -> DataFrame:
    """
    Execute a SQL query and return results as a pandas DataFrame.

    Uses a cached Snowflake connection created from Streamlit secrets.
    """
    conn = get_snowflake_connection_from_secrets()
    cur = conn.cursor()
    try:
        if params is not None:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        df: DataFrame = cur.fetch_pandas_all()
    finally:
        cur.close()
    return df


def run_scalar(sql: str, params: dict = None) -> str | int | float | None:
    """
    Execute a SQL query expected to return a single scalar value.
    Returns the first column of the first row or None if no rows.
    """
    conn = get_snowflake_connection_from_secrets()
    cur = conn.cursor()
    try:
        if params is not None:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        row = cur.fetchone()
    finally:
        cur.close()

    if row is None or len(row) == 0:
        return None

    value: Any = row[0]
    # Let the caller handle the actual type; we just return the first column.
    return value
