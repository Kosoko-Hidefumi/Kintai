from docx import Document
import os
import glob
import re

output_dir = r'd:\code4biz\採用\output\2nd_fugoukaku'
files = glob.glob(os.path.join(output_dir, '*_2nd_fugoukaku*.docx'))

if not files:
    print(f"No generated files found in {output_dir}")
else:
    for f in files:
        print(f"Checking: {os.path.basename(f)}")
        try:
            doc = Document(f)
            found_name = False
            
            for para in doc.paragraphs:
                if 'テスト 二次待ち子' in para.text:
                     print(f"FOUND NAME: {para.text.strip()}")
                     found_name = True
                elif '高良' in para.text:
                     print(f"FOUND NAME: {para.text.strip()}")
            
            # Check if we are checking the test file
            if 'テスト' in os.path.basename(f):
                print(f"Name Correct: {found_name}")

        except Exception as e:
            print(f"Error reading {f}: {e}")
