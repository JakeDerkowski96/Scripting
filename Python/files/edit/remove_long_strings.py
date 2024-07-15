import argparse

def remove_long_string(line, char, max_length):
    index = line.find(char)
    if index == -1:
        return line
    elif index > max_length:
        return ''
    else:
        return line[:index+1]

def parse_args():
    parser = argparse.ArgumentParser(description='Remove strings longer than a given length.')
    parser.add_argument('input_file', type=str, help='the input file')
    parser.add_argument('output_file', type=str, help='the output file')
    # parser.add_argument('char', type=str, help='the character to search for')
    parser.add_argument('max_length', type=int, help='the maximum length of the string')
    return parser.parse_args()

def main():
    args = parse_args()
    char = ','
    with open(args.input_file, 'r') as f_in:
        with open(args.output_file, 'w') as f_out:
            for line in f_in:
                new_line = remove_long_string(line, char, args.max_length)
                f_out.write(new_line)

if __name__ == '__main__':
    main()