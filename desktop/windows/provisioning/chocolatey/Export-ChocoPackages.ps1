# Function to export a list of installed Chocolatey packages to a file
function Export-ChocoPackages {
    <#
    .SYNOPSIS
    Exports a list of installed Chocolatey packages to a specified file.

    .DESCRIPTION
    This function checks for Chocolatey installation, retrieves a list of all locally installed packages, 
    and writes the package names to an output file. It includes options for verbose output and logging.

    .PARAMETER OutputFile
    The file path where the list of packages will be saved. Default is "ChocoPackages.txt".

    .PARAMETER Verbose
    If specified, additional details will be printed to the console during execution.

    .PARAMETER Log
    If specified, actions and errors will be logged to a log file.

    .EXAMPLE
    Export-ChocoPackages -OutputFile "C:\Packages.txt" -Verbose -Log

    Exports the list of installed Chocolatey packages to "C:\Packages.txt" with verbose output and logging.

    .NOTES
    Ensure Chocolatey is installed on the system before running this function.
    #>
    param (
        [string]$OutputFile = "ChocoPackages.txt",
        [switch]$Verbose,
        [switch]$Log
    )

    try {
        # Check if Chocolatey is installed
        if (-not (Get-Command "choco" -ErrorAction SilentlyContinue)) {
            throw "Chocolatey is not installed on this system. Install it first and try again."
        }

        # Define the log file if logging is enabled
        $LogFile = if ($Log) { "$($OutputFile)-log.txt" } else { $null }

        Write-Log -Message "Chocolatey detected. Retrieving list of installed packages." -LogFile $LogFile -Severity "Info"
        if ($Verbose) { Write-Host "Chocolatey detected. Retrieving list of installed packages." }

        # Retrieve the list of installed packages
        $packages = choco list --local-only | ForEach-Object {
            $_ -split '\|' | Select-Object -First 1
        }

        if ($packages.Count -eq 0) {
            throw "No Chocolatey packages found on this system."
        }

        # Write the package list to the output file
        $packages | Out-File -FilePath $OutputFile -Encoding UTF8
        Write-Log -Message "Successfully exported package list to $OutputFile." -LogFile $LogFile -Severity "Info"
        if ($Verbose) { Write-Host "Successfully exported package list to $OutputFile." }
    }
    catch {
        Write-Log -Message "Error: $_" -LogFile $LogFile -Severity "Error"
        Write-Error "An error occurred: $_"
    }
}
