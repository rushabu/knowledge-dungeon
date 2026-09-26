"""Render the sample study books in samples/books/<subject>/ to PDF.

    python samples/build_books.py            # all books
    python samples/build_books.py dbms       # one book

Each book folder has meta.json ({"title", "subtitle", "color"}) and chapter files
NN-*.md written in a small markdown subset: # chapter, ## section, ### subsection,
paragraphs, - bullets, 1. numbered items, ``` code ```, > callouts, | tables |,
and inline **bold**, *italic*, `code`.
"""
import json
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, ListFlowable, ListItem, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle, XPreformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parent
BOOKS = ROOT / "books"
OUT = ROOT / "pdf"
FONTS = Path("C:/Windows/Fonts")

# Georgia for reading, Consolas for code; fall back to built-ins elsewhere
if (FONTS / "georgia.ttf").exists():
    pdfmetrics.registerFont(TTFont("Body", str(FONTS / "georgia.ttf")))
    pdfmetrics.registerFont(TTFont("Body-Bold", str(FONTS / "georgiab.ttf")))
    pdfmetrics.registerFont(TTFont("Body-Italic", str(FONTS / "georgiai.ttf")))
    pdfmetrics.registerFont(TTFont("Body-BoldItalic", str(FONTS / "georgiaz.ttf")))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic", boldItalic="Body-BoldItalic")
    pdfmetrics.registerFont(TTFont("Code", str(FONTS / "consola.ttf")))
    # Cambria Math fills in symbols (set operators, join, arrows) the text fonts lack
    pdfmetrics.registerFont(TTFont("Sym", str(FONTS / "cambria.ttc"), subfontIndex=1))
    BODY, BOLD, CODE = "Body", "Body-Bold", "Code"
    COVERED = {f: set(pdfmetrics.getFont(f).face.charToGlyph) for f in ("Body", "Code")}
else:
    BODY, BOLD, CODE = "Times-Roman", "Times-Bold", "Courier"
    COVERED = None

CODE_WRAP = 62  # characters per code line before wrapping


def symbols(text: str, font: str) -> str:
    """Wrap characters the given font can't draw in the symbol font."""
    if not COVERED:
        return text
    have = COVERED[font]
    return "".join(f'<font name="Sym">{c}</font>' if ord(c) > 127 and ord(c) not in have else c for c in text)

INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#666666")


def styles(accent):
    s = {
        "body": ParagraphStyle("body", fontName=BODY, fontSize=11.2, leading=17.4, textColor=INK, spaceAfter=8.5),
        "h1": ParagraphStyle("h1", fontName=BOLD, fontSize=21, leading=26, textColor=accent, spaceAfter=10),
        "chapnum": ParagraphStyle("chapnum", fontName=BODY, fontSize=11, leading=14, textColor=MUTED, spaceAfter=4),
        "h2": ParagraphStyle("h2", fontName=BOLD, fontSize=14, leading=18, textColor=accent, spaceBefore=12, spaceAfter=6, keepWithNext=1),
        "h3": ParagraphStyle("h3", fontName=BOLD, fontSize=11.5, leading=15, textColor=INK, spaceBefore=8, spaceAfter=4, keepWithNext=1),
        "code": ParagraphStyle("code", fontName=CODE, fontSize=8.8, leading=12.2, textColor=INK),
        "callout": ParagraphStyle("callout", fontName=BODY, fontSize=10.6, leading=16, textColor=INK),
        "cell": ParagraphStyle("cell", fontName=BODY, fontSize=9, leading=12, textColor=INK),
        "cellhead": ParagraphStyle("cellhead", fontName=BOLD, fontSize=9, leading=12, textColor=colors.white),
        "title": ParagraphStyle("title", fontName=BOLD, fontSize=30, leading=36, textColor=accent, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle", fontName=BODY, fontSize=13, leading=18, textColor=MUTED, alignment=TA_CENTER),
        "tochead": ParagraphStyle("tochead", fontName=BOLD, fontSize=21, leading=26, textColor=accent, spaceAfter=10),
        "toc1": ParagraphStyle("toc1", fontName=BODY, fontSize=10.5, leading=16, textColor=INK),
    }
    return s


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text: str) -> str:
    # set code spans aside first so * and _ inside them aren't read as formatting
    spans = []

    def stash(m):
        spans.append(symbols(escape(m.group(1)), "Code"))
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = symbols(escape(text), "Body")
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"\^\{([^}]+)\}", r"<super>\1</super>", text)   # x^{2}
    text = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", text)        # x_{i}
    return re.sub(r"\x00(\d+)\x00", lambda m: f'<font face="{CODE}" size="9">{spans[int(m.group(1))]}</font>', text)


class BookDoc(BaseDocTemplate):
    def __init__(self, path, meta, accent):
        super().__init__(str(path), pagesize=A5, leftMargin=16 * mm, rightMargin=16 * mm,
                         topMargin=18 * mm, bottomMargin=20 * mm, title=meta["title"], author="Knowledge Dungeon samples")
        self.meta, self.accent = meta, accent
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([
            PageTemplate("plain", [frame]),
            PageTemplate("body", [frame], onPage=self._decorate),
        ])

    def _decorate(self, canv, doc):
        canv.saveState()
        canv.setFont(BODY, 8)
        canv.setFillColor(MUTED)
        w, _ = A5
        canv.drawString(16 * mm, 10 * mm, self.meta["title"])
        canv.drawRightString(w - 16 * mm, 10 * mm, str(doc.page))
        canv.setStrokeColor(self.accent)
        canv.setLineWidth(0.6)
        canv.line(16 * mm, 13.5 * mm, w - 16 * mm, 13.5 * mm)
        canv.restoreState()

    def afterFlowable(self, f):
        # chapter headings feed the table of contents and the PDF bookmarks
        if isinstance(f, Paragraph) and f.style.name == "h1":
            text = f.getPlainText()
            key = f"ch{self.seq.nextf('chapter')}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=0)
            self.notify("TOCEntry", (0, text, self.page, key))


