#!/usr/bin/env python3
"""Convert a single PDF file to a text file."""

import argparse
from pdfreader import PdfReader


def parse_args():
    parser = argparse.ArgumentParser(description="Convert a PDF file to a text file.")
    parser.add_argument("input_file", help="Path to the input PDF file")
    parser.add_argument("--output", "-o", help="Output file path (default: input name with .txt extension)")
    return parser.parse_args()


def main():
    args = parse_args()
    output_file = args.output or args.input_file.rsplit(".", 1)[0] + ".txt"

    with open(args.input_file, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        with open(output_file, "w", encoding="utf-8") as text_file:
            for page in reader.pages:
                text_file.write(page.extract_text())

    print(f"Converted: {args.input_file} -> {output_file}")


if __name__ == "__main__":
    main()
