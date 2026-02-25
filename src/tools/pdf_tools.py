# src/tools/pdf_tools.py

from pathlib import Path
from typing import List
from pypdf import PdfReader


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]


def extract_chunks(pdf_path: Path) -> List[str]:
    text = extract_text(pdf_path)
    return chunk_text(text)
