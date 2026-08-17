# $ExePolicy = Get-ExecutionPolicy
# if ($ExePolicy )


Install-Module PowerShellGet -Force -AllowClobber
Get-Module PowerShellGet, PackageManagement -ListAvailable


winget install Microsoft.PowerShell
winget install Microsoft.VisualStudioCode
winget install chocolately
winget install Microsoft.VisualStudioCode
winget install Microsoft.VisualStudio.2022.Community

choco install powershellget