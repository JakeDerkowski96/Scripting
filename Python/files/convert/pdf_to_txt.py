# import argparse
# from pdfreader import PdfReader


# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('input_file', type=str, help="Path to the input file")
#     parser.add_argument('--output', '-o', type=str, default='output.txt', help="Name of the output file")
#     return parser.parse_args()


# def pdf_to_txt(in_file, out_file):
#     pdf_file = open(in_file, 'rb')
#     pdf_reader = PyPDF2.PdfFileReader(pdf_file)

#     with open(out_file, 'w') as text_file:
#         for page_num in range(pdf_reader.numPages):
#             page = pdf_reader.getPage(page_num)
#             text_file.write(page.extractText())




# def main():
#     args = parse_args()
#     print(args)

#     pdf_to_txt(args.input_file, args.output)


# if __name__ == '__main__':
#     main()

import argparse
from pdfreader import PdfReader

parser = argparse.ArgumentParser(description='Convert a PDF file to a text file.')
parser.add_argument('input_file', metavar='INPUT_FILE', type=str,
                    help='the input PDF file')
args = parser.parse_args()

with open(args.input_file, 'rb') as pdf_file:
    pdf_reader = PdfReader(pdf_file)

    with open(args.input_file[:-4] + '.txt', 'w') as text_file:
        for page in pdf_reader.pages:
            text_file.write(page.extract_text())