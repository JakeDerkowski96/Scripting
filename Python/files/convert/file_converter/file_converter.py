"""this is intended to be the master converter script. inot sure if this will be main or package yet"""


import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Converts input file to output file type')
    parser.add_argument('input_file', type=str, help='Input file path')
    parser.add_argument('output_file', type=str, help='Output file path')
    parser.add_argument('filetype', type=str, help='Filetype/file extension')
    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.isfile(args.input_file):
        print(f"{args.input_file} does not exist")
        return

    if not args.input_file.endswith(args.filetype):
        print(f"{args.input_file} is not a {args.filetype} file")
        return

    if not args.output_file.endswith(args.filetype):
        args.output_file += f".{args.filetype}"

    with open(args.input_file, 'rb') as f:
        data = f.read()

    with open(args.output_file, 'wb') as f:
        f.write(data)

if __name__ == '__main__':
    main()


# This code has a separate function called `parse_args()` that returns the parsed arguments. The `main()` function calls this function to get the arguments and then proceeds with the rest of the code.
