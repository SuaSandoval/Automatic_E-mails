# BKW Daily Processing - Scheduling Guide

This guide will help you set up automated daily execution of the BKW data processing pipeline using Windows Task Scheduler.

## Files Overview

1. **run_daily_processing.py** - Main Python script (converted from notebook)
2. **run_processing.bat** - Batch file to launch the script
3. **.env** - Environment configuration (paths, credentials)
4. **logs/** - Processing logs (auto-created)

## Setup Steps

### 1. Verify Python Environment

First, ensure your Python environment is set up correctly:

```powershell
# Navigate to project directory
cd "C:\Users\sandovalsu\Documents\TBF projects\BKW"

# Test the script runs successfully
python run_daily_processing.py
```

### 2. Configure the Batch File

Edit `run_processing.bat` if needed:

- **For Conda users**: Uncomment the conda activate lines
- **For custom Python path**: Uncomment and update the path in Option 3
- **For logging**: The script already creates logs in the `logs/` folder

### 3. Create Scheduled Task

#### Option A: Using Task Scheduler GUI

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click **"Create Basic Task"** in the right panel
3. Configure:
   - **Name**: `BKW Daily Processing`
   - **Description**: `Automated BKW data processing from OneDrive`
   - **Trigger**: Daily
   - **Time**: Choose when to run (e.g., 8:00 AM)
   - **Action**: Start a program
   - **Program/script**: Browse to `run_processing.bat`
   - **Start in**: `C:\Users\sandovalsu\Documents\TBF projects\BKW`
4. Click **Finish**

#### Option B: Using PowerShell (Advanced)

```powershell
# Define task parameters
$taskName = "BKW Daily Processing"
$scriptPath = "C:\Users\sandovalsu\Documents\TBF projects\BKW\run_processing.bat"
$workingDir = "C:\Users\sandovalsu\Documents\TBF projects\BKW"
$runTime = "08:00"  # 8:00 AM

# Create action
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir

# Create trigger (daily at specified time)
$trigger = New-ScheduledTaskTrigger -Daily -At $runTime

# Create settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

# Register task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Automated BKW data processing"
```

### 4. Advanced Task Scheduler Settings

After creating the task, right-click it and select **Properties** to configure:

#### General Tab
- ✅ **Run whether user is logged on or not** (for unattended execution)
- ✅ **Run with highest privileges** (if OneDrive access requires it)

#### Triggers Tab
- Set to run **Daily** at your preferred time (e.g., 8:00 AM)
- Enable **"Stop task if it runs longer than"**: 1 hour (safety timeout)

#### Actions Tab
- Verify the batch file path is correct
- Ensure **"Start in"** is set to project directory

#### Conditions Tab
- ✅ **Start only if the computer is on AC power** (optional, for laptops)
- ✅ **Wake the computer to run this task** (if computer may be sleeping)
- ✅ **Start only if the following network connection is available**: Any connection

#### Settings Tab
- ✅ **Allow task to be run on demand** (for manual testing)
- ✅ **If the task fails, restart every**: 10 minutes, up to 3 attempts
- ✅ **Stop the task if it runs longer than**: 1 hour

### 5. Test the Scheduled Task

Before relying on it daily, test manually:

1. Open Task Scheduler
2. Find **"BKW Daily Processing"** in the task list
3. Right-click → **Run**
4. Check the `logs/` folder for the generated log file
5. Verify output files were created in your output directories

### 6. Monitor Execution

#### Check Last Run Status
- Open Task Scheduler
- View **Last Run Result** column (0x0 = success, other = error)
- Click on the task → **History** tab for detailed execution logs

#### Check Processing Logs
- Logs are saved to: `C:\Users\sandovalsu\Documents\TBF projects\BKW\logs\`
- Each run creates a timestamped log: `processing_YYYYMMDD_HHMMSS.log`
- Review logs to see:
  - Catalog validation warnings
  - Files processed successfully
  - Any errors or issues

#### Output Verification
- Local output: `C:\Users\sandovalsu\Documents\TBF projects\BKW\data\output\DD-MM-YYYY\`
- OneDrive output: Your configured OneDrive path

## Troubleshooting

### Task Doesn't Run
- Verify batch file path in task action
- Check "Last Run Result" in Task Scheduler
- Ensure "Start in" directory is set correctly
- Review Windows Event Viewer → Task Scheduler logs

### Python Not Found
- Update `run_processing.bat` with full Python path
- Example: `"C:\Python311\python.exe" run_daily_processing.py`

### Permission Errors
- Run task "with highest privileges"
- Ensure OneDrive folders are accessible
- Check file permissions in output directories

### Script Runs But No Output
- Check log files in `logs/` folder
- Verify .env configuration
- Ensure date folder exists in data source
- Run script manually to see real-time errors: `python run_daily_processing.py`

### Catalog or Data Not Found
- Verify paths in `.env` file
- Ensure OneDrive sync is active
- Check that folder structure matches configuration

## Maintenance

### Weekly
- Review log files for warnings/errors
- Verify output files are being created correctly

### Monthly
- Archive old logs (delete logs older than 30 days)
- Check disk space in output directories

### As Needed
- Update catalog (codeids.csv) when new resources added
- Adjust VERBOSE setting if logs are too large
- Update schedule time if business needs change

## Command Reference

### Manual Execution
```powershell
# Run with default settings (today's date)
python run_daily_processing.py

# Run from batch file
.\run_processing.bat
```

### Task Scheduler Commands
```powershell
# List all scheduled tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*BKW*"}

# Check task status
Get-ScheduledTaskInfo -TaskName "BKW Daily Processing"

# Run task manually
Start-ScheduledTask -TaskName "BKW Daily Processing"

# Disable task
Disable-ScheduledTask -TaskName "BKW Daily Processing"

# Enable task
Enable-ScheduledTask -TaskName "BKW Daily Processing"

# Delete task
Unregister-ScheduledTask -TaskName "BKW Daily Processing" -Confirm:$false
```

## Support

If you encounter issues:
1. Check the latest log file in `logs/` folder
2. Run the script manually to see real-time output
3. Verify .env configuration is correct
4. Ensure all required Python packages are installed
5. Check OneDrive sync status

---

**Last Updated**: December 2025
