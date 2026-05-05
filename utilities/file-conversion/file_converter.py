#!/usr/bin/env python3
"""Generic file conversion utility with type validation."""

import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Copy and convert a file with type validation.")
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument("output_file", help="Output file path")
    parser.add_argument("filetype", help="Expected file extension (e.g., pdf, docx)")
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Error: {args.input_file} does not exist")
        return

    if not args.input_file.endswith(f".{args.filetype}"):
        print(f"Error: {args.input_file} is not a .{args.filetype} file")
        return

    output_file = args.output_file
    if not output_file.endswith(f".{args.filetype}"):
        output_file += f".{args.filetype}"

    with open(args.input_file, "rb") as f:
        data = f.read()

    with open(output_file, "wb") as f:
        f.write(data)

    print(f"Converted: {args.input_file} -> {output_file}")


if __name__ == "__main__":
    main()
