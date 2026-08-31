function Deploy-ARMTemplate{
    [CmdletBinding()]
    param (
        [Alias("Tenant")]
        [Parameter(Mandatory)]
        $SentinelInstance,
        <#
            .EXAMPLE
            The expected input here is a hash table, essentially containing all required information as seen below:

            $TenantName=@{
                Tenant = DarkCloudSec
                TenantId
                Workspace = WorkspaceNAme
                WorkspaceId = workspace guid
                Subscription = subscriptionName
                SubscriptionId = sub guid
                ResourceGroup = resourceGroupName
            }
        #>
        [Parameter(Mandatory)]
        [string]
        $ARMPath,
        [Parameter()]
        [string]
        $ParameterPath
    )

    $deploymentName = "$($ARMPath.BaseName)-$(Get-Date -Format 'yyyy-MMdd')-$(Get-Random -Count 6)"

    if($deploymentName.Count -gt 64){ $deploymentName=$deploymentName[0..53] }

    try {
        if($null -eq $ParameterPath){                
            New-AzResourceGroupDeployment -Name $deploymentName `
                -TemplateFile $ARMPath `
                -TemplateParameterFile $ParameterPath `
                -ResourceGroupName $SentinelInstance.ResourceGroup `
                -Verbose
        }else{
            New-AzResourceGroupDeployment -Name $deploymentName `
                -TemplateFile $ARMPath `
                -ResourceGroupName $SentinelInstance.ResourceGroup `
                -Verbose
        }
    }
    catch {
        Write-Host -ForegroundColor Red "Failed to deploy the ARM template file: $($deploymentName.BaseName)"
    }


}