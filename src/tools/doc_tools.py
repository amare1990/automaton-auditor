from pathlib import Path
from typing import List
from pypdf import PdfReader


def ingest_pdf(path: Path) -> List[str]:
    """Read PDF and return a list of text chunks (RAG-lite chunking)."""
    reader = PdfReader(str(path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    # simple chunking by characters; downstream code can do smarter splitting
    chunk_size = 1200
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def extract_file_paths_from_text(text: str) -> List[str]:
    """Very small helper to find likely file paths mentioned in a report.

    This is intentionally simple for interim: looks for 'src/' occurrences and
    extracts the token and following path characters.
    """
    paths = []
    for part in text.split():
        if part.startswith("src/"):
            # strip punctuation
            p = part.strip(".,;()[]<>'\"")
            paths.append(p)
    return paths
