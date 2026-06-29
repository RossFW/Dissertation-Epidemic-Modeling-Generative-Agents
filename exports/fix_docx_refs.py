"""Normalize the reference-list font in a pdf2docx-generated .docx.

pdf2docx faithfully reproduces the PDF, where reference entries are set a bit
smaller than the body (11pt vs 12pt -> ~8.5pt vs ~9.0pt in the scaled docx
coordinate space). In Word that size gap reads as the references not matching
the rest of the paper. This bumps reference-entry runs up to the body size and
pins them to Times New Roman, leaving everything else (incl. keyword lines and
captions) untouched.

Usage: fix_docx_refs.py <path-to.docx>
"""
import sys, re
from docx import Document
from docx.shared import Pt
from docx.text.paragraph import Paragraph

BODY_PT = 9.0      # dominant body run size in the pdf2docx docx (== 12pt visual)
REF_PT  = 8.5      # reference-entry run size (== 11pt visual)
TOL     = 0.15
# a paragraph that begins (or contains, after a line break) a numbered ref entry
REF_RE  = re.compile(r'(?:^|\n)\s*\d+\.\s+[A-Z]')

def iter_paras(doc):
    for el in doc.element.body.iter():
        if el.tag.endswith('}p'):
            yield Paragraph(el, doc)

def main(path):
    doc = Document(path)
    changed = 0
    para_hits = 0
    for p in iter_paras(doc):
        if not REF_RE.search(p.text):
            continue
        para_hits += 1
        for r in p.runs:
            sz = r.font.size.pt if r.font.size else None
            if sz is not None and abs(sz - REF_PT) < TOL:
                r.font.size = Pt(BODY_PT)
                r.font.name = "Times New Roman"
                changed += 1
    doc.save(path)
    print(f"  fix_docx_refs: {changed} reference runs -> {BODY_PT}pt TNR "
          f"across {para_hits} reference paragraphs")

if __name__ == "__main__":
    main(sys.argv[1])
