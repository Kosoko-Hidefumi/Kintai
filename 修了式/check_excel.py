
import pandas as pd
import os

f = 'list.xlsx'
if os.path.exists(f):
    print(f"--- {f} ---")
    try:
        df = pd.read_excel(f)
        print("Columns:", df.columns.tolist())
        print(df.head(3))
    except Exception as e:
        print(f"Error reading {f}: {e}")
else:
    print(f"{f} not found")
