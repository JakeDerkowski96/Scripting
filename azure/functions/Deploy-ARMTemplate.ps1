#Requires -Module Az.Resources

function Deploy-ARMTemplate {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$TemplatePath,

        [Parameter(Mandatory)]
        [string]$ResourceGroup,

        [Parameter()]
        [string]$ParameterPath
    )

    $basename = (Get-Item -Path $TemplatePath).BaseName
    $deploymentName = "$basename-$(Get-Random)"

    Write-Verbose "Initiating deployment: $deploymentName"

    $params = @{
        Name              = $deploymentName
        ResourceGroupName = $ResourceGroup
        TemplateFile      = $TemplatePath
        Verbose           = $true
    }

    if ($ParameterPath) {
        $params['TemplateParameterFile'] = $ParameterPath
    }

    try {
        New-AzResourceGroupDeployment @params
        Write-Host "Successful deployment: $deploymentName" -ForegroundColor Green
    }
    catch {
        Write-Error "ARM template deployment failed: $($_.Exception.Message)"
    }
}
