
import pandas as pd

try:
    df = pd.read_excel('list.xlsx')
    # strip columns
    df.columns = [c.strip() for c in df.columns]
    
    col = '祝電'
    if col in df.columns:
        print(f"Unique values in '{col}': {df[col].unique()}")
        # Print rows where 祝電 is not null
        subset = df[pd.notna(df[col])]
        print(f"Rows with non-null '{col}':")
        print(subset[['名前', '祝電']])
    else:
        print(f"'{col}' not found.")
except Exception as e:
    print(e)
