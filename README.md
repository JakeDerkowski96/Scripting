# Scripting

A personal automation toolkit of PowerShell, Python, and Bash scripts for Azure and Microsoft security engineering, plus workstation provisioning and general file utilities.

## Purpose

This repo replaces four previously scattered sources (the old `Scripting` repo, `Azure-Powershell`, `MS-Sentinel-Experimental-Workspace`, and `Pwsh`) plus a set of loose gists. Scripts are now grouped by the platform they target, so a script can be found by asking "what does it talk to?" rather than "where did I save it?"

## What's here

| Folder | Contents |
|---|---|
| `azure/` | Azure sign-in, resource helpers, ARM template deployment, Log Analytics KQL over REST |
| `entra/` | App registration / service principal inventory and permissions, directory roles, group lookups, MFA state |
| `exchange-online/` | Exchange Online and Security & Compliance PowerShell connections |
| `microsoft-graph/` | Generic Graph API caller (OAuth 2.0 client credentials) |
| `microsoft-defender/` | Advanced hunting and incident retrieval |
| `microsoft-purview/` | Sensitivity labels, eDiscovery cases, DLP rule and SIT exports |
| `microsoft-sentinel/` | Workspace and playbook deployment, detections, analytic rules, hunting queries, test-tenant tooling |
| `powershell/` | Reusable functions, module helpers, profile setup |
| `desktop/` | Windows context-menu tweaks, provisioning (Chocolatey, Commando), icon normalization; Linux environment setup |
| `utilities/` | File conversion and editing, image cropping, VS Code backup, Python snippets |
| `templates/` | Script starter files |

Each platform folder has its own `README.md` with a per-script table where one exists.

## Prerequisites

- PowerShell 7+ and the [Az module](https://learn.microsoft.com/powershell/azure/install-azure-powershell) (`Install-Module Az`)
- Python 3.10+ for the Python utilities; per-folder `requirements.txt` where present (for example `utilities/file-conversion/`)
- An Azure subscription and, for the Graph-based scripts, an app registration with a client secret

## Required permissions

Permissions are per script. Grant only what the script you are running needs; the folder READMEs are the source of truth.

| Role / permission | Scope | Reason |
|---|---|---|
| `ThreatHunting.Read.All` (Graph application) | Tenant | `microsoft-defender/Invoke-DefenderAdvancedHunting.ps1` |
| `SecurityIncident.Read.All` (Graph application) | Tenant | `microsoft-defender/Get-DefenderIncidents.ps1` |
| `InformationProtectionPolicy.Read.All` (Graph application) | Tenant | `microsoft-purview/Get-PurviewSensitivityLabels.ps1` |
| `eDiscovery.Read.All` (Graph application) | Tenant | `microsoft-purview/Get-PurviewEdiscoveryCases.ps1` |
| Depends on endpoint | Tenant | `microsoft-graph/Invoke-MsGraph.ps1` calls any Graph endpoint |
| Azure RBAC role for the target operation | Resource group or subscription | `azure/` and `microsoft-sentinel/` deploy scripts. The scripts do not yet document a specific least-privilege role, so choose the narrowest role that covers the deployment rather than defaulting to Contributor |

The `entra/`, `exchange-online/`, and remaining `microsoft-sentinel/` scripts do not state their required permissions in a README yet.

## Usage

Dot-source a script, then call its function. Credentials are passed in as parameters; never commit them.

```powershell
. ./microsoft-defender/Invoke-DefenderAdvancedHunting.ps1
Invoke-DefenderAdvancedHunting -ClientId $id -ClientSecret $secret -TenantId $tenant `
    -Query "DeviceProcessEvents | where Timestamp > ago(1h) | take 20"
```

```powershell
. ./azure/functions/AzLogin.ps1
Connect-AzureLogin
```

## Documentation

There is no `docs/` directory yet. Until there is, per-folder READMEs hold the detail:
[azure](azure/README.md), [microsoft-defender](microsoft-defender/README.md), [microsoft-graph](microsoft-graph/README.md), [microsoft-purview](microsoft-purview/README.md), [desktop](desktop/README.md), [utilities/powershell](utilities/powershell/README.md).

## Contributing

Branch from `main` as `<type>/<short-kebab-description>` and never commit to `main` directly. Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/). Open a PR and squash-merge.

## License

[GPL-3.0](LICENSE)
