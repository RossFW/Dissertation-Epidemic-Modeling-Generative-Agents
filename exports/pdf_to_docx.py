"""Convert dissertation.pdf to dissertation.docx via pdf2docx."""
from pdf2docx import Converter
import time, os
SRC = "/Users/rosswilliams/Desktop/Dissertation/Dissertation Draft/exports/dissertation.pdf"
DST = "/Users/rosswilliams/Desktop/Dissertation/Dissertation Draft/exports/dissertation.docx"

if __name__ == "__main__":
    t0 = time.monotonic()
    cv = Converter(SRC)
    # single-process is slower but doesn't fight macOS spawn
    cv.convert(DST)
    cv.close()
    print(f"  converted in {time.monotonic()-t0:.1f}s")
    print(f"  size: {os.path.getsize(DST):,} bytes")
