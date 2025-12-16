# BKW Automation - Local OneDrive Processing

## Overview

This document explains the refactored project structure with utilities library and new local OneDrive processing workflow.

## Project Structure

```
BKW/
├── bkw_automation/
│   ├── __init__.py
│   ├── config.py
│   ├── sharepoint_client.py
│   ├── transformers.py
│   └── formatters.py                    # ✨ NEW: Data formatting utilities
├── notebooks/
│   ├── 01_explore_data.ipynb
│   ├── 02_sharepoint_connect.ipynb     # Updated: Now imports from formatters
│   └── 03_local_onedrive_processing.ipynb  # ✨ NEW: Local OneDrive workflow
├── data/
│   ├── output/                         # New: For CSV output files
│   ├── downloaded/
│   └── processed/
├── .env
└── pyproject.toml
```

## Changes Made

### 1. **Created `bkw_automation/formatters.py`**

A new utilities library for data formatting functions:

- **`formatdkw(df)`** - Formats DKW data with timestamp, value, and status columns
- **`format_csv_data(df, sep=';')`** - Parses CSV data with custom delimiters
- **`add_message_columns(df, source='local')`** - Adds message formatting for data transmission

**Usage:**
```python
from bkw_automation.formatters import formatdkw, format_csv_data, add_message_columns

# Format data
df = formatdkw(df)

# Add message structure
df_messages = add_message_columns(df, source='local-onedrive')
```

### 2. **Updated `02_sharepoint_connect.ipynb`**

Now imports formatting functions from the utilities library instead of defining them inline:

```python
from bkw_automation.formatters import formatdkw, format_csv_data, add_message_columns
```

### 3. **Created `03_local_onedrive_processing.ipynb`**

New workflow for local OneDrive data processing:

**Features:**
- Scans OneDrive folder for data files
- Loads CSV and XLSX files
- Applies formatting utilities
- Creates timestamped CSV output
- Generates message format for transmission
- Validates data quality

**Configuration (via .env file):**
```env
ONEDRIVE_FOLDER=/path/to/onedrive
DATA_SUBFOLDER=Data
OUTPUT_SUBFOLDER=Processed
```

## How to Use

### For SharePoint Workflow:
1. Open `02_sharepoint_connect.ipynb`
2. Follow the steps to connect to SharePoint
3. Select and download files
4. Data will be automatically formatted using the utilities library

### For Local OneDrive Workflow:
1. Open `03_local_onedrive_processing.ipynb`
2. Data will automatically load from your OneDrive folder
3. Formatted CSV files are saved to both:
   - Local: `data/output/` folder
   - OneDrive: `Processed/` folder
4. Message format is generated for transmission

## Environment Variables

Create a `.env` file in the project root:

```env
# SharePoint Configuration (for notebook 02)
SHAREPOINT_SITE_URL=https://notusenergygroup.sharepoint.com/sites/Data-Automation
SHAREPOINT_LIBRARY=Documents
SHAREPOINT_FOLDER_INCOMING=Incoming
SHAREPOINT_USERNAME=your.email@notus.de
SHAREPOINT_PASSWORD=your-password

# OneDrive Configuration (for notebook 03)
ONEDRIVE_FOLDER=/Users/sandovalsu/OneDrive
DATA_SUBFOLDER=Data
OUTPUT_SUBFOLDER=Processed
```

## File Format Specifications

### Input Data Format
- **CSV**: Semicolon-delimited or comma-delimited
- **XLSX**: Standard Excel format

### Output Format
- **Filename**: `formatted_data_YYYYMMDD_HHMMSS.csv`
- **Delimiter**: Semicolon (`;`)
- **Columns**: `timestamp`, `value`, `status`, `source` (if messages enabled), `message` (if messages enabled)

### Message Format Structure
```json
{
  "timestamp": "2025-12-16T13:45:00.000000",
  "source": "local-onedrive",
  "filename": "data.csv",
  "data_summary": {
    "total_rows": 144,
    "total_columns": 3,
    "columns": ["timestamp", "value", "status"]
  },
  "processing_metadata": {
    "processed_at": "2025-12-16T13:45:00.000000",
    "output_file": "/path/to/output/formatted_data_20251216_134500.csv",
    "output_onedrive": "/path/to/onedrive/Processed/formatted_data_20251216_134500.csv"
  }
}
```

## Utility Functions Reference

### `formatdkw(df: pd.DataFrame) -> pd.DataFrame`
Formats DKW (Datenkompressionswerkzeug) data by renaming columns and adding status indicators.

```python
df = formatdkw(df)
# Renames: 'Datum / Uhrzeit' → 'timestamp', 'Wind Speed (avg)' → 'value'
# Adds: 'status' (0 if value exists, -1 if empty)
```

### `format_csv_data(df: pd.DataFrame, sep: str = ';') -> pd.DataFrame`
Parses CSV data with custom delimiters.

```python
df = format_csv_data(df, sep=';')
# Splits concatenated columns like 'timestamp;value;status' into separate columns
```

### `add_message_columns(df: pd.DataFrame, source: str = 'local') -> pd.DataFrame`
Adds message formatting for data transmission.

```python
df = add_message_columns(df, source='local-onedrive')
# Adds 'source' column and 'message' column with formatted output
# Message format: "Timestamp: X | Value: Y | Status: Z"
```

## Troubleshooting

### OneDrive Folder Not Found
- Verify the `ONEDRIVE_FOLDER` path in your `.env` file
- Ensure OneDrive is synced to your computer
- Check folder permissions

### Data Not Loading
- Verify file format is CSV or XLSX
- Check file is not locked by another application
- Ensure column names match expected format

### Output Not Saved
- Check write permissions to `data/output/` folder
- Verify OneDrive `Processed/` folder exists
- Check disk space availability

## Next Steps

1. **Extend the formatters library** with additional data transformation functions
2. **Add database export** functionality to save processed data to a database
3. **Implement email notification** when processing completes
4. **Create automated scheduler** to run processing on a schedule

---

For questions or issues, refer to the notebooks' troubleshooting sections or check the logging output.
