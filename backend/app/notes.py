"""Turn uploaded notes (PDF / text / markdown) into plain text, and find the parts about a topic.

PDF headings are marked with markdown #'s (chapters from the PDF outline, sections from font size),
so long books can be split into chapters and chunked along their own section boundaries."""
import math
import re
from collections import Counter

import fitz  # PyMuPDF

MAX_CHARS = 400_000  # roughly a 250-page book; only small slices of it ever reach the LLM


def extract_text(filename: str, data: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        with fitz.open(stream=data, filetype="pdf") as doc:
            text = _pdf_text(doc)
    else:
        text = data.decode("utf-8", errors="ignore")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:MAX_CHARS]


def _norm(s: str) -> str:
    return re.sub(r"\W+", " ", s).strip().lower()


def _pdf_text(doc) -> str:
    # chapters come from the PDF outline: each starts on its page, whatever its title wraps into
    starts = {}
    for level, title, page in doc.get_toc():
        if level == 1 and page >= 1:
            starts.setdefault(page, title.strip())
    pages, sizes, seen = [], Counter(), Counter()
    for page in doc:
        blocks = []
        for b in page.get_text("dict")["blocks"]:
            lines = []
            for line in b.get("lines", []):
                spans = [s for s in line["spans"] if s["text"].strip()]
                if not spans:
                    continue
                text = "".join(s["text"] for s in spans).strip()
                size = max(s["size"] for s in spans)
                bold = all("bold" in s["font"].lower() or s["flags"] & 16 for s in spans)
                sizes[round(size, 1)] += len(text)
                lines.append((text, size, bold))
            if lines:
                blocks.append(lines)
        pages.append(blocks)
        seen.update({_norm(l[0]) for bl in blocks for l in bl})
    body = sizes.most_common(1)[0][0] if sizes else 11
    running = {t for t, n in seen.items() if len(pages) >= 5 and n > len(pages) * 0.3}  # headers/footers

    out, para = [], []

    def heading(text):
        if para:
            out.append("\n".join(para))
            para.clear()
        out.append(text)

    for pno, blocks in enumerate(pages, 1):
        chapter = starts.get(pno)
        if chapter:
            heading(f"# {chapter}")
        for lines in blocks:
            for text, size, bold in lines:
                key = _norm(text)
                if key in running or text.isdigit():
                    continue
                if chapter and size >= body * 1.2 and key and key in _norm(chapter):
                    continue  # the chapter title itself, already emitted
                if not starts and size >= body * 1.6 and len(text) < 80:
                    heading(f"# {text}")
                elif size >= body * 1.2 and len(text) < 80:
                    heading(f"## {text}")
                elif bold and len(lines) == 1 and len(text) < 70:
                    heading(f"### {text}")
                else:
                    para.append(" " + text if text.startswith("#") else text)  # a code comment is not a heading
    heading("")
    return "\n\n".join(out).strip()


def chapters(text: str, level=1) -> list[tuple[str, str]]:
    """(title, text) for each heading of this level; front matter before the first one is dropped."""
    out, fenced, mark = [], False, "#" * level + " "
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        if not fenced and line.startswith(mark):
            out.append([line[len(mark):].strip(), []])
        if out:
            out[-1][1].append(line)
    return [(title, "\n".join(lines).strip()) for title, lines in out]


def parts(text: str, n=10) -> list[tuple[str, str]]:
    """Fallback for long notes without headings: n roughly equal pieces cut at paragraph breaks."""
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    target = len(text) / n
    out, cur = [], []
    for p in paras:
        cur.append(p)
        if sum(map(len, cur)) >= target:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [(f"Part {i + 1}: {c[0].strip().splitlines()[0][:60]}", "\n\n".join(c)) for i, c in enumerate(out)]


def chunk(text: str, size=1200) -> list[str]:
    """Split on headings and blank lines, then pack paragraphs into ~size-char chunks."""
    pieces = []
    for part in (p.strip() for p in re.split(r"\n(?=#{1,6} )|\n\s*\n", text)):
        if len(part) <= size:
            pieces.append(part)
            continue
        cur = ""  # an oversized paragraph (e.g. a PDF page with no blank lines): pack its lines
        for line in part.splitlines():
            if cur and len(cur) + len(line) > size:
                pieces.append(cur)
                cur = ""
            cur = f"{cur}\n{line}" if cur else line
        pieces.append(cur)
    chunks, cur = [], ""
    for part in pieces:
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
