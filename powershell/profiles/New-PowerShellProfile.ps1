# Define the script
function New-PowerShellProfile {
    # Get the path of the current user's PowerShell profile
    $ProfilePath = $PROFILE
    $ProfileDirectory = Split-Path -Path $ProfilePath -Parent
    $FunctionsDirectory = Join-Path -Path $ProfileDirectory -ChildPath "profile-functions"

    try {
        # Check if the profile directory exists, and create it if necessary
        if (-not (Test-Path -Path $ProfileDirectory)) {
            New-Item -ItemType Directory -Path $ProfileDirectory -Force | Out-Null
            Write-Host "Created profile directory: $ProfileDirectory" -ForegroundColor Green
        }

        # Check if the profile file exists, and create it if necessary
        if (-not (Test-Path -Path $ProfilePath)) {
            New-Item -ItemType File -Path $ProfilePath -Force | Out-Null
            Write-Host "Created PowerShell profile: $ProfilePath" -ForegroundColor Green
        }
        else {
            Write-Host "PowerShell profile already exists: $ProfilePath" -ForegroundColor Yellow
        }

        # Check if the "profile-functions" directory exists, and create it if necessary
        if (-not (Test-Path -Path $FunctionsDirectory)) {
            New-Item -ItemType Directory -Path $FunctionsDirectory -Force | Out-Null
            Write-Host "Created 'profile-functions' directory: $FunctionsDirectory" -ForegroundColor Green
        }
        else {
            Write-Host "'profile-functions' directory already exists: $FunctionsDirectory" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Error "An error occurred: $_"
    }
}