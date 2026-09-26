"""Turn uploaded notes (PDF / text / markdown) into plain text chunks."""
import re

import fitz  # PyMuPDF

MAX_CHARS = 60_000  # keep prompts within small-model context windows


def extract_text(filename: str, data: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        with fitz.open(stream=data, filetype="pdf") as doc:
            text = "\n".join(page.get_text() for page in doc)
    else:
        text = data.decode("utf-8", errors="ignore")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:MAX_CHARS]


def chunk(text: str, size=1200, overlap=150) -> list[str]:
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += size - overlap
    return chunks


def relevant_chunks(chunks: list[str], keywords: list[str], k=4) -> list[str]:
    """Cheap keyword retrieval: good enough for a single set of course notes."""
    terms = [w.lower() for kw in keywords for w in re.findall(r"\w{3,}", kw)]
    scored = sorted(
        ((sum(c.lower().count(t) for t in terms), i) for i, c in enumerate(chunks)),
        reverse=True,
    )
    return [chunks[i] for score, i in scored[:k] if score > 0] or chunks[:k]
