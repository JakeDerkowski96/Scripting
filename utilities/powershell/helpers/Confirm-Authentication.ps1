function Confirm-Authentication {
    <#
    .NOTES
    This is incomplete but is intended to cover all authentication that I use, so multiple functions are not necessary
    #>
    param(
        [ValidateSetAttribute('Azure', 'Entra', 'Exchange', 'Purview')]
        [Parameter(Mandatory)][string]$AuthType
    )

    switch ($AuthType) {
        'Azure' {
            if ($null -eq $(Get-AzContext)) {
                try {
                    $Conn = Connect-AzAccount
                    if ($null -ne $Conn) {
                        Write-Host -ForegroundColor "Successful authenticated with $($conn.Context.Account.Id)"
                        return 0
                    }
                    else {
                        Write-Host -ForegroundColor Red "Failed to authenticate to Azure"
                        return 1
                    }
                }
                catch {
                    Write-Host -ForegroundColor Red "Failed to authenticate to Azure"
                }        
            }
            else {
                Write-Host -ForegroundColor Green "A connection has already been established with $($conn.Context.Account.Type) to $($conn.Context.Account.Id)"
                return 0
            }  
        }
        'Entra' {
            if ($null -eq $(Get-AzureADSignedInUser)) {
                try {
                    
                }
                catch {
                    Write-Host -ForegroundColor Red "Failed Authentication to $AuthType"
                }
            }
        }
        'Exchange' { }
        'Purview' { }
        Default {}
    }      
}