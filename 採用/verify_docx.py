from docx import Document
import os
import glob
import re

output_dir = r'd:\code4biz\採用\output'
files = glob.glob(os.path.join(output_dir, '*_1st_goukaku.docx'))

if not files:
    print("No generated files found.")
else:
    for f in files:
        print(f"Checking: {os.path.basename(f)}")
        try:
            doc = Document(f)
            found_date = False
            found_time = False
            
            for para in doc.paragraphs:
                # Debug print for relevant lines
                if '日時' in para.text or '面接' in para.text:
                    print(f"DEBUG PARA: {para.text.strip()}")

                # Look for date pattern: YYYY年MM月DD日
                if re.search(r'\d{4}年\d{1,2}月\d{1,2}日', para.text):
                     print(f"FOUND DATE: {para.text.strip()}")
                     found_date = True
                # Look for time pattern: HH:MM
                if re.search(r'\d{1,2}:\d{2}', para.text):
                     print(f"FOUND TIME: {para.text.strip()}")
                     found_time = True

            print(f"Date Verified: {found_date}")
            print(f"Time Verified: {found_time}")

        except Exception as e:
            print(f"Error reading {f}: {e}")
