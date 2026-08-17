# Scripting

Automation toolkit for Azure cloud engineering, Microsoft security platforms, workstation provisioning, and general-purpose file utilities. Built in PowerShell, Python, and Bash.

## Repository Structure

```
├── azure/
│   ├── functions/       # Azure auth, ARM deployment, resource management, Entra ID
│   └── kql/             # Log Analytics KQL query execution via REST API
│
├── microsoft-graph/     # Generic Microsoft Graph API caller (OAuth 2.0 client credentials)
│
├── microsoft-sentinel/
│   ├── deploy/          # Workspace creation, data ingestion to Log Analytics
│   ├── detections/      # Detection rule selection and deployment tooling
│   └── analytics-rules/ # Analytic rule ARM template modification
│
├── microsoft-defender/  # Advanced hunting + incident retrieval (Graph security API)
├── microsoft-purview/   # Sensitivity labels + eDiscovery cases (Graph security API)
│
├── desktop/
│   ├── windows/         # Context-menu registry tweaks + fresh-install provisioning (Chocolatey)
│   └── linux/           # Ubuntu/Debian environment setup: packages, snaps, GNOME, shell config
│
├── utilities/
│   ├── file-conversion/ # PDF/DOCX to TXT converters
│   ├── file-editing/    # Text processing (dedup, filter, split)
│   ├── images/          # Bulk image cropping
│   ├── vscode/          # VS Code settings/extensions backup
│   ├── linux/           # User and group enumeration
│   └── powershell/      # General-purpose PowerShell helpers, module, and profile tooling
│
└── templates/           # Script boilerplate/starter files
```

## Prerequisites

### PowerShell

- PowerShell 7+
- [Az PowerShell module](https://learn.microsoft.com/en-us/powershell/azure/install-azure-powershell) (`Install-Module Az`)

### Python

- Python 3.8+
- Per-project dependencies in `requirements.txt` where applicable:
  - `PyPDF2` — PDF text extraction
  - `pdfreader` — Alternative PDF reader
  - `docx2txt` — DOCX text extraction

### Azure

- Azure subscription with appropriate RBAC roles
- App registration with client secret (for Graph API / KQL scripts)

## Usage

```powershell
# Authenticate to Azure
. ./azure/functions/AzLogin.ps1
Connect-AzureLogin

# Deploy an ARM template
. ./azure/functions/Deploy-ARMTemplate.ps1
Deploy-ARMTemplate -TemplatePath ./template.json -ResourceGroup "my-rg"

# Query Log Analytics
. ./azure/kql/Invoke-LAWQuery.ps1
Invoke-LAWQuery -ClientId $id -ClientSecret $secret -TenantId $tenant `
    -SubscriptionId $sub -ResourceGroup "my-rg" -Workspace "my-law" `
    -Query "SecurityEvent | take 10"

# Run a Defender XDR advanced hunting query
. ./microsoft-defender/Invoke-DefenderAdvancedHunting.ps1
Invoke-DefenderAdvancedHunting -ClientId $id -ClientSecret $secret -TenantId $tenant `
    -Query "DeviceProcessEvents | where Timestamp > ago(1h) | take 20"
```

```bash
# Convert all PDFs in current directory to text
python utilities/file-conversion/all_pdfs_to_txt.py

# Send API data to Log Analytics
python microsoft-sentinel/deploy/send_api_data_to_law.py rest \
    --api-url https://api.example.com/data \
    --workspace-id $WORKSPACE_ID \
    --shared-key $SHARED_KEY
```

## License

[GPL-3.0](LICENSE)
