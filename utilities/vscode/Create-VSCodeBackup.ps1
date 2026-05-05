# ================================
# VS Code Backup Export Script
# ================================

$BackupRoot = "$HOME\vscode-backup"
$UserDir = "$env:APPDATA\Code\User"

# Create backup directories
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
New-Item -ItemType Directory -Force -Path "$BackupRoot\User" | Out-Null

Write-Host "Exporting VS Code extensions..."
code --list-extensions > "$BackupRoot\extensions.list"

Write-Host "Copying VS Code user settings..."
Copy-Item "$UserDir\*" "$BackupRoot\User" -Recurse -Force

Write-Host "Backup completed at $BackupRoot"
