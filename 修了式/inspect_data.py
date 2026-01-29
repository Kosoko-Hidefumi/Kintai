
import pandas as pd
import os

files = ['list.xlsx', '研修医一覧.xlsx', '施設リスト.csv']

for f in files:
    if os.path.exists(f):
        print(f"--- {f} ---")
        try:
            if f.endswith('.csv'):
                df = pd.read_csv(f, encoding='utf-8') # Attempt utf-8 first
            else:
                df = pd.read_excel(f)
            print(df.head())
            print(df.columns.tolist())
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"{f} not found")
