"""Step 2 of the accessible-PDF build: tagged PDF/UA via WeasyPrint.

Reads the frozen (JS-already-run) HTML, injects a small WeasyPrint-
specific stylesheet, and writes a tagged PDF/UA-1 file. Pagination is
done natively with CSS @page counters (title unnumbered, front matter
roman, body arabic) so page numbers are real tagged content rather than
stamped-on artwork.
"""
import logging, re, sys, time
from pathlib import Path
from weasyprint import HTML, CSS

logging.getLogger('weasyprint').setLevel(logging.ERROR)
HERE = Path(__file__).resolve().parent
BODY_PT = float(sys.argv[1]) if len(sys.argv) > 1 else 11.0
SRC  = HERE / "dissertation_frozen.html"
OUT  = HERE / "Williams_RF_D_2026_accessible.pdf"

WEASY_CSS = """
/* WeasyPrint cannot paginate a flex container; make the page root a block. */
#app { display: block !important; max-width: none !important; padding: 0 !important; margin: 0 !important; }
body { padding: 0 !important; }

/* ── Three page groups ───────────────────────────────────────── */
@page            { size: letter; margin: 1in; @bottom-center { content: none; } }
@page front      { @bottom-center { content: counter(page, lower-roman); font-family: 'Times New Roman', serif; font-size: 11pt; color: #444; } }
@page body       { @bottom-center { content: none; } }  /* arabic stamped post-render */

.titlepage   { page: title; }
.frontmatter { page: front; }
.chapter, #appendices { page: body; }

/* Title page counts as i; roman continues from ii. Body restarts at 1. */


/* Page breaks (were swallowed by flex). */
.titlepage, .frontmatter { break-after: page; }
.chapter, #appendices   { break-before: page; }

/* Keep headings with following content. */
h1, h2, h3, h4 { break-after: avoid; }
/* Image figures stay whole; a tall TABLE may break between rows (its
   <thead> repeats automatically) -- forcing avoid orphaned captions. */
figure:not(:has(table)):not(:has(img[style*='break-before'])) { break-inside: avoid; }
/* appendix image wrappers: single images stay whole; multi-part ones may break */
div.section:not(:has(img[style*='break-before'])) { break-inside: avoid; }
figure > figcaption { break-after: avoid; }
figure > table { break-before: avoid; }
tr { break-inside: avoid; }
ol[data-refs="cites"] > li { break-inside: avoid; }

/* Body size: BODY_PT is substituted at build time. */
p, li, ul, ol { font-size: BODY_PTpt !important; }
/* tables keep their authored sizes (Table 4 is 11 columns at 9.5pt) */
/* Wide numeric tables: tight cell padding so 11 columns fit the 6.5in body
   (WeasyPrint honors min-content width; Chrome silently squeezed it). */
table { table-layout: auto; max-width: 100%; }
table th, table td { padding: 4px 5px !important; }
table td, table th { word-break: normal; overflow-wrap: normal; white-space: normal; }
/* numbers-with-stars cells must not wrap mid-token */
table td { hyphens: none; }
/* Table 4 (11 numeric columns) genuinely needs a smaller face to fit 6.5in */
figure:has(#table-4) table { font-size: 8.5pt !important; }
figure:has(#table-4) table th, figure:has(#table-4) table td { padding: 3px 4px !important; }
"""

def stamp_arabic(path):
    """WeasyPrint cannot reset the page counter mid-document, so the body's
    arabic numbers are added here. Roman numerals on the front matter are
    native CSS output and untouched."""
    import pymupdf
    d = pymupdf.open(str(path))
    pages = [re.sub(r"\s+", " ", d[i].get_text()).strip() for i in range(d.page_count)]
    body = next(i for i, t in enumerate(pages) if t.startswith("Chapter 1: Introduction"))
    for i in range(body, d.page_count):
        pg = d[i]; r = pg.rect
        pg.insert_textbox(pymupdf.Rect(0, r.height - 52, r.width, r.height - 30), str(i - body + 1),
                          fontsize=11, fontname="Times-Roman", align=pymupdf.TEXT_ALIGN_CENTER,
                          color=(0.27, 0.27, 0.27))
    tmp = path.with_suffix(".tmp.pdf"); d.save(str(tmp)); d.close(); tmp.replace(path)
    return body, len(pages)

def main():
    t0 = time.time()
    css = WEASY_CSS.replace("BODY_PT", str(BODY_PT))
    doc = HTML(filename=str(SRC), base_url="http://localhost:8000/").render(
        stylesheets=[CSS(string=css)])
    doc.write_pdf(str(OUT), pdf_variant="pdf/ua-1")
    body, n = stamp_arabic(OUT)
    print(f"wrote {OUT.name}: {n} pages, {OUT.stat().st_size:,} bytes, {time.time()-t0:.0f}s")
    print(f"  front matter i-roman({body}), body 1-{n-body}, Ch1 at index {body}")

if __name__ == "__main__":
    main()
