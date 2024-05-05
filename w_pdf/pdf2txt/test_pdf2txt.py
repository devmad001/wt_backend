#from pypdf import PdfReader
import PyPDF2
from PyPDF2 import PdfReader   #BOA tables

#0v1# JC Feb 28, 2024  Issue on support for Minion Pro/roboto

print ("PyPDF2 version: "+str(PyPDF2.__version__))

pdf_roboto = r"test_pdf_roboto.pdf"
pdf_arial = r"test_pdf_arial.pdf"

reader = PdfReader(pdf_arial)
page = reader.pages[0]
pages_text = page.extract_text()
#print(pages_text)
