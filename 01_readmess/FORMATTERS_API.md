# BKW Automation Utilities Library - API Reference

## Module: `bkw_automation.formatters`

Complete reference for all formatting utility functions.

---

## Function: `formatdkw`

### Description
Formats DKW (Datenkompressionswerkzeug) data by standardizing column names and adding status indicators based on values.

### Signature
```python
def formatdkw(df: pd.DataFrame) -> pd.DataFrame
```

### Parameters
- **df** (`pd.DataFrame`): Input DataFrame containing columns 'Datum / Uhrzeit' and 'Wind Speed (avg)'

### Returns
- **pd.DataFrame**: Formatted DataFrame with columns: 'timestamp', 'value', 'status'

### Column Transformations
| Input Column | Output Column | Description |
|---|---|---|
| Datum / Uhrzeit | timestamp | ISO format timestamp |
| Wind Speed (avg) | value | Wind speed value |
| — | status | 0 if value exists, -1 if empty |

### Example
```python
from bkw_automation.formatters import formatdkw

# Load raw data
df = pd.read_csv('winddata.csv')

# Apply formatting
df_formatted = formatdkw(df)

print(df_formatted.head())
# Output:
#                  timestamp   value  status
# 0  2025-11-23T23:10:00Z    8.72       0
# 1  2025-11-23T23:20:00Z    9.02       0
# 2  2025-11-23T23:30:00Z    8.73       0
```

### Errors
- Raises `KeyError` if expected columns are not found
- Raises `ValueError` if data format is invalid

---

## Function: `format_csv_data`

### Description
Parses CSV data with custom delimiters. Useful when CSV data was read with wrong delimiter and columns are concatenated.

### Signature
```python
def format_csv_data(df: pd.DataFrame, sep: str = ';') -> pd.DataFrame
```

### Parameters
- **df** (`pd.DataFrame`): DataFrame with potentially concatenated columns
- **sep** (`str`, default=`;`): Delimiter used in the data

### Returns
- **pd.DataFrame**: DataFrame with separated columns

### Example
```python
from bkw_automation.formatters import format_csv_data

# Data loaded with wrong delimiter - columns concatenated
df = pd.read_csv('data.csv')
# Result: Single column named 'timestamp;value;status'

# Apply parsing with correct delimiter
df_parsed = format_csv_data(df, sep=';')

print(df_parsed.head())
# Output:
#                  timestamp   value  status
# 0  2025-11-23T23:10:00Z    8.72       0
# 1  2025-11-23T23:20:00Z    9.02       0
```

### Notes
- Automatically detects if data needs parsing
- Skips if columns are already properly separated
- Sets column names to: `['timestamp', 'value', 'status']`

---

## Function: `add_message_columns`

### Description
Adds message formatting columns to a DataFrame for structured data transmission. Creates human-readable message strings and adds source identifier.

### Signature
```python
def add_message_columns(df: pd.DataFrame, source: str = 'local') -> pd.DataFrame
```

### Parameters
- **df** (`pd.DataFrame`): Input DataFrame with columns 'timestamp', 'value', 'status'
- **source** (`str`, default='local'): Source identifier for the data

### Returns
- **pd.DataFrame**: DataFrame with added 'source' and 'message' columns

### New Columns Added
| Column | Type | Description |
|---|---|---|
| source | str | Source identifier (e.g., 'local-onedrive', 'sharepoint') |
| message | str | Formatted message string |

### Message Format
```
Timestamp: <timestamp> | Value: <value> | Status: <status>
```

### Example
```python
from bkw_automation.formatters import add_message_columns

# Add message columns
df_with_messages = add_message_columns(df, source='local-onedrive')

print(df_with_messages.head())
# Output:
#                  timestamp   value  status          source  message
# 0  2025-11-23T23:10:00Z    8.72       0  local-onedrive  Timestamp: 2025-11-23T23:10:00Z | Value: 8.72 | Status: 0
# 1  2025-11-23T23:20:00Z    9.02       0  local-onedrive  Timestamp: 2025-11-23T23:20:00Z | Value: 9.02 | Status: 0

# Use for sending messages
for idx, row in df_with_messages.iterrows():
    print(f"Row {idx}: {row['message']}")
```

