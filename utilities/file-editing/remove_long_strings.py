#!/usr/bin/env python3
"""Remove strings longer than a given length, truncating at a delimiter character."""

import argparse


def remove_long_string(line, delimiter, max_length):
    index = line.find(delimiter)
    if index == -1:
        return line
    elif index > max_length:
        return ""
    else:
        return line[: index + 1]


def main():
    parser = argparse.ArgumentParser(description="Remove strings longer than a given length.")
    parser.add_argument("input_file", help="Path to input file")
    parser.add_argument("output_file", help="Path to output file")
    parser.add_argument("max_length", type=int, help="Maximum string length before delimiter")
    parser.add_argument("--delimiter", "-d", default=",", help="Delimiter character (default: comma)")
    args = parser.parse_args()

    with open(args.input_file, "r") as f_in:
        with open(args.output_file, "w") as f_out:
            for line in f_in:
                f_out.write(remove_long_string(line, args.delimiter, args.max_length))


if __name__ == "__main__":
    main()
