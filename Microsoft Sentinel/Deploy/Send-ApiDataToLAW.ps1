function Invoke-GeneralApi {
    param (
        [Parameter(Mandatory = $true)]
        [string]$ApiUrl,
        
        [Parameter(Mandatory = $true)]
        [string]$HttpMethod,

        [Parameter(Mandatory = $false)]
        [hashtable]$Headers = @{},
        
        [Parameter(Mandatory = $false)]
        [string]$Body
    )

    try {
        $response = Invoke-RestMethod -Uri $ApiUrl -Method $HttpMethod -Headers $Headers -Body $Body -ContentType "application/json"
        return $response
    }
    catch {
        Write-Error "API call failed: $_"
    }
}

function Send-ToLogAnalytics {
    param (
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceId,
        
        [Parameter(Mandatory = $true)]
        [string]$SharedKey,
        
        [Parameter(Mandatory = $true)]
        [string]$LogType,
        
        [Parameter(Mandatory = $true)]
        [PSObject]$JsonPayload
    )

    $json = $JsonPayload | ConvertTo-Json -Depth 6
    $apiVersion = "2016-04-01"
    $contentType = "application/json"
    $resource = "/api/logs"
    $timeStamp = Get-Date -Format "r"
    $stringToSign = "POST`n$json.Length`n$contentType`n${timeStamp}`n$resource"
    
    $hmacsha256 = New-Object System.Security.Cryptography.HMACSHA256
    $hmacsha256.Key = [Convert]::FromBase64String($SharedKey)
    $signatureBytes = $hmacsha256.ComputeHash([Text.Encoding]::UTF8.GetBytes($stringToSign))
    $signature = [Convert]::ToBase64String($signatureBytes)
    $authorization = "SharedKey $WorkspaceId:$signature"
    
    $headers = @{
        "Content-Type"         = $contentType
        "Authorization"        = $authorization
        "Log-Type"             = $LogType
        "x-ms-date"            = $timeStamp
        "time-generated-field" = $null
    }
    
    try {
        Invoke-RestMethod -Method Post -Uri "https://$($WorkspaceId).ods.opinsights.azure.com$resource?api-version=$apiVersion" -Headers $headers -Body $json
        Write-Output "Data successfully sent to Log Analytics workspace."
    }
    catch {
        Write-Error "Failed to send data to Log Analytics: $_"
    }
}

# Example Usage
$ApiUrl = "https://api.example.com/data"
$HttpMethod = "GET"
$Headers = @{
    "Authorization" = "Bearer your_access_token"
}

$response = Invoke-GeneralApi -ApiUrl $ApiUrl -HttpMethod $HttpMethod -Headers $Headers

if ($response) {
    $WorkspaceId = "your-workspace-id"
    $SharedKey = "your-shared-key"
    $LogType = "CustomLogType"

    Send-ToLogAnalytics -WorkspaceId $WorkspaceId -SharedKey $SharedKey -LogType $LogType -JsonPayload $response
}
