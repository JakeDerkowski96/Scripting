function Test-AdminPrivileges {
    <#
    .DESCRIPTION
    Tell you if the user whor ran the current script was an admin or not
    .EXAMPLE
    $isAdminResult = Test-AdminPrivileges
    if ($isAdminResult) {
        Write-Host "Admin privileges detected."
    }
    else {
        Write-Host "Not running as an administrator."
    }
    #>
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    return $isAdmin
}

# Example usage:

