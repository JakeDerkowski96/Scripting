#!/usr/bin/env python3
"""normalize_folder_icons.py

Scan a directory of collected icon files (.ico, .svg, .png, .jpg/.jpeg) and
produce a clean set of multi-resolution Windows .ico files, suitable for
Explorer > Properties > Customize > Change Icon.

Why this exists: icons collected from different sources rarely share the same
resolution set. Some .ico files only contain one small frame, some .png/.jpg
files aren't square, and .svg files aren't usable by Explorer at all. This
script normalizes all of that into consistent, well-formed .ico files.

SVG support requires one of the following to be available:
  - the Python package `cairosvg` (pip install cairosvg) - on Windows this
    also needs the Cairo native library, easiest via:
    https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
  - Inkscape on PATH (https://inkscape.org) - no extra Python deps
  - ImageMagick's `magick` on PATH (https://imagemagick.org)
If none are available, .svg files are skipped with a warning and everything
else still processes normally.

Requirements:
    pip install Pillow

Usage:
    python normalize_folder_icons.py --source "C:\\Icons\\Collected" --output "C:\\Icons\\Normalized"
    python normalize_folder_icons.py --source ./raw --output ./clean --dry-run --verbose
"""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - dependency guidance path
    print("Pillow is required. Install it with: pip install Pillow", file=sys.stderr)
    raise

LOGGER = logging.getLogger("normalize_folder_icons")

DEFAULT_SIZES: tuple[int, ...] = (16, 24, 32, 48, 64, 128, 256)
SUPPORTED_SUFFIXES: tuple[str, ...] = (".ico", ".svg", ".png", ".jpg", ".jpeg")
SVG_RASTER_SIZE = 256


class IconConversionError(Exception):
    """Raised when a single icon file cannot be converted."""


