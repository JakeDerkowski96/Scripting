#!/usr/bin/env python3
"""Remove lines exceeding a maximum character length from a file."""

import argparse


def remove_long_lines(input_file, output_file, max_length):
    with open(input_file, "r") as f:
        lines = f.readlines()

    with open(output_file, "w") as f:
        for line in lines:
            if len(line.rstrip("\n")) <= max_length:
                f.write(line)


def main():
    parser = argparse.ArgumentParser(description="Remove lines longer than a given length.")
    parser.add_argument("input_file", help="Path to input file")
    parser.add_argument("output_file", help="Path to output file")
    parser.add_argument("max_length", type=int, help="Maximum line length to keep")
    args = parser.parse_args()

    remove_long_lines(args.input_file, args.output_file, args.max_length)


if __name__ == "__main__":
    main()
