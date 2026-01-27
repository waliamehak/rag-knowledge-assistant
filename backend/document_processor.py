import PyPDF2


def extract_text_from_pdf(file_path):
    # Extract text from a PDF file
    text = ""
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def chunk_text(text, chunk_size=512, overlap=50):
    # Split text into chunks with overlap
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
