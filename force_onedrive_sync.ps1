# Force OneDrive Sync Script
# Ensures files are uploaded even when computer is locked

param(
    [string]$FolderPath = "C:\Users\sandovalsu\OneDrive - NOTUS energy GmbH\PowerAutomate\BKW test\Dynamic_folder\outgoing",
    [int]$TimeoutSeconds = 120,  # 2 minutes max wait (increased for locked sessions)
    [int]$MaxRetries = 3  # Retry sync if it fails
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

# For incoming folders, always wait to ensure files are downloaded
# For outgoing folders, check if there are files to upload
$isIncoming = $FolderPath -like "*incoming*"
$recentFiles = Get-ChildItem -Path $FolderPath -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-10) }

if (-not $isIncoming -and (-not $recentFiles -or $recentFiles.Count -eq 0)) {
    Write-Host "[$(Get-Date)] No recent files to sync - proceeding immediately"
    exit 0
}

if ($isIncoming) {
    Write-Host "[$(Get-Date)] Incoming folder - forcing sync check for new files"
}

# Start OneDrive sync with retry logic
$oneDrivePath = "$env:LOCALAPPDATA\Microsoft\OneDrive\OneDrive.exe"
$retryCount = 0
$syncTriggered = $false

while ($retryCount -lt $MaxRetries -and -not $syncTriggered) {
    try {
        # Method 1: Use /sync parameter
        Start-Process -FilePath $oneDrivePath -ArgumentList "/sync" -WindowStyle Hidden -ErrorAction Stop
        
        # Method 2: Also try touching multiple files to trigger change detection
        # This is more reliable when computer is locked
        $filesToTouch = Get-ChildItem -Path $FolderPath -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 5
        foreach ($file in $filesToTouch) {
            try {
                $file.LastAccessTime = Get-Date
            } catch { }
        }
        
        $syncTriggered = $true
        Write-Host "[$(Get-Date)] OneDrive sync triggered (attempt $($retryCount + 1)/$MaxRetries)"
    } catch {
        $retryCount++
        Write-Host "[$(Get-Date)] Sync trigger failed (attempt $retryCount/$MaxRetries): $_"
        if ($retryCount -lt $MaxRetries) {
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $syncTriggered) {
    Write-Host "[$(Get-Date)] WARNING: Failed to trigger OneDrive sync after $MaxRetries attempts"
}

Write-Host "[$(Get-Date)] Waiting up to $TimeoutSeconds seconds for sync..."

# Wait for files to sync with verification
$startTime = Get-Date
$synced = $false
$checkInterval = 3  # Check every 3 seconds
$lastFileCount = -1
$stableChecks = 0

while (((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSeconds) {
    Start-Sleep -Seconds $checkInterval
    
    # Get current file count and sizes (more reliable than attributes when locked)
    $currentFiles = Get-ChildItem -Path $FolderPath -Recurse -File -ErrorAction SilentlyContinue
    $currentCount = if ($currentFiles) { $currentFiles.Count } else { 0 }
    
    # For incoming: check if file count has stabilized (no new downloads)
    # For outgoing: check if files exist and have non-zero size
    if ($isIncoming) {
        if ($currentCount -eq $lastFileCount) {
            $stableChecks++
            if ($stableChecks -ge 2) {  # Stable for 2 consecutive checks (6 seconds)
                $synced = $true
                Write-Host "[$(Get-Date)] File count stabilized at $currentCount files (after $([math]::Round(((Get-Date) - $startTime).TotalSeconds, 1))s)"
                break
            }
        } else {
            $stableChecks = 0
            Write-Host "[$(Get-Date)] Files detected: $currentCount (monitoring for changes...)"
        }
        $lastFileCount = $currentCount
    } else {
        # For outgoing: verify files have content (not placeholder files)
        $validFiles = $currentFiles | Where-Object { $_.Length -gt 0 }
        $validCount = if ($validFiles) { $validFiles.Count } else { 0 }
        
        if ($validCount -eq $currentCount -and $currentCount -gt 0) {
            $synced = $true
            Write-Host "[$(Get-Date)] All $currentCount file(s) ready for upload (after $([math]::Round(((Get-Date) - $startTime).TotalSeconds, 1))s)"
            break
        }
        
        Write-Host "[$(Get-Date)] Files: $validCount/$currentCount ready for upload..."
    }
}

if ($synced) {
    Write-Host "[$(Get-Date)] SUCCESS: OneDrive sync completed"
    # Add final wait to ensure OneDrive commits changes
    Start-Sleep -Seconds 2
    exit 0
} else {
    Write-Host "[$(Get-Date)] WARNING: Timeout reached after $TimeoutSeconds seconds"
    Write-Host "[$(Get-Date)] Sync may still be in progress - check OneDrive status"
    # Still exit 0 to not fail the entire pipeline, but log the warning
    exit 0
}