def parse_chapter(md: str, st, chap_no: int, accent) -> list:
    story, lines, i = [], md.splitlines(), 0
    para: list[str] = []

    def flush():
        if para:
            story.append(Paragraph(inline(" ".join(para)), st["body"]))
            para.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("```"):
            flush()
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            wrapped = []
            for c in code:
                while len(c) > CODE_WRAP:
                    cut = c.rfind(" ", 0, CODE_WRAP)
                    cut = cut if cut > CODE_WRAP // 2 else CODE_WRAP
                    wrapped.append(c[:cut])
                    c = "    " + c[cut:].lstrip()
                wrapped.append(c)
            box = Table([[XPreformatted(symbols(escape("\n".join(wrapped)), "Code"), st["code"])]], colWidths=["100%"])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f4f4")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story += [box, Spacer(1, 8)]
        elif line.startswith("# "):
            flush()
            story += [NextPageTemplate("body"), PageBreak(),
                      Paragraph(f"CHAPTER {chap_no}", st["chapnum"]), Paragraph(inline(line[2:]), st["h1"])]
        elif line.startswith("## "):
            flush()
            story.append(Paragraph(inline(line[3:]), st["h2"]))
        elif line.startswith("### "):
            flush()
            story.append(Paragraph(inline(line[4:]), st["h3"]))
        elif line.startswith("> "):
            flush()
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i][1:].strip())
                i += 1
            box = Table([[Paragraph(inline(" ".join(quote)), st["callout"])]], colWidths=["100%"])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.Color(accent.red, accent.green, accent.blue, alpha=0.08)),
                ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story += [Spacer(1, 3), box, Spacer(1, 9)]
            continue
        elif line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            data = [[Paragraph(inline(c), st["cellhead" if r == 0 else "cell"]) for c in row] for r, row in enumerate(rows)]
            t = Table(data, repeatRows=1, hAlign="LEFT", colWidths=[None] * len(rows[0]))
            t._argW = [ (A5[0] - 32 * mm) / len(rows[0]) ] * len(rows[0])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), accent),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6f6")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story += [t, Spacer(1, 9)]
            continue
        elif re.match(r"^(- |\d+\. )", line):
            flush()
            ordered = bool(re.match(r"^\d+\. ", line))
            items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                text = re.sub(r"^(- |\d+\. )", "", lines[i].rstrip())
                i += 1
                sub = []  # indented "- " lines form a nested bullet list
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    if re.match(r"^\s+- ", lines[i]):
                        sub.append(re.sub(r"^\s+- ", "", lines[i].rstrip()))
                    elif sub:
                        sub[-1] += " " + lines[i].strip()
                    else:
                        text += " " + lines[i].strip()
                    i += 1
                body = [Paragraph(inline(text), st["body"])]
                if sub:
                    body.append(ListFlowable(
                        [ListItem(Paragraph(inline(s), st["body"]), leftIndent=12) for s in sub],
                        bulletType="bullet", start="–", bulletFontName=BODY, bulletFontSize=9, leftIndent=12))
                items.append(ListItem(body, leftIndent=14))
            story.append(ListFlowable(items, bulletType="1" if ordered else "bullet", start="1" if ordered else None,
                                      bulletFontName=BODY, bulletFontSize=9, leftIndent=14,
                                      **({"bulletFormat": "%s."} if ordered else {})))
            continue
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
        i += 1
    flush()
    return story


def build(subject_dir: Path):
    meta = json.loads((subject_dir / "meta.json").read_text(encoding="utf-8"))
    accent = colors.HexColor(meta.get("color", "#3b5bdb"))
    st = styles(accent)
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{subject_dir.name}.pdf"
    doc = BookDoc(out, meta, accent)

    story = [Spacer(1, 55 * mm), Paragraph(meta["title"], st["title"]), Spacer(1, 6 * mm),
             Paragraph(meta.get("subtitle", ""), st["subtitle"]), Spacer(1, 40 * mm),
             Paragraph("Sample study notes · Knowledge Dungeon", st["subtitle"]),
             PageBreak(), Paragraph("Contents", st["tochead"])]
    toc = TableOfContents()
    toc.levelStyles = [st["toc1"]]
    toc.dotsMinLevel = 0
    story.append(toc)

    for n, path in enumerate(sorted(subject_dir.glob("[0-9][0-9]-*.md")), start=1):
        story += parse_chapter(path.read_text(encoding="utf-8"), st, n, accent)

    doc.multiBuild(story)
    return out


if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for d in sorted(p for p in BOOKS.iterdir() if p.is_dir()):
        if not wanted or d.name in wanted:
            out = build(d)
            from pypdf import PdfReader
            print(f"{out.name}: {len(PdfReader(out).pages)} pages")
