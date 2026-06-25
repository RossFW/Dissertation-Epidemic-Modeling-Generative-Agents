#!/usr/bin/env python3
"""Re-export Paper-3 appendix tables/figures from paper.html with the
dissertation's consolidated appendix letters (A->D, B->E, C->F).

The labels ("Table A.1.1", "Figure C.1.1") live in paper.html's .fig-num
divs; this script loads paper.html (served locally so its CSV fetches work),
rewrites every .fig-num prefix A/B/C -> D/E/F in the DOM, then screenshots
each appendix-item <div.section> to <newname>.png.

Usage:
  export_appendix_figs.py <out_dir> <mode> [scale]
    mode = test  -> only D.1.1 (a table) and F.1.1 (a figure)
    mode = full  -> all units
    scale        -> deviceScaleFactor (default 2.0; tune to hit 1326px width)
"""
import sys, os, subprocess, time, contextlib, socket
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "test"
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
PAPER_VIZ = "/Users/rosswilliams/Desktop/Dissertation/Paper 3 - LLM Sensitivity/GABM mobility curve/viz"
TEST_UNITS = {"D.1.1", "F.1.1"}

os.makedirs(OUT, exist_ok=True)

def free_port():
    s = socket.socket(); s.bind(("", 0)); p = s.getsockname()[1]; s.close(); return p

PORT = free_port()
srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT)], cwd=PAPER_VIZ,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(1.5)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(device_scale_factor=SCALE, viewport={"width": 1200, "height": 2000}).new_page()
        page.goto(f"http://localhost:{PORT}/paper.html", wait_until="networkidle", timeout=120000)
        # let JS-rendered regression tables / diagnostic charts settle
        page.wait_for_timeout(5000)

        units = page.evaluate(r"""() => {
            const map = {A:'D', B:'E', C:'F'};
            const found = [];
            document.querySelectorAll('.fig-num').forEach(fn => {
                const t = (fn.textContent || '').trim();
                const m = t.match(/^(Table|Figure) ([ABC])\.([0-9.]+)$/);
                if (m) {
                    const newName = map[m[2]] + '.' + m[3];
                    fn.closest('.section').setAttribute('data-export', newName);
                    found.push(newName);
                }
            });
            // relabel ALL fig-nums for display
            document.querySelectorAll('.fig-num').forEach(fn => {
                let t = fn.textContent;
                t = t.replace(/^A\./,'D.').replace(/^B\./,'E.').replace(/^C\./,'F.');
                t = t.replace('Appendix A','Appendix D').replace('Appendix B','Appendix E').replace('Appendix C','Appendix F');
                t = t.replace('Table A','Table D').replace('Table B','Table E').replace('Table C','Table F');
                t = t.replace('Figure A','Figure D').replace('Figure B','Figure E').replace('Figure C','Figure F');
                fn.textContent = t;
            });
            return found;
        }""")

        if MODE == "test":
            units = [u for u in units if u in TEST_UNITS]
        print(f"exporting {len(units)} unit(s) at scale {SCALE}")
        for u in units:
            el = page.query_selector(f'[data-export="{u}"]')
            if not el:
                print(f"  !! no element for {u}"); continue
            el.screenshot(path=os.path.join(OUT, f"{u}.png"))
            print(f"  wrote {u}.png")
        browser.close()
finally:
    srv.terminate()
    with contextlib.suppress(Exception):
        srv.wait(timeout=5)
