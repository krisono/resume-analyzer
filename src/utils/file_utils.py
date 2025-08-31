from io import BytesIO
from typing import Tuple
from pdfminer.high_level import extract_text as pdf_extract
from docx import Document

def read_file_content(file_storage) -> Tuple[str, str]:
    filename = (file_storage.filename or "").lower()
    data = file_storage.read()
    if filename.endswith(".pdf"):
        text = pdf_extract(BytesIO(data))
        return text, "application/pdf"
    elif filename.endswith(".docx"):
        doc = Document(BytesIO(data))
        text = "\n".join(p.text for p in doc.paragraphs)
        return text, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".txt"):
        return data.decode("utf-8", errors="ignore"), "text/plain"
    else:
        return data.decode("utf-8", errors="ignore"), "application/octet-stream"