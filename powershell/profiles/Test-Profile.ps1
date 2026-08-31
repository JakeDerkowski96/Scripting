# Function to create a PowerShell profile if it doesn't exist
function Confirm-PowerShellProfile {
    param (
        [switch]$OpenProfile  # Optional parameter to open the profile after creating it
    )

    # Get the current user's PowerShell profile path
    $profilePath = $PROFILE

    # Check if the profile file exists
    if (-Not (Test-Path -Path $profilePath)) {
        Write-Host "PowerShell profile does not exist. Creating it now..." -ForegroundColor Yellow
        
        # Ensure the directory exists
        $profileDirectory = Split-Path -Path $profilePath
        if (-Not (Test-Path -Path $profileDirectory)) {
            New-Item -ItemType Directory -Path $profileDirectory -Force | Out-Null
            Write-Host "Created directory: $profileDirectory" -ForegroundColor Green
        }

        # Create an empty profile file
        New-Item -ItemType File -Path $profilePath -Force | Out-Null
        Write-Host "Created PowerShell profile: $profilePath" -ForegroundColor Green
    }
    else {
        Write-Host "PowerShell profile already exists: $profilePath" -ForegroundColor Cyan
    }

    # Optionally open the profile for editing
    if ($OpenProfile) {
        Write-Host "Opening the PowerShell profile for editing..." -ForegroundColor Cyan
        code $profilePath
    }
}

# Run the function
# Confirm-PowerShellProfile -OpenProfile
