from pdf2docx import Converter

def convert_pdf_to_word(pdf_file_path, word_file_path):
    # Create a PDF converter object
    cv = Converter(pdf_file_path)
    
    # Convert all pages of the PDF to a Word document
    cv.convert(word_file_path, start=0, end=None)
    
    # Close the converter to release resources
    cv.close()

# Specify the path to your PDF file and the output Word file
pdf_path = 'C:/Users/AnderSein/Downloads/TNLK021KEP-Comunicacion-KepServerEx-con-Siemens-S7-1200.pdf'
docx_path = 'C:/Users/AnderSein/Downloads/pdf_to_word.docx'

# Call the function with the paths
convert_pdf_to_word(pdf_path, docx_path)
