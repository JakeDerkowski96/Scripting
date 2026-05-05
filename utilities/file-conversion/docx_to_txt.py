#!/usr/bin/env python3
"""Convert a DOCX file to a text file."""

import argparse
import docx2txt


def parse_args():
    parser = argparse.ArgumentParser(description="Convert a DOCX file to a text file.")
    parser.add_argument("input_file", help="Path to the input DOCX file")
    parser.add_argument("--output", "-o", default="output.txt", help="Output file path")
    return parser.parse_args()


def main():
    args = parse_args()
    text = docx2txt.process(args.input_file)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Converted: {args.input_file} -> {args.output}")


if __name__ == "__main__":
    main()
