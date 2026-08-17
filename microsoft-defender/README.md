# Microsoft Defender

Automation scripts for Microsoft Defender XDR, built on the Microsoft Graph security API
(OAuth 2.0 client-credentials flow).

| Script | Purpose | App permission |
|--------|---------|----------------|
| `Invoke-DefenderAdvancedHunting.ps1` | Run an advanced hunting (KQL) query and return the result rows | `ThreatHunting.Read.All` |
| `Get-DefenderIncidents.ps1` | List Defender XDR incidents with optional OData filtering and automatic paging | `SecurityIncident.Read.All` |

## Example

```powershell
. ./Invoke-DefenderAdvancedHunting.ps1
Invoke-DefenderAdvancedHunting -ClientId $id -ClientSecret $secret -TenantId $tenant `
    -Query "DeviceProcessEvents | where Timestamp > ago(1h) | take 20"
```
