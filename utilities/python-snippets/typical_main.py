import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser('')
    parser.add_argument('arg1',
                        metavar='',
                        help='the name (or path) to the CSV file you wish to view'
    )
    parser.add_argument('--option1', '-opt',
                        default='', nargs='', action='', type=, 
                        dest='',
                        help=''
    )

    parser.add_argument('-p', '--path', type=str,
                        default='', 
                        help=''
    )
    parser.add_argument("-o", "--output", action='store', type=str,
                        dest='output', 
                        help="Output name"
    )
    parser.add_argument('-v', '--verbose', action='count', default=0)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()



def main():
    args = parse_args()
    print(args)
    


if __name__ == '__main__':
    main()