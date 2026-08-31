[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
    [string]
    $ARMPath,

    [Parameter(Mandatory)]
    [string]
    $ResourceGroup,

    [Parameter()]
    [string]
    $TemplatePath
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

try{
    Connect-AzAccount

    Deploy-ARMTemplate $ARMPath $ParameterPath $ResourceGroup
}catch{
    Write-Host $_.Exception.Message
}