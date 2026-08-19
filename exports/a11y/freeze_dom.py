"""Step 1 of the accessible-PDF build.

Load dissertation.html in headless Chromium so the per-chapter citation
renderer runs, then serialize the *resulting* DOM to a static HTML file.
WeasyPrint does not execute JavaScript, so it needs the numbers baked in.

Also strips editor-only artifacts (toolbar, contenteditable) and both
<script> blocks, which have no place in the print document.
"""
import asyncio, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

URL = "http://localhost:8000/dissertation.html"
OUT = Path(__file__).resolve().parent / "dissertation_frozen.html"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto(URL, wait_until="networkidle", timeout=120_000)
        await pg.wait_for_timeout(2000)
        html = await pg.evaluate("""() => {
            const root = document.documentElement.cloneNode(true);
            root.querySelector('#editor-toolbar')?.remove();
            root.querySelectorAll('[contenteditable]').forEach(e => e.removeAttribute('contenteditable'));
            root.querySelectorAll('script').forEach(e => e.remove());
            return '<!DOCTYPE html>\\n' + root.outerHTML + '\\n';
        }""")
        await b.close()
    OUT.write_text(html, encoding="utf-8")
    n_cites = len(re.findall(r'class="cite-group"[^>]*>\(\d', html))
    print(f"wrote {OUT}  ({len(html):,} chars)")
    print(f"rendered citation groups: {n_cites}")
    print(f"remaining <script>: {html.count('<script')}")

asyncio.run(main())
