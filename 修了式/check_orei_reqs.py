
import pandas as pd
import os

print("--- Check Columns ---")
try:
    df = pd.read_excel('list.xlsx')
    cols = [c.strip() for c in df.columns]
    print("Columns:", cols)
    for col in ['写真配布', '祝電', '祝辞']:
        if col in cols:
            print(f"'{col}' found. Unique values: {df[col].unique()}")
        else:
            print(f"'{col}' NOT found.")
except Exception as e:
    print(e)

print("\n--- Check Templates ---")
templates = ['orei_shukuji.docx', 'orei_shukuden.docx', 'orei_general.docx']
for t in templates:
    if os.path.exists(t):
        print(f"OK: {t}")
    else:
        print(f"MISSING: {t}")
