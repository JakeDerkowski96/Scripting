# normalize-folder-icons

Converts a folder of collected icon files (`.ico`, `.svg`, `.png`, `.jpg`) into clean, multi-resolution Windows `.ico` files ready for Explorer's *Properties > Customize > Change Icon*.

## Purpose

Icons collected from different sources rarely share the same resolution set — some `.ico` files only embed one small frame, `.png`/`.jpg` files are often not square, and `.svg` files aren't usable by Explorer at all. This script normalizes a whole folder at once instead of fixing icons by hand one at a time.

## What's here

```text
desktop/normalize-folder-icons/
├── normalize_folder_icons.py   # the script
└── README.md                   # this file
```

## Prerequisites

- Python 3.10+
- [Pillow](https://pypi.org/project/Pillow/): `pip install Pillow`
- **Optional, for `.svg` support** — one of:
  - `cairosvg` (`pip install cairosvg`; on Windows also requires the Cairo native library, easiest via the [GTK3 runtime installer](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer))
  - [Inkscape](https://inkscape.org) on `PATH`
  - [ImageMagick](https://imagemagick.org) (`magick`) on `PATH`

  Without one of these, `.svg` files are skipped with a warning — everything else still processes normally.

## Required permissions

| Role | Scope | Reason |
|---|---|---|
| None | Local filesystem only | Reads from `--source` and writes to `--output`; makes no network or cloud calls |

## Usage

```bash
python normalize_folder_icons.py --source "C:\Icons\Collected" --output "C:\Icons\Normalized"
```

Preview what would happen first, without writing anything:

```bash
python normalize_folder_icons.py --source ./raw --output ./clean --dry-run --verbose
```

Regenerate `.ico` files that already exist in the output folder:

```bash
python normalize_folder_icons.py --source ./raw --output ./clean --overwrite
```

Use a custom set of embedded sizes (default is `16,24,32,48,64,128,256`):

```bash
python normalize_folder_icons.py --source ./raw --output ./clean --sizes 16,32,48,256
```

| Flag | Effect |
|---|---|
| `--source` | Directory to scan recursively for icon source files (required) |
| `--output` | Directory to write normalized `.ico` files into (required) |
| `--sizes` | Comma-separated pixel sizes to embed |
| `--overwrite` | Regenerate output files that already exist (default: skip them) |
| `--dry-run` | Report what would happen without writing any files |
| `--verbose` | Enable debug-level logging |

## Documentation

No additional docs beyond this README — the script is a single self-contained utility. Behavior notes and known limitations are in the module docstring and function docstrings in `normalize_folder_icons.py`.

**Known limitations:**
- Non-square source images are padded to square on a transparent background rather than cropped, so the original content is never lost, but this can leave visible padding on very rectangular sources.
- For existing `.ico` files, the largest embedded frame is used as the source for re-encoding; frames larger than what's requested via `--sizes` are simply not included in the output.

## Contributing

Personal utility script — no external contribution workflow. Standard practice: verbose and dry-run flags stay supported for any future changes that write to disk.

## License

MIT — free to use, modify, and distribute.
