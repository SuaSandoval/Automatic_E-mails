"""
Data formatting utilities for BKW automation.

Provides functions to format and transform data from various sources.
"""

import pandas as pd
from typing import Optional


def formatdkw(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format DKW (Datenkompressionswerkzeug) data.
    
    Renames columns, normalizes timestamps to ISO 8601 with Z, and adds status information.
    Handles timezone conversion from Swiss local time (CET/CEST) to UTC.
    
    Args:
        df: DataFrame with columns 'Datum / Uhrzeit' and 'Wind Speed (avg)'
    
    Returns:
        Formatted DataFrame with 'timestamp', 'value', and 'status' columns
    """
    df = df.rename(columns={
        'Datum / Uhrzeit': 'timestamp',
        'Wind Speed (avg)': 'value'
    })
    
    # Parse timestamps as Swiss local time (Europe/Zurich), then convert to UTC
    # This automatically handles CET (UTC+1) and CEST (UTC+2) transitions
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['timestamp'] = df['timestamp'].dt.tz_localize('Europe/Zurich', ambiguous='infer', nonexistent='shift_forward')
    df['timestamp'] = df['timestamp'].dt.tz_convert('UTC')
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    df['status'] = df['value'].apply(lambda x: 0 if x else -1)
    return df


def format_csv_data(df: pd.DataFrame, sep: str = ';') -> pd.DataFrame:
    """
    Parse and format CSV data with semicolon or custom delimiter.
    
    Args:
        df: DataFrame to format
        sep: Delimiter used in the data (default: semicolon)
    
    Returns:
        Properly formatted DataFrame
    """
    # If data came from CSV with wrong delimiter, it will have columns
    # like 'timestamp;value;status' - split them
    if len(df.columns) == 1 and sep in df.columns[0]:
        col_name = df.columns[0]
        df = df[col_name].str.split(sep, expand=True)
        df.columns = ['timestamp', 'value', 'status']
    
    return df


def add_message_columns(df: pd.DataFrame, source: str = 'local') -> pd.DataFrame:
    """
    Add message-formatted columns for communication/export.
    
    Args:
        df: DataFrame with timestamp, value, status columns
        source: Source identifier (e.g., 'local', 'sharepoint')
    
    Returns:
        DataFrame with additional message columns
    """
    df = df.copy()
    df['source'] = source
    df['message'] = df.apply(
        lambda row: f"Timestamp: {row['timestamp']} | Value: {row['value']} | Status: {row['status']}",
        axis=1
    )
    return df
