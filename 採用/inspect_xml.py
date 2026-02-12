from docx import Document
import zipfile
import re

template_path = r'd:\code4biz\採用\template\1st_goukaku.docx'

with zipfile.ZipFile(template_path) as z:
    for name in z.namelist():
        if name.startswith('word/') and name.endswith('.xml'):
            content = z.read(name).decode('utf-8')
            if '{{' in content:
                print(f"Found '{{{{' in {name}")
                # Extract context
                matches = re.findall(r'.{0,50}\{\{.*?\}\}.{0,50}', content)
                for m in matches:
                    print(f"  Match: {m}")
            else:
                 pass # print(f"No placeholders in {name}")
