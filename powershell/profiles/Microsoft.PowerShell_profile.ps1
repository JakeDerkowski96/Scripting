
# Ensure RemoteSigned scripts can execute for the current user
if ((Get-ExecutionPolicy -Scope CurrentUser) -ne 'RemoteSigned') {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
}

# ~~~~ MODULES (GIT + AUTOCOMPLETION) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Import-Module posh-git -ErrorAction SilentlyContinue
if (-not (Get-Module PSReadLine)) { Import-Module PSReadLine -ErrorAction SilentlyContinue }

# Predictive IntelliSense from history, menu-style tab completion, no bell
Set-PSReadLineOption -PredictionSource History
Set-PSReadLineOption -PredictionViewStyle ListView
Set-PSReadLineOption -BellStyle None
Set-PSReadLineOption -HistorySearchCursorMovesToEnd
Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward

# SHELL APPEARANCE AND BEHAVIORS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function Get-Loc {
    $path = (Get-Location).Path
    if ($path -eq $env:USERPROFILE) { return '~' }
    $leaf = Split-Path -Path $path -Leaf
    if ([string]::IsNullOrEmpty($leaf)) { return $path }
    return $leaf
}

function Get-GitPromptSegment {
    if (-not (Get-Command Get-GitStatus -ErrorAction SilentlyContinue)) { return '' }
    $gitStatus = Get-GitStatus
    if (-not $gitStatus) { return '' }

    $dirty  = if ($gitStatus.HasWorking -or $gitStatus.HasIndex) { '*' } else { '' }
    $ahead  = if ($gitStatus.AheadBy -gt 0) { "`u{2191}$($gitStatus.AheadBy)" } else { '' }
    $behind = if ($gitStatus.BehindBy -gt 0) { "`u{2193}$($gitStatus.BehindBy)" } else { '' }

    " `e[35;1m($($gitStatus.Branch)$dirty$ahead$behind)`e[0m"
}

function Prompt {
    $colorTable = @{
        Reset  = "`e[0m"
        Red    = "`e[31;1m"
        Green  = "`e[32;1m"
        Yellow = "`e[33;1m"
        Grey   = "`e[37;0m"
        White  = "`e[37;1m"
        Invert = "`e[7m"
        RedBg  = "`e[41m"
        CyanBg = "`e[46m"
    }

    $currentDir = Get-Loc
    $gitSegment = Get-GitPromptSegment
    $promptChar = if (Test-IsAdmin) { '#' } else { '$' }

    "$($colorTable.Reset)$($colorTable.Yellow)[$env:COMPUTERNAME]:$($colorTable.Reset)$($colorTable.Green)[$currentDir]$($colorTable.Reset)$gitSegment $promptChar "
}

# Check if the current session is running as administrator
function Test-IsAdmin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Tint the console red when running as administrator
if (Test-IsAdmin) {
    $host.UI.RawUI.ForegroundColor = "Red"
}


# ~~~~ FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function Update-Powershell { Invoke-Expression "& { $(Invoke-RestMethod https://aka.ms/install-powershell.ps1) } -UseMSI" }

function subl { &"${Env:ProgramFiles}\Sublime Text 3\sublime_text.exe" $args }

function cdrepos { Set-Location $myRepos }

function Show-ShellVar { (Get-ChildItem variable:).where({ $_.options -match 'allscope' }) }

function Show-EnvVar { Get-ChildItem env:* | Sort-Object Name }

# ~~~~ VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
. "$PSScriptRoot\variables.ps1"

# ~~~~ FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function Import-Functions {
    param(
        [Parameter(Mandatory)][string]$functionPath
    )
    if (-not (Test-Path $functionPath)) { return }

    foreach ($file in Get-ChildItem -Path $functionPath -Filter '*.ps1') {
        try {
            . $file.FullName
            Write-Verbose "Successfully imported $($file.BaseName)"
        }
        catch {
            Write-Warning "Failed to import $($file.BaseName): $_"
        }
    }
}

Import-Functions -functionPath $myFunctionPath
