# Microsoft Graph

Generic Microsoft Graph API caller using the OAuth 2.0 client-credentials flow. Used as a
building block by the Defender and Purview scripts, or on its own for any Graph endpoint.

| Script | Purpose | App permission |
|--------|---------|----------------|
| `Invoke-MsGraph.ps1` | Acquire an app-only token and call any Graph endpoint (Get/Post/Patch/Delete) | Depends on the endpoint called |

## Example

```powershell
. ./Invoke-MsGraph.ps1
Invoke-MsGraphApi -ClientId $id -ClientSecret $secret -TenantId $tenant `
    -ApiEndpoint "https://graph.microsoft.com/v1.0/users?`$top=5"
```
