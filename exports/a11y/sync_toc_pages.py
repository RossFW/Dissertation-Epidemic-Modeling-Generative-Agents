"""Step 3: rewrite every ToC / List of Figures / List of Tables page number
in dissertation.html to match the rendered accessible PDF.

Finds each entry's anchor target in the PDF by its heading/caption text
(monotonic scan, so repeated headings like 'References' resolve in order),
computes the printed label, and rewrites the <span class="toc-page">.
Front-matter entries get roman labels, body entries arabic.
Run freeze_dom.py + build_accessible_pdf.py again afterward (ToC text
itself changes width -> can shift pagination by a page; iterate to fixpoint).
"""
import re, sys
from pathlib import Path
import pymupdf

HERE = Path(__file__).resolve().parent
PDF  = HERE / "Williams_RF_D_2026_accessible.pdf"
HTML = HERE.parent.parent / "viz" / "dissertation.html"

def roman(n):
    out=""; 
    for q,s in [(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n>=q: out+=s; n-=q
    return out

d = pymupdf.open(str(PDF))
pages = [re.sub(r'\s+',' ',d[i].get_text()).strip() for i in range(d.page_count)]
BODY = next(i for i,t in enumerate(pages) if t.startswith("Chapter 1: Introduction"))
def label(i): return roman(i+1) if i < BODY else str(i-BODY+1)

h = HTML.read_text(encoding="utf-8")
strip = lambda s: re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s)).strip()
toc_end = h.index('id="list-of-figures"'); lof_end = h.index('id="list-of-tables"')

pat = re.compile(r'(<a href="#([^"]+)">(.*?)</a></span><span class="toc-page">)([^<]+)(</span>)')
cursor = {"ToC":1, "LoF":BODY, "LoT":BODY}   # ToC may point into front matter; lists only into body
changes=[]; miss=[]
def repl(m):
    pre, anchor, text, old, post = m.groups()
    pos = m.start()
    lst = "ToC" if pos < toc_end else ("LoF" if pos < lof_end else "LoT")
    t = strip(text)
    key = t[:70] if re.match(r'^(Figure|Table) ', t) else t
    start = cursor[lst]
    # skip the front-matter list pages themselves when searching for ToC targets
    found = None
    FRONT = ("Dedication","Acknowledgement","Table of Contents","List of Figures","List of Tables","Abstract","General Audience Abstract")
    for i in range(start, len(pages)):
        if t in FRONT and anchor in ("dedication","acknowledgement","toc","list-of-figures","list-of-tables","abstract","general-audience-abstract"):
            # front-matter sections: the target page STARTS with the title (never a ToC listing line)
            if pages[i].startswith(t): found = i; break
            continue
        if key.lower() in pages[i].lower():
            found = i; break
    if found is None:
        miss.append(t); return m.group(0)
    cursor[lst] = found
    new = label(found)
    if new != old: changes.append((lst, t[:58], old, new))
    return f"{pre}{new}{post}"

h2 = pat.sub(repl, h)
HTML.write_text(h2, encoding="utf-8")
print(f"PDF: {d.page_count} pages, body starts idx {BODY}")
print(f"updated {len(changes)} entries; {len(miss)} not found")
for l,t,o,n in changes[:200]: print(f"  [{l}] {t:60s} {o:>5s} -> {n}")
for t in miss: print("  MISSING:", t)
