#!/usr/bin/env python3
"""Re-export Ch4 main figures from paper.html CHART-ONLY (no baked caption).

Each figure in paper.html is <figure><div chart/><figcaption>Figure N. …</figcaption></figure>.
The old PNGs baked the figcaption in, duplicating (and now mis-numbering) the
dissertation's HTML caption. This hides every figcaption, then screenshots each
<figure> element to Figure_N.png (same filename; HTML caption supplies the label).

Usage: export_main_figs.py <out_dir> <test|full> [scale]
"""
import sys, os, subprocess, time, socket, contextlib
from playwright.sync_api import sync_playwright

OUT=sys.argv[1]; MODE=sys.argv[2] if len(sys.argv)>2 else "test"; SCALE=float(sys.argv[3]) if len(sys.argv)>3 else 2.0
PAPER_VIZ="/Users/rosswilliams/Desktop/Dissertation/Paper 3 - LLM Sensitivity/GABM mobility curve/viz"
TARGET=set([1]+list(range(3,22)))   # 1, 3..21  (no 2 = native-HTML prompt template)
TEST={1,4}
os.makedirs(OUT,exist_ok=True)

def free_port():
    s=socket.socket(); s.bind(("",0)); p=s.getsockname()[1]; s.close(); return p
PORT=free_port()
srv=subprocess.Popen(["python3","-m","http.server",str(PORT)],cwd=PAPER_VIZ,
                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1.5)
    with sync_playwright() as pw:
        b=pw.chromium.launch()
        pg=b.new_context(device_scale_factor=SCALE,viewport={"width":1200,"height":2400}).new_page()
        pg.goto(f"http://localhost:{PORT}/paper.html",wait_until="networkidle",timeout=120000)
        pg.wait_for_timeout(6000)   # let JS charts render
        nums=pg.evaluate(r"""() => {
            const found=[];
            document.querySelectorAll('figure').forEach(fig => {
                const cap=fig.querySelector('figcaption');
                if(!cap) return;
                const m=(cap.textContent||'').trim().match(/^Figure (\d+)\./);
                if(!m) return;
                fig.setAttribute('data-mainfig', m[1]);
                cap.style.display='none';      // drop the baked caption
                found.push(parseInt(m[1]));
            });
            return found;
        }""")
        want = (TEST if MODE=="test" else TARGET)
        todo=[n for n in nums if n in want]
        print(f"figures found: {sorted(nums)}; exporting {sorted(todo)} at scale {SCALE}")
        for n in todo:
            el=pg.query_selector(f'[data-mainfig="{n}"]')
            if not el: print(f"  !! no element Figure {n}"); continue
            el.screenshot(path=os.path.join(OUT,f"Figure_{n}.png"))
            print(f"  wrote Figure_{n}.png")
        b.close()
finally:
    srv.terminate()
    with contextlib.suppress(Exception): srv.wait(timeout=5)
