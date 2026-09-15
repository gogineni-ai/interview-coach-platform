from io import BytesIO
from pypdf import PdfReader
from docx import Document

def extract_resume_text(filename: str, data: bytes) -> str:
    lower = filename.lower()

    if lower.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    if lower.endswith(".docx"):
        doc = Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs).strip()

    if lower.endswith(".txt"):
        return data.decode("utf-8", errors="ignore").strip()

    raise ValueError("Supported formats: PDF, DOCX, TXT")