def setup_logging(verbose: bool) -> None:
    """Configure logging output.

    Args:
        verbose: If True, emit DEBUG-level messages; otherwise INFO-level.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)-8s %(message)s",
    )
    # Pillow's own loggers are extremely chatty at DEBUG; keep our output readable.
    logging.getLogger("PIL").setLevel(logging.INFO)


def find_svg_rasterizer() -> str | None:
    """Detect which SVG-to-PNG method is available on this machine.

    Returns:
        One of "cairosvg", "inkscape", "magick", or None if nothing usable
        was found.
    """
    try:
        import cairosvg  # noqa: F401

        return "cairosvg"
    except ImportError:
        pass

    if shutil.which("inkscape"):
        return "inkscape"
    if shutil.which("magick"):
        return "magick"
    return None


def rasterize_svg(svg_path: Path, method: str, size: int = SVG_RASTER_SIZE) -> Image.Image:
    """Render an SVG file to a square RGBA raster image.

    Args:
        svg_path: Path to the source .svg file.
        method: Rasterization backend, as returned by find_svg_rasterizer().
        size: Target width/height in pixels of the rasterized output.

    Returns:
        A Pillow Image in RGBA mode.

    Raises:
        IconConversionError: If rasterization fails for any reason.
    """
    try:
        if method == "cairosvg":
            import cairosvg

            png_bytes = cairosvg.svg2png(
                url=str(svg_path), output_width=size, output_height=size
            )
            with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
                tmp.write(png_bytes)
                tmp.flush()
                return Image.open(tmp.name).convert("RGBA")

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_png = Path(tmp_dir) / "raster.png"
            if method == "inkscape":
                cmd = [
                    "inkscape",
                    str(svg_path),
                    f"--export-filename={out_png}",
                    f"--export-width={size}",
                    f"--export-height={size}",
                ]
            elif method == "magick":
                cmd = [
                    "magick",
                    "-background",
                    "none",
                    "-density",
                    "384",
                    str(svg_path),
                    "-resize",
                    f"{size}x{size}",
                    str(out_png),
                ]
            else:
                raise IconConversionError(f"Unknown rasterization method: {method}")

            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            return Image.open(out_png).convert("RGBA")

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        raise IconConversionError(f"Failed to rasterize {svg_path.name}: {exc}") from exc


def make_square(image: Image.Image) -> Image.Image:
    """Pad a non-square image to square on a transparent canvas, centered.

    Args:
        image: Source image in RGBA mode.

    Returns:
        A square RGBA image. Already-square input is returned unchanged.
    """
    width, height = image.size
    if width == height:
        return image

    side = max(width, height)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    offset = ((side - width) // 2, (side - height) // 2)
    canvas.paste(image, offset)
    return canvas


def load_base_image(path: Path, svg_method: str | None) -> Image.Image:
    """Load the highest-quality source image available for a given file.

    Args:
        path: Path to a .ico, .svg, .png, .jpg, or .jpeg file.
        svg_method: Rasterization backend to use for .svg files, or None.

    Returns:
        A square RGBA Pillow Image ready to be re-encoded as .ico.

    Raises:
        IconConversionError: If the file cannot be read or converted.
    """
    suffix = path.suffix.lower()

    if suffix == ".svg":
        if svg_method is None:
            raise IconConversionError(
                "no SVG rasterizer available (install cairosvg, Inkscape, or ImageMagick)"
            )
        image = rasterize_svg(path, svg_method)

    elif suffix == ".ico":
        try:
            with Image.open(path) as ico:
                # Pick the largest embedded frame for the cleanest re-encode.
                sizes = getattr(ico, "info", {}).get("sizes") or [ico.size]
                best_size = max(sizes, key=lambda s: s[0] * s[1])
                ico.size = best_size
                ico.load()
                image = ico.convert("RGBA")
        except OSError as exc:
            raise IconConversionError(f"could not read {path.name}: {exc}") from exc

    else:  # .png, .jpg, .jpeg
        try:
            with Image.open(path) as img:
                image = img.convert("RGBA")
        except OSError as exc:
            raise IconConversionError(f"could not read {path.name}: {exc}") from exc

    return make_square(image)


def build_ico(image: Image.Image, output_path: Path, sizes: tuple[int, ...], dry_run: bool) -> None:
    """Write a multi-resolution .ico file from a single source image.

    Args:
        image: Square RGBA source image.
        output_path: Destination .ico path.
        sizes: Pixel dimensions to embed, e.g. (16, 32, 48, 64, 128, 256).
        dry_run: If True, log the intended action without writing anything.

    Raises:
        IconConversionError: If the .ico file cannot be written.
    """
    usable_sizes = tuple((s, s) for s in sorted(sizes) if s <= image.size[0]) or ((image.size[0], image.size[0]),)

    if dry_run:
        LOGGER.info("[dry-run] would write %s with sizes %s", output_path.name, usable_sizes)
        return

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="ICO", sizes=list(usable_sizes))
    except OSError as exc:
        raise IconConversionError(f"could not write {output_path.name}: {exc}") from exc


def process_file(
    path: Path,
    output_dir: Path,
    sizes: tuple[int, ...],
    svg_method: str | None,
    overwrite: bool,
    dry_run: bool,
) -> bool:
    """Convert a single icon source file into a normalized .ico.

    Args:
        path: Source file (.ico, .svg, .png, .jpg, .jpeg).
        output_dir: Directory to write the resulting .ico into.
        sizes: Pixel dimensions to embed in the output .ico.
        svg_method: Rasterization backend for .svg files, or None.
        overwrite: If False, skip files whose output already exists.
        dry_run: If True, do not write any files.

    Returns:
        True if the file was processed (or would be, in dry-run), False if
        it was skipped.
    """
    output_path = output_dir / f"{path.stem}.ico"

    if output_path.exists() and not overwrite:
        LOGGER.debug("skipping %s (output already exists, use --overwrite)", path.name)
        return False

    try:
        image = load_base_image(path, svg_method)
        build_ico(image, output_path, sizes, dry_run)
        LOGGER.info("%s -> %s", path.name, output_path.name)
        return True
    except IconConversionError as exc:
        LOGGER.warning("skipped %s: %s", path.name, exc)
        return False


def discover_source_files(source_dir: Path) -> list[Path]:
    """Find all supported icon source files under a directory.

    Args:
        source_dir: Directory to scan (recursively).

    Returns:
        Sorted list of matching file paths.
    """
    return sorted(
        p for p in source_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list to parse; defaults to sys.argv when None.

    Returns:
        Parsed argument namespace.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--source", required=True, type=Path, help="Directory of collected icon files")
    parser.add_argument("--output", required=True, type=Path, help="Directory to write normalized .ico files")
    parser.add_argument(
        "--sizes",
        default=",".join(str(s) for s in DEFAULT_SIZES),
        help=f"Comma-separated icon sizes in pixels (default: {','.join(str(s) for s in DEFAULT_SIZES)})",
    )
    parser.add_argument("--overwrite", action="store_true", help="Regenerate .ico files that already exist")
    parser.add_argument("--dry-run", action="store_true", help="Report what would happen without writing files")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Argument list; defaults to sys.argv when None.

    Returns:
        Process exit code (0 on success, 1 if the source directory is invalid).
    """
    args = parse_args(argv)
    setup_logging(args.verbose)

    if not args.source.is_dir():
        LOGGER.error("source directory does not exist: %s", args.source)
        return 1

    sizes = tuple(int(s.strip()) for s in args.sizes.split(",") if s.strip())
    svg_method = find_svg_rasterizer()
    if svg_method:
        LOGGER.debug("SVG rasterizer: %s", svg_method)
    else:
        LOGGER.warning("no SVG rasterizer found - .svg files will be skipped")

    files = discover_source_files(args.source)
    LOGGER.info("found %d candidate icon file(s) in %s", len(files), args.source)

    processed = skipped = 0
    for path in files:
        if process_file(path, args.output, sizes, svg_method, args.overwrite, args.dry_run):
            processed += 1
        else:
            skipped += 1

    LOGGER.info("done: %d processed, %d skipped", processed, skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
