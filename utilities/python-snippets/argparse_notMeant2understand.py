import argparse
import pathlib


parser = argparse.ArgumentParser()

# type options
parser.add_argument('count', type=int)
parser.add_argument('distance', type=float)
parser.add_argument('street', type=ascii)
parser.add_argument('code_point', type=ord)
parser.add_argument('source_file', type=open)
parser.add_argument('dest_file', type=argparse.FileType('w', encoding='latin-1'))
parser.add_argument('datapath', type=pathlib.Path)

# STORE ARGS INTO LIST
# all str args stored in list, no arg required
parser.add_argument('-arglist', action='extend', nargs='+', type=str) 
# accepts x args, stored into the 'bar' list, at least 1 arg is required
parser.add_argument('bar', nargs='*') 


parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

# POSITIONAL ``````````````````````````````
# Cast the input to string, int or float type 
parser.add_argument(dest='argument1', type=str, help="A string argument")
parser.add_argument(dest='argument2', type=int, help="An integer argument")
parser.add_argument(dest='argument3', type=float, help="A float argument")

# Validate that the input is in specified list
parser.add_argument(dest='argument4', choices=['red', 'green', 'blue'])

# Accept multiple inputs for an argument, returned as a list
# Will be of type string, unless specified
parser.add_argument(dest='argument5', nargs=2, type=int)

# Optional positional argument (length 0 or 1)
parser.add_argument(dest='argument6', nargs='?')
''' END OF POSITIONAL '''


# Optional (flag) arguments
# Boolean flag (does not accept input data), with default value
parser.add_argument('-a1', action="store_true", default=False)

# Cast input to integer, with a default value
parser.add_argument('-a2', type=int, default=0)

# Provide long form name as well (maps to 'argument3' not 'a3')
parser.add_argument('-a3', '--argument3', type=str)

# Make argument mandatory
parser.add_argument('-a4', required=True)

# Retur the input via different parameter name
parser.add_argument('-a5', '--argument5', dest='my_argument')
''' END OF OPTIONAL (FLAG) '''

# Opening and closing files
# Add a required, positional argument for the input data file name,
# and open in 'read' mode
parser.add_argument('infile', type=argparse.FileType('r'))

# Add an optional argument for the output file,
# open in 'write' mode and and specify encoding
parser.add_argument('--output', type=argparse.FileType('w', encoding='UTF-8'))

args = parser.parse_args()

# Read a CSV file,  sum the values in the second column,
# and optionally write to file
sum = 0
with args.infile as infile:
    for line in infile:
        value = int(line.split(',')[1])
        sum += value
        print(sum)
    
        if args.output is not None:
            args.output.writelines(f'{sum}\n')


''' END OF OPENING AND CLOSING FILES '''



parser.parse_args()