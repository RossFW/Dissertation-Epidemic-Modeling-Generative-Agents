"""Generate dissertation.pdf from dissertation.html using Chromium's print engine.

The HTML's @media print + @page rules give us letter paper, 1in margins,
chapter page breaks, and hidden TODO notes. Citation JS finishes before we
print so '(N)' numbers appear in the PDF.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

URL = "http://localhost:8000/dissertation.html"
OUT = Path("/Users/rosswilliams/Desktop/Dissertation/Dissertation Draft/exports/dissertation.pdf")
OUT.parent.mkdir(exist_ok=True)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=120_000)
        # let citation renderer finish + give layout time to settle
        await page.wait_for_timeout(3000)
        # Page-number footer. Chromium replaces <span class="pageNumber">
        # at print time. Empty header avoids clashing with the in-page
        # running header (dissertation title + author) on chapters.
        footer = (
            '<div style="font-size:10px; width:100%; text-align:center; '
            'font-family:Georgia,serif; color:#444; padding-bottom:0.3in;">'
            '<span class="pageNumber"></span>'
            '</div>'
        )
        await page.pdf(
            path=str(OUT),
            format="Letter",
            margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template='<div></div>',
            footer_template=footer,
        )
        print(f"  wrote {OUT}")
        print(f"  size: {OUT.stat().st_size:,} bytes")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
