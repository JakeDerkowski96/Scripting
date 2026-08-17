function Write-Log {
    param (
        [string]$Message,
        [string]$Severity = "INFO",
        [string]$LogFilePath = "$PSScriptRoot\pwsh_scripts.log"
    )

    # List of acceptable severity levels
    $validSeverities = @("INFO", "WARNING", "ERROR", "CRITICAL")

    # Validate severity level
    if ($Severity -notin $validSeverities) {
        throw "Invalid severity level: $Severity. Acceptable values are: $($validSeverities -join ', ')"
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp [$Severity] - $Message"
    Add-Content -Path $LogFilePath -Value $logMessage
}

function Get-ModuleVersion {
    param (
        [string]$ModulePath
    )
    $psd1File = Get-ChildItem -Path $ModulePath -Filter *.psd1 -ErrorAction SilentlyContinue
    if ($null -ne $psd1File) {
        $psd1Content = Get-Content -Path $psd1File.FullName -Raw | Out-String | ConvertFrom-StringData
        return $psd1Content.ModuleVersion
    }
    return $null
}

function New-PowerShellModule {
    param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$FunctionsDirectory,

        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$ModuleName
    )

    $ErrorActionPreference = 'Stop'

    try {
        # Validate Functions Directory
        if (-not (Test-Path -Path $FunctionsDirectory -PathType Container)) {
            throw "The specified functions directory does not exist: $FunctionsDirectory"
        }

        # Create Module Directory
        $ModulePath = Join-Path -Path $FunctionsDirectory -ChildPath $ModuleName
        if (-not (Test-Path -Path $ModulePath)) {
            New-Item -Path $ModulePath -ItemType Directory
            Write-Log -Message "Created module directory: $ModulePath" -Severity "INFO"
        }

        # Check for existing module version
        $existingVersion = Get-ModuleVersion -ModulePath $ModulePath
        if ($null -eq $existingVersion) {
            $ModuleVersion = "1.0.0"
        }
        else {
            $incrementVersion = Read-Host "Existing module version $existingVersion found. Do you want to increment the version? (Y/N)"
            if ($incrementVersion -eq "Y") {
                $versionComponents = $existingVersion.Split('.')
                $versionComponents[2] = [int]$versionComponents[2] + 1
                $ModuleVersion = "$($versionComponents[0]).$($versionComponents[1]).$($versionComponents[2])"
            }
            else {
                $ModuleVersion = $existingVersion
            }
        }

        # Create .psm1 file
        $Psm1Path = Join-Path -Path $ModulePath -ChildPath "$ModuleName.psm1"
        if (-not (Test-Path -Path $Psm1Path)) {
            New-Item -Path $Psm1Path -ItemType File
            $FunctionFiles = Get-ChildItem -Path $FunctionsDirectory -Filter *.ps1
            foreach ($FunctionFile in $FunctionFiles) {
                $FunctionContent = Get-Content -Path $FunctionFile.FullName -Raw
                Add-Content -Path $Psm1Path -Value $FunctionContent
            }
            Write-Log -Message "Created .psm1 file: $Psm1Path" -Severity "INFO"
        }

        # Create .psd1 file
        $Psd1Path = Join-Path -Path $ModulePath -ChildPath "$ModuleName.psd1"
        if (-not (Test-Path -Path $Psd1Path)) {
            $Psd1Content = @"
@{
    RootModule = '$ModuleName.psm1'
    ModuleVersion = '$ModuleVersion'
    GUID = '$(New-Guid)'
    Author = 'Your Name'
    CompanyName = 'Your Company'
    Copyright = '(c) $(Get-Date -Format yyyy) Your Name. All rights reserved.'
    FunctionsToExport = @()
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
"@
            Set-Content -Path $Psd1Path -Value $Psd1Content
            Write-Log -Message "Created .psd1 file: $Psd1Path" -Severity "INFO"
        }

        Write-Log -Message "PowerShell module $ModuleName created successfully." -Severity "INFO"
    }
    catch {
        Write-Log -Message "Error: $_" -Severity "ERROR"
        throw
    }
}

# Example usage:
New-PowerShellModule -FunctionsDirectory "C:\Path\To\Functions" -ModuleName "MyCustomModule"
