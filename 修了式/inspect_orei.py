
from docx import Document
import os

files = ['orei_shukuji.docx', 'orei_shukuden.docx', 'orei_general.docx']

for f in files:
    if os.path.exists(f):
        print(f"--- {f} ---")
        try:
            doc = Document(f)
            # Inspect first 10 paragraphs
            for i, p in enumerate(doc.paragraphs[:10]):
                print(f"P{i}: '{p.text}'")
                # print runs to see if split
                # print([r.text for r in p.runs])
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"MISSING: {f}")
