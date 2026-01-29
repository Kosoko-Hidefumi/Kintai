
import pandas as pd

try:
    df = pd.read_excel('list.xlsx')
    print("Columns:", df.columns.tolist())
    if '祝辞' in df.columns:
        print("Column '祝辞' found.")
        print("Values:", df['祝辞'].unique())
    else:
        print("Column '祝辞' NOT found.")
        
    if '肩書き' in df.columns and '名前' in df.columns:
        print("Required columns '肩書き', '名前' found.")
except Exception as e:
    print(e)
