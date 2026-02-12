import pandas as pd
import os

file_path = r'd:\code4biz\採用\data\applicant_list_temp.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    # Add a dummy row with empty 2nd pass
    new_row = {
        '名前': 'テスト 二次待ち子',
        '郵便番号': '000-0000',
        '住所': 'テスト県テスト市',
        '電話番号': '090-0000-0000',
        '一次合否': '◯', # 1st pass Pass (shouldn't matter per new logic, but realistic)
        '二次合否': '' # Empty!
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(file_path, index=False)
    print("Added test data.")
else:
    print("File not found")
