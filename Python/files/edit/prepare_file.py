import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Remove duplicate and blank lines from a text file")
    parser.add_argument("input_file_path", type=str, help="Path to input file")
    parser.add_argument("output_file_name", type=str, help="Name of output file")
    return parser.parse_args()


def remove_duplicates_blank_lines(lines):
    lines = list(set(lines))
    lines = [line for line in lines if line.strip() != ""]
    return lines


def process_file(input_file_path, output_file_name):
    with open(input_file_path) as f:
        lines = f.readlines()
    lines = remove_duplicates_blank_lines(lines)
    with open(output_file_name, "w") as f:
        f.write("".join(lines))


def main():
    args = parse_args()
    process_file(args.input_file_path, args.output_file_name)


if __name__ == "__main__":
    main()

