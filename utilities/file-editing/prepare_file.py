#!/usr/bin/env python3
"""Remove duplicate and blank lines from a text file."""

import argparse


def remove_duplicates_and_blanks(lines):
    seen = set()
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            result.append(line)
    return result


def main():
    parser = argparse.ArgumentParser(description="Remove duplicate and blank lines from a text file.")
    parser.add_argument("input_file", help="Path to input file")
    parser.add_argument("output_file", help="Path to output file")
    args = parser.parse_args()

    with open(args.input_file) as f:
        lines = f.readlines()

    cleaned = remove_duplicates_and_blanks(lines)

    with open(args.output_file, "w") as f:
        f.writelines(cleaned)

    print(f"Processed {len(lines)} lines -> {len(cleaned)} lines")


if __name__ == "__main__":
    main()
