Function Get-RequiredModules {
    <#
    .DESCRIPTION 
    Get-Required is used to install and then import a specified PowerShell module.
    
    .PARAMETER Module
    parameter specifices the PowerShell module to install. 
    #>

    [CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $Module        
    )
    
    try {
        $installedModule = Get-InstalledModule -Name $Module -ErrorAction SilentlyContinue       

        if ($null -eq $installedModule) {
            Write-Host "The $Module PowerShell module was not found" 
            #check for Admin Privleges
            $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

            if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
                #Not an Admin, install to current user            
                Write-Host "Can not install the $Module module. You are not running as Administrator" 
                Write-Host "Installing $Module module to current user Scope" 
                
                Install-Module -Name $Module -Scope CurrentUser -Repository PSGallery -Force -AllowClobber
                $latestVersion = [Version](Get-Module -Name $Module).Version  

                Write-Host "Importing module $Module with version $latestVersion" -LogFileName $LogFileName -Severity Information

                Import-Module -Name $Module -RequiredVersion $latestVersion -Force
            }
            else {
                #Admin, install to all users																		   
                Write-Host "Installing the $Module module to all users" 

                Install-Module -Name $Module -Repository PSGallery -Force -AllowClobber

                $latestVersion = [Version](Get-Module -Name $Module).Version   

                Write-Host "Importing module $Module with version $latestVersion" -LogFileName $LogFileName -Severity Information

                Import-Module -Name $Module -RequiredVersion $latestVersion -Force
            }
        }
        else {
            if ($UpdateAzModules) {
                Write-Host "Checking updates for module $Module" -LogFileName $LogFileName -Severity Information
                $currentVersion = [Version](Get-InstalledModule | Where-Object { $_.Name -eq $Module }).Version
                # Get latest version from gallery
                $latestVersion = [Version](Find-Module -Name $Module).Version
                if ($currentVersion -ne $latestVersion) {
                    #check for Admin Privleges
                    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

                    if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
                        #install to current user            
                        Write-Host "Can not update the $Module module. You are not running as Administrator" 
                        Write-Host "Updating $Module from [$currentVersion] to [$latestVersion] to current user Scope" 
                        Update-Module -Name $Module -RequiredVersion $latestVersion -Force
                    }
                    else {
                        #Admin - Install to all users																		   
                        Write-Host "Updating $Module from [$currentVersion] to [$latestVersion] to all users" 
                        Update-Module -Name $Module -RequiredVersion $latestVersion -Force
                    }
                }
                else {
                    $latestVersion = [Version](Get-Module -Name $Module).Version               
                    Write-Host "Importing module $Module with version $latestVersion" -LogFileName $LogFileName -Severity Information
                    Import-Module -Name $Module -RequiredVersion $latestVersion -Force
                }
            }
            else {
                $latestVersion = [Version](Get-Module -Name $Module).Version               
                Write-Host "Importing module $Module with version $latestVersion" -LogFileName $LogFileName -Severity Information

                Import-Module -Name $Module -RequiredVersion $latestVersion -Force
            }
        }
        # Install-Module will obtain the module from the gallery and install it on your local machine, making it available for use.
        # Import-Module will bring the module and its functions into your current powershell session, if the module is installed.  
    }
    catch {
        Write-Host "An error occurred in Get-RequiredModules() method - $($_)" -LogFileName $LogFileName -Severity Error        
    }
}