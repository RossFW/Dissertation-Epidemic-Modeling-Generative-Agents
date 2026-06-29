"""Convert Williams_Ross_Dissertation.pdf to .docx via pdf2docx, then
normalize the reference-list font to match the body (see fix_docx_refs.py)."""
from pdf2docx import Converter
import time, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Williams_Ross_Dissertation.pdf")
DST = os.path.join(HERE, "Williams_Ross_Dissertation.docx")

if __name__ == "__main__":
    t0 = time.monotonic()
    cv = Converter(SRC)
    cv.convert(DST)          # single-process: slower but avoids macOS spawn issues
    cv.close()
    print(f"  converted in {time.monotonic()-t0:.1f}s")
    # match reference-list font size to the body
    subprocess.run([sys.executable, os.path.join(HERE, "fix_docx_refs.py"), DST], check=True)
    print(f"  size: {os.path.getsize(DST):,} bytes")
