Function Resolve-TenantDetails {
    <#
    .Synopsis
    ASUMMES THAT THERE HAS ALREADY BEEN A CONNECTION ESTABLISHED
    This function will uses an azure account to create a powershell object that will be used throughout the scripts you see in this repository (and others) to easily and quickly refer to a specific tenant; due to my type of work, this function is primarily interested in the azure details surrounding the location of Microsoft Sentinel.

    .Description
    You will be prompted to login to an azure account of your choosing, the azure context that is created as the result of a successful login is used to search for the location of Microsoft Sentinel. This function will return a powershell object containing the details of this location to be used in later misc. code.

    .Outputs
    a powershell object containing tenant details will be returned, example:

        $tenantExample = @{
            Name = "Azure Tenant or Directory name"
            TenantId = "AzTenantId"
            Workspace = "Sentinel LAW workspace name"
            WorkspaceId = "the Id of workspace above"
            ResourceGroup = "where LAW is located"
            Subscription = "Sub name where Sentinel is located"
            SubscriptionId = "Id of subscription above"
            ResourceId = "Sentinel ResourceId"
        }
    .NOTES
    Requires:
        - Az.Accounts
        - Az.Resources
        - Az.SecurityInsights
        - Az.OperationalInsights
    #>

    [CmdletBinding()]
    param (
        [Parameter()]
        [string]
        $Subscription
    )

    try {
        Select-AzSubscription -Subscription $Subscription
        Write-Verbose -Message "Connection established $(Get-AzContext)"
        
    }
    catch {
        Write-Host -ForegroundColor Red "Failed to connect"
        Exit
    }

    # initiate the object of the details you wish to capture
    # since im in SecOps, I want the Sentinel specific info
    $targetObject = {
        Tenant = $null
        TenantId = $null
        SubscriptionName = $null
        SubscriptionId = $null
        ResourceGroup  = $null
        WorkspaceName  = $null
        WorkspaceId = $null        
    }



    return $targetObject

}