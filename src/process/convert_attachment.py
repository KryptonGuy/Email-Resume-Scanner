# from pdfminer.high_level import extract_text
import docx2txt
import subprocess  
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import os
from io import StringIO
from logger import getLogger


logger = getLogger(__name__)

def extract_text_from_pdf(file):
    logger.info("Extracting text from pdf")

    output_string = StringIO()

    # Create interpreter
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Parse PDF
    file.seek(0) # To keep pointer at 0
    parser = PDFParser(file)
    doc = PDFDocument(parser)
    
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

    return output_string.getvalue()

def extract_text_from_docx(file):
    
    logger.info("Extracting text from docx")

    txt = docx2txt.process(file.name)
    if txt:
        return txt.replace('\t', ' ')
    return None


def extract_text_from_doc(file):

    logger.info("Extracting text from doc")

    try:
        process = subprocess.Popen(  
            ['catdoc', '-w', file.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except (
        FileNotFoundError,
        ValueError,
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
    ) as err:
        return (None, str(err))
    else:
        stdout, stderr = process.communicate()
 
    return (stdout.strip(), stderr.strip())



def extract_text_from_file(file, name):

    name_tup = os.path.splitext(name)
    extention = name_tup[1]

    logger.info(f"Extension for file {name} is {extention}")

    if extention == ".pdf":
        return extract_text_from_pdf(file)
    elif extention==".docx":
        return extract_text_from_docx(file)
    elif extention==".doc":
        return extract_text_from_doc(file)
    else:
        logger.info(f"Unable to process file with extention {extention}")
        return ""




