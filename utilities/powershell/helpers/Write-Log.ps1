# Global Log function for writing logs to a file with severity level and error handling
function Write-Log {
    <#
    .SYNOPSIS
    Writes a message to a specified log file with a timestamp and severity level.

    .DESCRIPTION
    This function logs a message to a specified file. Each log entry includes:
    - A timestamp in the format 'yyyy-MM-dd HH:mm:ss'
    - A severity level (Info, Warning, Error)
    - The message to be logged

    If writing to the log file fails (e.g., due to permissions or file lock issues), 
    the function captures the error and displays it as a PowerShell error message.

    .PARAMETER Message
    The message to be written to the log file.

    .PARAMETER LogFile
    The full path of the log file where the message should be written.
    If no file is specified, no action is taken.

    .PARAMETER Severity
    The severity level of the log message. Valid values are:
    - Info: For general informational messages
    - Warning: For potential issues or warnings
    - Error: For critical issues or failures

    Default value is 'Info'.

    .EXAMPLE
    Write-Log -Message "Process started successfully." -LogFile "C:\Logs\MyLogFile.txt" -Severity "Info"

    Logs an informational message in the specified log file.

    .EXAMPLE
    Write-Log -Message "Disk space running low." -LogFile "C:\Logs\MyLogFile.txt" -Severity "Warning"

    Logs a warning message in the specified log file.

    .EXAMPLE
    Write-Log -Message "Failed to connect to the database." -LogFile "C:\Logs\MyLogFile.txt" -Severity "Error"

    Logs an error message in the specified log file.

    .NOTES
    If the log file does not exist, it will be created. Ensure the user running the script 
    has write permissions to the specified file path.
    #>
    param (
        [string]$Message, # The log message to write
        [string]$LogFile, # Path to the log file
        [ValidateSet("Info", "Warning", "Error")]
        [string]$Severity = "Info"  # Log message severity level
    )

    try {
        if ($LogFile) {
            # Format the log entry with a timestamp, severity level, and message
            $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
            $logEntry = "$timestamp [$Severity] $Message"

            # Write the log entry to the file
            Add-Content -Path $LogFile -Value $logEntry
        }
    }
    catch {
        # If writing to the log fails, display an error message
        Write-Error "Failed to write to log file '$LogFile': $_"
    }
}
