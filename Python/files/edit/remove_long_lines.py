import argparse

def remove_long_lines(input_file, output_file, max_length):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    with open(output_file, 'w') as file:
        for line in lines:
            if len(line) <= max_length:
                file.write(line)

def parse_args():
    parser = argparse.ArgumentParser(description='Remove lines longer than a variable length from a file.')
    parser.add_argument('input_file', help='path to input file')
    parser.add_argument('output_file', help='path to output file')
    parser.add_argument('max_length', type=int, help='maximum length of a line to keep')
    return parser.parse_args()

def main():
    args = parse_args()
    remove_long_lines(args.input_file, args.output_file, args.max_length)

if __name__ == '__main__':
    main()