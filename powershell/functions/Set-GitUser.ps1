function Set-GitUser {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Email,

        [Parameter()]
        [string]$RepositoryPath = $null, # Set null for global

        [switch]$Global
    )

    # Check if Git is installed
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "Git is not installed or not available in PATH."
        return
    }

    try {
        if ($Global -or -not $RepositoryPath) {
            # Set global Git user
            git config --global user.name $Name
            git config --global user.email $Email
            Write-Host "Global Git user updated: $Name <$Email>" -ForegroundColor Green
        } else {
            # Set repository-specific Git user
            if (-not (Test-Path $RepositoryPath)) {
                Write-Error "Repository path '$RepositoryPath' does not exist."
                return
            }

            Set-Location -Path $RepositoryPath
            git config user.name $Name
            git config user.email $Email
            Write-Host "Git user updated for repository '$RepositoryPath': $Name <$Email>" -ForegroundColor Green
        }

        # Verify the configuration
        Write-Host "Current Git Configuration:"
        if ($Global -or -not $RepositoryPath) {
            git config --global --list
        } else {
            git config --list
        }
    } catch {
        Write-Error "An error occurred while setting the Git user: $_"
    }
}