### Source Identifiers (Recommended)
- `'local-onedrive'` - From local OneDrive sync
- `'sharepoint'` - From SharePoint Online
- `'local-file'` - From local filesystem
- `'api'` - From external API

---

## Complete Workflow Example

### Scenario: Process wind data from OneDrive

```python
import pandas as pd
from bkw_automation.formatters import formatdkw, format_csv_data, add_message_columns
from pathlib import Path

# 1. Load data from OneDrive
onedrive_path = Path.home() / 'OneDrive' / 'Data' / 'winddata.csv'
df = pd.read_csv(onedrive_path)

# 2. Parse if needed
if len(df.columns) == 1 and ';' in str(df.columns[0]):
    df = format_csv_data(df, sep=';')

# 3. Format using DKW formatter
df = formatdkw(df)

# 4. Add message structure
df = add_message_columns(df, source='local-onedrive')

# 5. Save formatted output
output_path = Path.home() / 'OneDrive' / 'Processed' / 'winddata_formatted.csv'
df.to_csv(output_path, index=False, sep=';')

# 6. Display messages
print("Generated Messages:")
for idx, row in df.head(3).iterrows():
    print(f"{row['message']}")
```

---

## Error Handling

### Common Errors and Solutions

#### `KeyError: 'timestamp'`
**Cause:** Input DataFrame missing expected columns  
**Solution:** Check column names and use `df.columns` to verify

#### `ValueError: Unable to parse data`
**Cause:** Data format doesn't match expected structure  
**Solution:** Inspect data with `df.head()` and `df.dtypes`

#### `AttributeError: 'NoneType' object has no attribute 'columns'`
**Cause:** DataFrame is None or not loaded  
**Solution:** Verify data loading step completed successfully

### Error Handling Pattern

```python
try:
    df = formatdkw(df)
except KeyError as e:
    print(f"Column not found: {e}")
    print(f"Available columns: {df.columns.tolist()}")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
```

---

## Performance Considerations

### Large Datasets
For datasets with >1M rows:

```python
# Process in chunks
chunk_size = 100000
chunks = []

for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    chunk = formatdkw(chunk)
    chunks.append(chunk)

df = pd.concat(chunks, ignore_index=True)
```

### Memory Optimization
```python
# Specify dtypes to reduce memory usage
dtypes = {
    'timestamp': 'object',
    'value': 'float32',
    'status': 'int8'
}

df = pd.read_csv('file.csv', dtype=dtypes)
df = formatdkw(df)
```

---

## Data Type Information

### Input Data Types (formatdkw)
- timestamp: string or datetime
- value: numeric (int, float)
- status: numeric (int, float)

### Output Data Types (formatdkw)
- timestamp: object (string)
- value: varies (preserves input type)
- status: int (0 or -1)

### Message Columns Data Types
- source: object (string)
- message: object (string)

---

## Integration with Other Modules

### Using with SharePoint Client
```python
from bkw_automation.sharepoint_client import SharePointClient
from bkw_automation.formatters import formatdkw, add_message_columns

sp_client = SharePointClient(...)
# ... download file ...

df = pd.read_csv('downloaded_file.csv')
df = formatdkw(df)
df = add_message_columns(df, source='sharepoint')
```

### Using with Transformers
```python
from bkw_automation.transformers import *
from bkw_automation.formatters import formatdkw

df = load_data()
df = formatdkw(df)
# ... apply other transformations ...
```

---

## Version Information

- **Version:** 1.0
- **Created:** December 16, 2025
- **Python Version:** 3.9+
- **Dependencies:** pandas, numpy (optional)

---

## Support & Troubleshooting

For issues:
1. Check the examples above
2. Review error messages and stack traces
3. Verify input data format with `df.head()` and `df.dtypes`
4. Check the relevant notebook's troubleshooting section
5. Review logs in `logs/` folder

---

**Last Updated:** December 16, 2025
