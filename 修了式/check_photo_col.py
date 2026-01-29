
import pandas as pd

try:
    df = pd.read_excel('list.xlsx')
    col = '写真配布'
    if col in df.columns:
        print(f"Unique values in '{col}': {df[col].unique()}")
        print(f"First 10 values: {df[col].head(10).tolist()}")
    else:
        print(f"'{col}' not found.")
except Exception as e:
    print(e)
