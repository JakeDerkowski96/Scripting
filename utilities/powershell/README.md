# PowerShell Toolkit

A general-purpose PowerShell library: reusable helper functions, a packaged module, and
profile-setup tooling. Consolidated here from a former standalone repository.

## helpers/

Standalone functions covering common needs — path/existence validation (`Test-*`),
authentication and module checks (`Confirm-*`), file operations (`Copy-FilesRecursively`,
`Build-FilesFromContent`), JSON cleanup (`Clean-Json`, `Remove-NullProperties`),
logging (`Write-Log`), and shell conveniences (`Create-DesktopShortcut`, `Set-GitUser`).
Dot-source an individual function to use it:

```powershell
. ./helpers/Test-AdminPrivilege.ps1
if (-not (Test-AdminPrivilege)) { Write-Warning "Run elevated." }
```

## module/

`FrequentFunctions` — the frequently used helpers packaged as an importable module —
plus tooling to scaffold and update custom modules (`New-CustomModule.ps1`,
`Update-CustomModule.ps1`, `Install-Modules.ps1`).

```powershell
Import-Module ./module/FrequentFunctions/FrequentFunctions.psd1
```

## profile/

Scripts to generate and test a PowerShell profile (`New-PowerShellProfile.ps1`,
`Test-Profile.ps1`) plus a reference `pwsh-profile.ps1`.
