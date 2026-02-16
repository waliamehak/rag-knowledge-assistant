import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text_from_pdf(file_path):
    # Extract text from a PDF file
    text = ""
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def chunk_text(text):
    # Split text into chunks respecting sentence boundaries
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_text(text)
    return chunks
