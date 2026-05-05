#!/usr/bin/env python3
"""Split repeating structured text data into separate files.

Designed for output from PowerShell commands like:
  Get-DLPCompliancePolicy | Format-List
"""

import argparse
import os
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split repeating data blocks into separate files."
    )
    parser.add_argument("input_file", help="Path to input file with repeating blocks")
    parser.add_argument("output_dir", help="Directory to write output files")
    parser.add_argument(
        "--name-field",
        default="Name",
        help="Field name to use for output filenames (default: Name)",
    )
    parser.add_argument(
        "--separator",
        default="",
        help="Line that separates blocks (default: blank line)",
    )
    return parser.parse_args()


def split_blocks(content, separator):
    if separator:
        return content.split(separator)
    return re.split(r"\n\s*\n", content)


def extract_name(block, name_field):
    for line in block.strip().splitlines():
        if line.strip().startswith(f"{name_field}"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                return parts[1].strip().replace(" ", "_").replace("/", "_")
    return None


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.input_file, "r") as f:
        content = f.read()

    blocks = split_blocks(content, args.separator)
    count = 0

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        name = extract_name(block, args.name_field) or f"block_{count}"
        output_path = os.path.join(args.output_dir, f"{name}.txt")

        with open(output_path, "w") as f:
            f.write(block)
        count += 1

    print(f"Created {count} files in {args.output_dir}")


if __name__ == "__main__":
    main()
