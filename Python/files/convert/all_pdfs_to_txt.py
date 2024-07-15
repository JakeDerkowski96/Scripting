import glob
import PyPDF2

pdf_files = glob.glob('*.pdf')

for pdf_file in pdf_files:
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        with open(pdf_file[:-4] + '.txt', 'w') as text_file:
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                text_file.write(page.extractText())