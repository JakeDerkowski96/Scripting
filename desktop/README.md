# Desktop Personalization

Scripts for provisioning and personalizing a fresh workstation on both Windows and
Linux — context-menu tweaks, package installation, and shell/terminal configuration.

```
desktop/
├── windows/
│   ├── context-menu/    # Registry tweaks for the "New" right-click submenu (add/remove per file type)
│   └── provisioning/
│       ├── commando/     # Fresh-Windows bootstrap (Chocolatey install + Windows Terminal profile)
│       └── chocolatey/   # Export/import an installed Chocolatey package set
└── linux/                # Ubuntu/Debian environment setup: packages, snaps, GNOME extensions, shell config
```

## Windows

### context-menu/
Registry (`.reg`) files that add or remove entries from the Windows 10/11 **New** submenu
for common file types (Python, PowerShell, C++, Markdown, JSON, and more). `NewItems/`
adds an entry; `RemoveItems/` reverts it. The `cmd/` and `myNewMenuItems.bat` helpers apply
a batch of them at once.

```bat
:: Add all "New" submenu entries
cmd\add.cmd
```

### provisioning/
- **commando/** — bootstraps a fresh Windows install: installs Chocolatey and applies a
  Windows Terminal profile (`full_profile.json`).
- **chocolatey/** — `Export-ChocoPackages.ps1` snapshots the currently installed Chocolatey
  packages; `Install-ChocoPackages.ps1` restores them on a new machine.

## Linux

Environment setup validated on recent Ubuntu (Debian-based). `automate.sh` orchestrates the
`scripts/` steps (apt packages, snaps, GNOME extensions) and applies shell configuration
(`bashrc`, `aliases`). Includes helpers for installing Brave and OneDrive.

```bash
bash linux/automate.sh
```
