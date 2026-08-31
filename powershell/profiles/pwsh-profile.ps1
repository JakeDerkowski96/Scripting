# Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Azure Active Directory
if ($host.Name -eq 'ConsoleHost') { Import-Module PSReadLine }
Import-Module AzureAD
Import-Module Az.Accounts
# Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Chocolatey profile
$ChocolateyProfile = "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
if (Test-Path($ChocolateyProfile)) {
    Import-Module "$ChocolateyProfile"
}
# SHELL APPEARANCE AND BEHAVIORS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function Get-Loc { Split-Path -leaf -path (Get-Location) }

function Prompt {
    $colorTable = @{
        "Reset"  = "`e[0m";
        "Red"    = "`e[31;1m";
        "Green"  = "`e[32;1m";
        "Yellow" = "`e[33;1m";
        "Grey"   = "`e[37;0m";
        "White"  = "`e[37;1m";
        "Invert" = "`e[7m";
        "RedBg"  = "`e[41m";
        "CyanBg" = "`e[46m";
    }

    $CurrentDir = (Get-Loc)

    switch ($CurrentDir -like "$($env:USERPROFILE)*") {
        $true {
            $CurrentDir = $CurrentDir.Replace($env:USERPROFILE)
            $CurrentDir = (Get-Loc)
            break
        }

        Default {
            break
        }
    }

    $promptText = "$($colorTable.Reset)$($colorTable.Yellow)[$env:COMPUTERNAME]:$($colorTable.Reset)$($colorTable.Green)[$($CurrentDir)]$($colorTable.Reset)$($promptKey)$($colorTable.Reset)"

    "${promptText} "
}

if ($Host.USI.RawUI.WindowTitle -like "*administrator*") {
    $Host.UI.RawUI.ForegroundColor = "Red"
}
# SHELL APPEARANCE AND BEHAVIORS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$myFunctionPath = "${myPwsh}\Functions\profile-functions"
if(!(Test-Path -Path $myFunctionPath)){
    Write-Host -ForegroundColor Yellow "Creating directory to store custom functions in at $myFunctionPath"
    New-Item -Path $myFunctionPath -ItemType Directory
}

function Import-Functions {
    param(
        [Parameter(Mandatory)][string]$functionPath
    )
    $functionFiles = Get-ChildItem -Path $functionPath -Filter "*.ps1"
    
    # loop an try to import the function
    foreach ($file in $functionFiles) {
        try {
            . $file.FullName
            Write-Verbose -Message "Successfully imported $($file.BaseName)"
            
        }
        catch {
            Write-Verbose -Message "Failed to import $($file.BaseName)"
        }
    }
}

Import-Functions -functionPath $myFunctionPath

# ~~~~ FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Quickly perform commands(s)                                                            
function Update-Powershell { iex "& { $(irm https://aka.ms/install-powershell.ps1) } -UseMSI" }
function subl { &"${Env:ProgramFiles}\Sublime Text 3\sublime_text.exe" $args }
function Show-ShellVars { (dir variable:).where({ $_.options -match 'allscope' }) };
function Show-ENVVars { gci env:* | sort-object name; }
# ~~~~ SHORTCUTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Quickly naviagate to commonly used directories
$OnedrivePath = "$($Env:USERPROFILE)\OneDrive"
function Go-1drive { cd $OnedrivePath; }
function Go-myDocs { cd "$($OnedrivePath)\Documents" }
function Go-Workspace { cd "$($OnedrivePath)\Workspace" }
function Go-tmp { cd "$($OnedrivePath)\tmp" }
