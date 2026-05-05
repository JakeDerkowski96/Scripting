function Invoke-GeneralApi {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ApiUrl,

        [Parameter(Mandatory)]
        [ValidateSet("Get", "Post", "Put", "Patch", "Delete")]
        [string]$HttpMethod,

        [Parameter()]
        [hashtable]$Headers = @{},

        [Parameter()]
        [string]$Body
    )

    try {
        $params = @{
            Uri         = $ApiUrl
            Method      = $HttpMethod
            Headers     = $Headers
            ContentType = "application/json"
        }
        if ($Body) { $params['Body'] = $Body }

        Invoke-RestMethod @params
    }
    catch {
        Write-Error "API call failed: $($_.Exception.Message)"
    }
}

function Send-ToLogAnalytics {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$WorkspaceId,

        [Parameter(Mandatory)]
        [string]$SharedKey,

        [Parameter(Mandatory)]
        [string]$LogType,

        [Parameter(Mandatory)]
        [PSObject]$JsonPayload
    )

    $json = $JsonPayload | ConvertTo-Json -Depth 6
    $contentType = "application/json"
    $resource = "/api/logs"
    $timeStamp = Get-Date -Format "r"
    $contentLength = [System.Text.Encoding]::UTF8.GetByteCount($json)

    $stringToSign = "POST`n$contentLength`n$contentType`nx-ms-date:$timeStamp`n$resource"

    $hmacsha256 = New-Object System.Security.Cryptography.HMACSHA256
    $hmacsha256.Key = [Convert]::FromBase64String($SharedKey)
    $signatureBytes = $hmacsha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($stringToSign))
    $signature = [Convert]::ToBase64String($signatureBytes)
    $authorization = "SharedKey ${WorkspaceId}:$signature"

    $headers = @{
        "Content-Type"         = $contentType
        "Authorization"        = $authorization
        "Log-Type"             = $LogType
        "x-ms-date"            = $timeStamp
        "time-generated-field" = ""
    }

    $uri = "https://$WorkspaceId.ods.opinsights.azure.com$resource?api-version=2016-04-01"

    try {
        Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $json
        Write-Output "Data successfully sent to Log Analytics workspace."
    }
    catch {
        Write-Error "Failed to send data to Log Analytics: $($_.Exception.Message)"
    }
}
