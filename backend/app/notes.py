"""Turn uploaded notes (PDF / text / markdown) into plain text, and find the parts about a topic."""
import math
import re
from collections import Counter

import fitz  # PyMuPDF

MAX_CHARS = 60_000  # keep prompts within model context windows


def extract_text(filename: str, data: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        with fitz.open(stream=data, filetype="pdf") as doc:
            text = "\n".join(page.get_text() for page in doc)
    else:
        text = data.decode("utf-8", errors="ignore")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:MAX_CHARS]


def chunk(text: str, size=1200) -> list[str]:
    """Split on headings and blank lines, then pack paragraphs into ~size-char chunks."""
    parts = re.split(r"\n(?=#{1,6} )|\n\s*\n", text)
    chunks, cur = [], ""
    for part in (p.strip() for p in parts):
        if not part:
            continue
        starts_section = part.startswith("#")
        if cur and (starts_section or len(cur) + len(part) > size):
            chunks.append(cur)
            cur = ""
        cur = f"{cur}\n{part}" if cur else part
    if cur:
        chunks.append(cur)
    return chunks


def _terms(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z0-9'-]{2,}", text.lower())


def relevant_chunks(chunks: list[str], title: str, keywords: list[str], k=3) -> list[str]:
    """TF-IDF-style retrieval: rare topic words count for more than words used everywhere."""
    if not chunks:
        return []
    docs = [Counter(_terms(c)) for c in chunks]
    df = Counter(t for d in docs for t in d)
    idf = {t: math.log((1 + len(docs)) / (1 + n)) + 1 for t, n in df.items()}
    title_terms = set(_terms(title))
    query = Counter(_terms(title)) + Counter(_terms(" ".join(keywords)))

    def score(i):
        d = docs[i]
        s = sum(qn * (1 + math.log(d[t])) * idf[t] for t, qn in query.items() if d[t])
        heading = chunks[i].splitlines()[0].lower()
        if heading.startswith("#") and title_terms & set(_terms(heading)):
            s *= 2  # the section *about* this topic beats sections that mention it
        return s

    scores = [score(i) for i in range(len(chunks))]
    ranked = sorted(range(len(chunks)), key=scores.__getitem__, reverse=True)
    best = scores[ranked[0]]
    if best <= 0:
        return chunks[:k]
    # keep only chunks close to the best match, so neighbouring topics don't leak in
    return [chunks[i] for i in ranked[:k] if scores[i] >= 0.6 * best]
