#!/bin/bash
# Build dissertation.pdf and dissertation.docx from dissertation.html.
# Pipeline: Chromium print engine (Playwright) → PDF → pdf2docx → docx.
# The PDF preserves all CSS styling; the docx is derived from the PDF for fidelity.
#
# Requirements:
#   - dissertation server up: cd ../viz && python3 editor_server.py 8000 &
#   - python venv with playwright + pdf2docx at /tmp/pwvenv
set -e
cd "$(dirname "$0")"

# sanity: dissertation server up?
if ! curl -s -o /dev/null --max-time 2 http://localhost:8000/dissertation.html; then
  echo "  ✗ no server on localhost:8000 — start it first:"
  echo "    cd ../viz && python3 editor_server.py 8000 &"
  exit 1
fi

# sanity: pwvenv has what we need?
if [ ! -x /tmp/pwvenv/bin/python3 ]; then
  echo "  ✗ /tmp/pwvenv missing — recreate with:"
  echo "    python3 -m venv /tmp/pwvenv && /tmp/pwvenv/bin/pip install playwright pdf2docx && /tmp/pwvenv/bin/playwright install chromium"
  exit 1
fi

echo "  [1/2] Generating PDF (Chromium print engine, respects CSS)..."
/tmp/pwvenv/bin/python3 ./build_pdf.py

echo "  [2/2] Converting PDF → docx (pdf2docx)..."
/tmp/pwvenv/bin/python3 ./pdf_to_docx.py

echo ""
echo "  Outputs:"
ls -la dissertation.pdf dissertation.docx 2>/dev/null
