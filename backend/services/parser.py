"""
Parser — extracts raw text from .txt, .pdf, and .docx files.
"""

import io


def parse_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def parse_pdf(content: bytes) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def parse_docx(content: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(content))
    return "\n".join([para.text for para in doc.paragraphs])


def parse_file(filename: str, content: bytes) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "txt":
        return parse_txt(content)
    elif ext == "pdf":
        return parse_pdf(content)
    elif ext == "docx":
        return parse_docx(content)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")
