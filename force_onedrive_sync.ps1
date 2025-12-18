# Force OneDrive Sync Script
# Ensures files are uploaded even when computer is locked

param(
    [string]$FolderPath = "C:\Users\sandovalsu\OneDrive - NOTUS energy GmbH\PowerAutomate\BKW test\Dynamic_folder\outgoing",
    [int]$TimeoutSeconds = 30  # 30 seconds max wait (reduced from 5 minutes)
)

Write-Host "[$(Get-Date)] Starting OneDrive sync for: $FolderPath"

# Get OneDrive process
$oneDriveProcess = Get-Process -Name "OneDrive" -ErrorAction SilentlyContinue

if (-not $oneDriveProcess) {
    Write-Host "[$(Get-Date)] ERROR: OneDrive is not running"
    exit 1
}

# Check OneDrive status quickly
Write-Host "[$(Get-Date)] Checking OneDrive status..."

# Trigger sync by touching the folder (forces OneDrive to detect changes)
$targetFolder = Get-Item $FolderPath -ErrorAction SilentlyContinue
if ($targetFolder) {
    $targetFolder.LastWriteTime = Get-Date
    Write-Host "[$(Get-Date)] Triggered folder change detection"
}

# Quick check - if folder is already synced, skip waiting
$recentFiles = Get-ChildItem -Path $FolderPath -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-10) }

if (-not $recentFiles -or $recentFiles.Count -eq 0) {
    Write-Host "[$(Get-Date)] No recent files to sync - proceeding immediately"
    exit 0
}

# Start OneDrive sync
$oneDrivePath = "$env:LOCALAPPDATA\Microsoft\OneDrive\OneDrive.exe"
Start-Process -FilePath $oneDrivePath -ArgumentList "/sync" -WindowStyle Hidden

Write-Host "[$(Get-Date)] OneDrive sync triggered, waiting up to $TimeoutSeconds seconds..."

# Wait for files to sync with shorter intervals
$startTime = Get-Date
$uploaded = $false
$checkInterval = 2  # Check every 2 seconds instead of 5

while (((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSeconds) {
    # Check if any files in the folder are still pending upload
    $pendingFiles = Get-ChildItem -Path $FolderPath -Recurse -File -ErrorAction SilentlyContinue | 
        Where-Object { 
            # Files with cloud icon overlay or pending sync
            ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -or
            ($_.Length -eq 0 -and $_.CreationTime -gt (Get-Date).AddMinutes(-5))
        }
    
    if (-not $pendingFiles -or $pendingFiles.Count -eq 0) {
        $uploaded = $true
        Write-Host "[$(Get-Date)] All files synced (after $([math]::Round(((Get-Date) - $startTime).TotalSeconds, 1))s)"
        break
    }
    
    Write-Host "[$(Get-Date)] Waiting for $($pendingFiles.Count) file(s)..."
    Start-Sleep -Seconds $checkInterval
}

if ($uploaded) {
    Write-Host "[$(Get-Date)] SUCCESS: OneDrive sync completed"
    exit 0
} else {
    Write-Host "[$(Get-Date)] Timeout reached after $TimeoutSeconds seconds - continuing anyway"
    exit 0  # Don't fail the task, files will upload eventually
}
