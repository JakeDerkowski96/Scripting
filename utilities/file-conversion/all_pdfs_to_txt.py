#!/usr/bin/env python3
"""Batch convert all PDF files in the current directory to text files."""

import glob
import PyPDF2


def convert_all_pdfs():
    pdf_files = glob.glob("*.pdf")
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return

    for pdf_file in pdf_files:
        output_file = pdf_file[:-4] + ".txt"
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            with open(output_file, "w", encoding="utf-8") as text_file:
                for page in reader.pages:
                    text_file.write(page.extract_text())
        print(f"Converted: {pdf_file} -> {output_file}")


if __name__ == "__main__":
    convert_all_pdfs()
