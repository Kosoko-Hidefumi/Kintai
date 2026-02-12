import pandas as pd
import os

file_path = r'd:\code4biz\採用\data\applicant_list.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print("--- Data Inspection ---")
    # Filter for the relevant applicant
    target = df[df['名前'].str.contains('兼堅', na=False)]
    if not target.empty:
        row = target.iloc[0]
        val = row['面接日']
        print(f"Applicant: {row['名前']}")
        print(f"Raw Date Value: {val!r}")
        print(f"Raw Date Type: {type(val)}")
        
        # Test pd.to_datetime behavior
        try:
             dt = pd.to_datetime(val)
             print(f"pd.to_datetime result: {dt}")
        except Exception as e:
             print(f"pd.to_datetime error: {e}")
    else:
        print("Applicant '兼堅' not found.")
        print("Head of data:")
        print(df.head())
else:
    print("File not found")
