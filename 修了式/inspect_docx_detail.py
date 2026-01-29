
from docx import Document
import os

files = ['template_general.docx', 'template_guest.docx']

for f in files:
    if os.path.exists(f):
        print(f"--- {f} ---")
        doc = Document(f)
        for i, p in enumerate(doc.paragraphs[:10]):
            print(f"P{i}: '{p.text}'")
            # Also inspect runs to see if split
            runs = [r.text for r in p.runs]
            print(f"  Runs: {runs}")
