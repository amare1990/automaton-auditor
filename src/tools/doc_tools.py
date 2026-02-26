from pathlib import Path
from typing import List
from pypdf import PdfReader


def ingest_pdf(path: Path, chunk_size: int = 1200) -> List[str]:
    """Read PDF defensively and return character-based text chunks."""
    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        # could record exc as Evidence in detective node
        return []

    text = []
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        except Exception:
            continue

    full_text = "\n".join(text)
    return [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]


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
