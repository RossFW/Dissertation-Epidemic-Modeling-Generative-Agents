"""Generate dissertation.pdf from dissertation.html (Chromium print engine),
then stamp page numbers: title page unnumbered, front matter lower-roman,
body arabic restarting at 1 on Chapter 1 (standard ETD pagination).

The Chromium footer can only emit one continuous arabic sequence, so we
render with no footer and add the numbers afterward with PyMuPDF.
"""
import asyncio, re
from pathlib import Path
from playwright.async_api import async_playwright
import fitz

URL = "http://localhost:8000/dissertation.html"
OUT = Path(__file__).resolve().parent / "Williams_Ross_Dissertation.pdf"
TMP = Path("/tmp/_diss_nofooter.pdf")
MARGIN = {"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"}


async def render(path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=120_000)
        await page.wait_for_timeout(3000)
        await page.pdf(path=str(path), format="Letter", margin=MARGIN,
                       print_background=True, prefer_css_page_size=True,
                       display_header_footer=False)
        await browser.close()


def _roman(n):
    out = ""
    for q, s in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),
                 (50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n >= q:
            out += s; n -= q
    return out


def stamp_page_numbers(src, dst):
    d = fitz.open(src)
    pages = [re.sub(r'\s+', ' ', d[i].get_text()).strip() for i in range(d.page_count)]
    body_start = next(i for i in range(d.page_count) if pages[i].startswith("Chapter 1: Introduction"))
    for i in range(d.page_count):
        if i == 0:           # title page: unnumbered (counts as i)
            continue
        label = _roman(i + 1) if i < body_start else str(i - body_start + 1)
        pg = d[i]
        r = pg.rect
        pg.insert_textbox(fitz.Rect(0, r.height - 52, r.width, r.height - 30),
                          label, fontsize=11, fontname="Times-Roman",
                          align=fitz.TEXT_ALIGN_CENTER, color=(0.27, 0.27, 0.27))
    d.save(str(dst)); d.close()
    return body_start, len(pages)


if __name__ == "__main__":
    asyncio.run(render(TMP))
    bs, n = stamp_page_numbers(TMP, OUT)
    print(f"  wrote {OUT}")
    print(f"  {n} pages; front matter i-{_roman(bs)} (roman), body 1-{n-bs} (arabic), Ch1 at index {bs}")
    print(f"  size: {OUT.stat().st_size:,} bytes")
