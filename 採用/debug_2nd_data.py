import pandas as pd
import os

file_path = r'd:\code4biz\採用\data\applicant_list_temp.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print("--- Data Inspection ---")
    print("Columns:", df.columns)
    if '二次合否' in df.columns:
        print("Tail of data (newly added row should be here):")
        print(df.tail(1)[['名前', '二次合否']])
        
        last_val = df.tail(1)['二次合否'].iloc[0]
        print(f"Last Value: {last_val!r}")
        print(f"Is Null: {pd.isna(last_val)}")
        
        # Test the filter logic
        df['二次合否'] = df['二次合否'].astype(str).replace('nan', '')
        print(f"Converted Last Value: {df.tail(1)['二次合否'].iloc[0]!r}")
        
        target = df[df['二次合否'] == '']
        print(f"Filter count: {len(target)}")
else:
    print("Temp file not found")
