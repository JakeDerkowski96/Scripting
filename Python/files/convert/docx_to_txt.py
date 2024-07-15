import argparse
import docx2txt


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help="Path to the input file")
    parser.add_argument('--output', '-o', type=str, default='output.txt', help="Name of the output file")
    return parser.parse_args()


def main():
    args = parse_args()
    print(args)

    MY_TEXT = docx2txt.process(args.input_file)

    with open(args.output, "w", encoding='utf-8') as text_file:
        print(MY_TEXT, file=text_file)


if __name__ == '__main__':
    main()

