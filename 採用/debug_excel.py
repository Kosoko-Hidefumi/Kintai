import pandas as pd
import os

file_path = r'd:\code4biz\採用\data\applicant_list.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(df.head())
    print("-" * 20)
    print("Columns:", df.columns)
    if '一次合否' in df.columns:
        print("Pass counts:", df['一次合否'].value_counts())
else:
    print("File not found")
