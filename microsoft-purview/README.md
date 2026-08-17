# Microsoft Purview

Automation scripts for Microsoft Purview compliance and data governance, built on the
Microsoft Graph security API (OAuth 2.0 client-credentials flow).

| Script | Purpose | App permission |
|--------|---------|----------------|
| `Get-PurviewSensitivityLabels.ps1` | List published sensitivity labels (Graph beta) | `InformationProtectionPolicy.Read.All` |
| `Get-PurviewEdiscoveryCases.ps1` | List eDiscovery (Premium) cases with optional filtering and automatic paging | `eDiscovery.Read.All` |

## Example

```powershell
. ./Get-PurviewSensitivityLabels.ps1
Get-PurviewSensitivityLabels -ClientId $id -ClientSecret $secret -TenantId $tenant |
    Sort-Object priority | Format-Table name, priority, isActive
```
