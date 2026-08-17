
# Function to install Chocolatey packages from a file
function Install-ChocoPackages {
    <#
    .SYNOPSIS
    Installs Chocolatey packages listed in a specified input file.

    .DESCRIPTION
    This function reads a list of package names from an input file and installs them using Chocolatey.
    It includes options for verbose output and logging.

    .PARAMETER InputFile
    The file path containing the list of package names to install. Default is "ChocoPackages.txt".

    .PARAMETER Verbose
    If specified, additional details will be printed to the console during execution.

    .PARAMETER Log
    If specified, actions and errors will be logged to a log file.

    .EXAMPLE
    Install-ChocoPackages -InputFile "C:\Packages.txt" -Verbose -Log

    Installs packages listed in "C:\Packages.txt" with verbose output and logging.

    .NOTES
    Ensure Chocolatey is installed on the system before running this function.
    #>
    param (
        [string]$InputFile = "ChocoPackages.txt",
        [switch]$Verbose,
        [switch]$Log
    )

    try {
        # Check if Chocolatey is installed
        if (-not (Get-Command "choco" -ErrorAction SilentlyContinue)) {
            throw "Chocolatey is not installed on this system. Install it first and try again."
        }

        # Define the log file if logging is enabled
        $LogFile = if ($Log) { "$($InputFile)-install-log.txt" } else { $null }

        Write-Log -Message "Chocolatey detected. Starting package installation process." -LogFile $LogFile -Severity "Info"
        if ($Verbose) { Write-Host "Chocolatey detected. Starting package installation process." }

        # Check if the input file exists
        if (-not (Test-Path $InputFile)) {
            throw "Input file not found: $InputFile"
        }

        # Read the package names from the input file
        $packages = Get-Content -Path $InputFile

        if ($packages.Count -eq 0) {
            throw "No packages listed in $InputFile."
        }

        # Install each package
        foreach ($package in $packages) {
            Write-Log -Message "Installing package: $package" -LogFile $LogFile -Severity "Info"
            if ($Verbose) { Write-Host "Installing package: $package" }
            choco install $package -y
        }

        Write-Log -Message "All packages installed successfully." -LogFile $LogFile -Severity "Info"
        if ($Verbose) { Write-Host "All packages installed successfully." }
    }
    catch {
        Write-Log -Message "Error: $_" -LogFile $LogFile -Severity "Error"
        Write-Error "An error occurred: $_"
    }
}