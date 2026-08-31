
function Write-LogFile() {
    [CmdletBinding()]
    param (
        [Parameter()]
        [string]
        $Message,

        [ValidateSet("Yellow", "Red", "Green")]
        [Parameter()]
        [String]
        $Color
    )
    <#
    .NOTES
    Log will be stored within the directory the script is ran from, and will be named after the script from which calls this function
    #>
    
    # if you want the log to be created where the executing script lives
    # $OutputDir = "$(Split-Path -Path $PSCommandPath)\Logs"

    # if log should be created at the location in which the script was ran
    $OutputDir = "$(Get-Location)\Logs"
    if (!(test-path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir > $null
        Write-Verbose -Message "Created directory: $OutputDir"
    }

    $scriptName = $MyInvocation.MyCommand.Name
    $OutputFile = "$($scriptName)-$(Get-Date -Format 'yyyy-MM-dd').log"
    $logFile = "$OutputDir\$OutputFile"

    $scriptName
    $outputFile
    $logFile


    switch ($color) {
        "Yellow" { [Console]::ForegroundColor = [ConsoleColor]::Yellow }
        "Red" { [Console]::ForegroundColor = [ConsoleColor]::Red }
        "Green" { [Console]::ForegroundColor = [ConsoleColor]::Green }
        default { [Console]::ResetColor() }
    }

    [Console]::WriteLine($message)
    [Console]::ResetColor()
    $logToWrite = [DateTime]::Now.ToString() + ": " + $message
    $logToWrite | Out-File -FilePath $LogFile -Append
}

Write-LogFile -message "[TEST] testing XXX" -Color Yellow