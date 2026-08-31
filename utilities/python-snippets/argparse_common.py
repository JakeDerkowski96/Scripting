import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help="Path to the input file")
    parser.add_argument('--output', '-o', type=str, dest='out_file', default='output.txt', help="Name of the output file")
    return parser.parse_args()


def main():
    args = parse_args()
    print(args)


if __name__ == '__main__':
    main()
