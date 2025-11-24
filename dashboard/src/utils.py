from pandas import DataFrame


def ensure_date_column(df: DataFrame, column_name: str) -> DataFrame:
    """
    Ensure the given column in df is a datetime type, returning a new DataFrame
    or the original if already converted.
    """
    ...


def format_number(value: float, decimals: int = 1) -> str:
    """
    Format a numeric value for display in KPI cards.
    """
    ...
