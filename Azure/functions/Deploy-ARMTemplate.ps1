[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]
    $ARMPath,

    [Parameter(Mandatory)]
    [string]
    $ResourceGroup,

    [Parameter()]
    [string]
    $ParameterPath
)

function Deploy-ARMTemplate($ARMPath, $ParameterPath, $ResourceGroup){

    $basename = (Get-Item -Path $ARMPath).BaseName

    $deploymentName =  $basename + '-' + (Get-Random)

    Write-Host -ForegroundColor Yellow "Initiating deployment of the $($basename) template"

    try {
        New-AzResourceGroupDeployment -Name $deploymentName `
            -ResourceGroupName $ResourceGroup `
            -templateFile $ARMPath `
            -TemplateParameterFile $ParameterPath `
            -Verbose

        Write-Host -ForegroundColor Green "Successful deployment: $($deploymentName)"
    }
    catch {
        Write-Host -ForegroundColor Red "ARM Template deployment failed"
        Exit
    }
}