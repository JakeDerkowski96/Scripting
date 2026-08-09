function Get-AzConnection {
    if ($null -ne $(Get-AzContext)) {
        $azContext = Get-AzContext        
        Write-Host -ForegroundColor Green "A connection has already been established with $($azContext.Account.Type) to $($azContext.Account.Id)"        
    }else {
        try {
            $Conn = Connect-AzAccount
            if($null -ne $Conn){
                Write-Host -ForegroundColor Green "Sucessful authentication to Azure "
            }
        }catch {
            Write-Host -ForegroundColor Red "Failed to authenticate to Azure  with $($conn.Account.Type) to $($conn.Account.Id)"
            Exit
        }
    }
}

function Install-Module-If-Needed {
    param([string]$ModuleName)

    if (Get-Module -ListAvailable -Name $ModuleName) {
        Write-Host "Module '$($ModuleName)' already exists, continue..." -ForegroundColor Green
    }
    else {
        Write-Host "Module '$($ModuleName)' does not exist, installing..." -ForegroundColor Yellow
        Install-Module $ModuleName -Force -AllowClobber -ErrorAction Stop
        Write-Host "Module '$($ModuleName)' installed." -ForegroundColor Green
    }
}

$VerbosePreference = 'Continue'

Install-Module-If-Needed -ModuleName "Az.Accounts"

# Connect if not connected
Get-AzConnection


#! Get Az Access Token
$token = Get-AzAccessToken 
$authHeader = @{
    'Content-Type'  = 'application/json'
    'Authorization' = 'Bearer ' + $token.Token
}

# set workospace details
$workspaceName = "law-siem01"
$subscriptionId = "8e970e2a-c002-4c7b-aee4-fe0538e8e16c"
$resourceGroupName = "rg-logs"

$WorkspaceParameters = @{
    subscriptionId    = $subscriptionId
    workspaceName     = $workspaceName
    resourceGroupName = $resourceGroupName
}

# Get Content Product Packages
$contentURI = "https://management.azure.com/subscriptions/$subscriptionid/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/contentProductPackages?api-version=2023-09-01-preview"

$contentResponse = (Invoke-RestMethod $contentURI -Method 'GET' -Headers $authHeader).value

$OutPath = ".\Output"

if (!(Test-Path -PAth $OutPath)) {
    New-Item -ItemType Directory -Path $OutPath
}

# saved as a json file
$contentResponse | ConvertTo-Json -Depth 100 | Out-File -FilePath "$OutPath\Content-Solution-Packages.json"

$solutions = $contentResponse | Where-Object { $null -ne $_.properties.installedVersion }

# must define the target solution
$solutionName = "Security Threat Essentials"

$solution = ($solutions | Where-Object { $_.properties.displayName -eq "$solutionName" }).properties.contentId


# Get Content Templates
$contentURI = "https://management.azure.com/subscriptions/$subscriptionid/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/contentTemplates?api-version=2023-09-01-preview"
$contentResponse = (Invoke-RestMethod $contentURI -Method 'GET' -Headers $authHeader).value

try {
    $contentTemplates = $contentResponse | Where-Object { $_.properties.packageId -eq $solution -and $_.properties.contentKind -eq "AnalyticsRule" }
    if ($contentTemplates.Count -eq 0) {
        throw "Solution Name: [$solutionName] cannot be found. Please check the solution name and Install it from the Content Hub blade"
    }
}
catch {
    Write-Error $_ -ErrorAction Stop
}