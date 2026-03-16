"""
データ処理用のモジュール
Excelファイルを読み込んで、Web表示用のデータを返す
"""
import os
import re
import pandas as pd
from typing import Dict, List, Optional
from kibetu_list import (
    normalize_name, normalize_facility_name, is_okinawa_birthplace,
    is_okinawa_facility, classify_status, calculate_statistics,
    get_names_by_category, OKINAWA_FACILITIES_RAW
)
from openai import OpenAI


def process_master_file(master_file_path: str) -> Dict:
    """
    マスターファイルを処理して、Web表示用のデータを返す
    
    Parameters:
    -----------
    master_file_path : str
        マスターファイルのパス
    
    Returns:
    --------
    dict
        {
            'periods': [
                {
                    'period': 47,
                    'data': [...],  # 各期のデータ
                    'statistics': {...},  # 集計結果
                    'names_by_category': {...}  # カテゴリごとの名前リスト
                }
            ],
            'summary_statistics': [...]  # 全体の集計結果
        }
    """
    # ファイルの存在確認
    if not os.path.exists(master_file_path):
        raise FileNotFoundError(f"ファイルが見つかりません: {master_file_path}")
    
    # mainシートからマスターデータを読み込む（ヘッダー行を探す）
    df_temp = pd.read_excel(master_file_path, sheet_name='main', engine='openpyxl', header=None, nrows=10)
    
    # ヘッダー行を探す
    header_row = None
    for idx in range(len(df_temp)):
        row_values = df_temp.iloc[idx].values
        row_str = ' '.join([str(v) for v in row_values if pd.notna(v)])
        if '年度' in row_str and '名前' in row_str:
            header_row = idx
            break
    
    if header_row is None:
        raise ValueError("ヘッダー行が見つかりません。'年度'と'名前'を含む行を探しましたが見つかりませんでした。")
    
    # ヘッダー行を指定して再度読み込み
    df_master = pd.read_excel(master_file_path, sheet_name='main', engine='openpyxl', header=header_row)
    
    # 空白列を削除
    df_master = df_master.loc[:, ~df_master.columns.str.contains('^Unnamed')]
    df_master = df_master.dropna(axis=1, how='all')
    df_master = df_master.dropna(how='all')
    
    # 正規化された名前列を追加
    df_master['名前_正規化'] = df_master['名前'].apply(normalize_name)
    
    # 必須列の確認
    required_columns = ['年度', '学年', '名前', '進路']
    missing_columns = [col for col in required_columns if col not in df_master.columns]
    if missing_columns:
        raise ValueError(f"必須列が不足しています: {missing_columns}")
    
    # '初・後'列の確認
    ki_column = None
    for col in df_master.columns:
        if '初' in str(col) or '後' in str(col) or '期' in str(col):
            ki_column = col
            break
    
    if ki_column is None:
        raise ValueError("'初・後'または期を表す列が見つかりません")
    
    # 終了進路のリスト
    end_statuses = ['転出', '修了', '中断', '退職']
    
    # 期番号を抽出（47期〜59期）
    df_master['期番号'] = df_master[ki_column].astype(str).str.extract(r'(\d+)期')[0].astype(float)
    # 後期・受入で期番号が取れない行は年度から推測（期 ≈ 年度 - 1965、例: 2024年度→59期）
    ki_vals = df_master[ki_column].astype(str).str.strip()
    has_kouki_or_junyu = ki_vals.str.contains('後期', na=False) | ki_vals.str.contains('受入', na=False)
    need_fill = has_kouki_or_junyu & df_master['期番号'].isna()
    if need_fill.any() and '年度' in df_master.columns:
        def infer_ki(row):
            y = row.get('年度')
            if pd.notna(y):
                s = str(y).strip()
                m = re.search(r'(\d{4})', s)
                if m:
                    y_int = int(m.group(1))
                    ki = y_int - 1965
                    return ki if 47 <= ki <= 59 else 59
                try:
                    y_int = int(float(s))
                    ki = y_int - 1965
                    return ki if 47 <= ki <= 59 else 59
                except (ValueError, TypeError):
                    pass
            return 59.0
        df_master.loc[need_fill, '期番号'] = df_master.loc[need_fill].apply(infer_ki, axis=1)
    if need_fill.any():
        still_na = need_fill & df_master['期番号'].isna()
        if still_na.any():
            df_master.loc[still_na, '期番号'] = 59.0
    # 初期・後期・受入のすべてを含める（47期〜59期）
    df_filtered = df_master[df_master['期番号'].between(47, 59)]
    
    if len(df_filtered) == 0:
        raise ValueError("処理対象のデータがありません")
    
    # OpenAI APIクライアントの初期化
    api_key = os.getenv('OPENAI_API_KEY')
    client = None
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"[WARNING] OpenAI APIクライアントの初期化に失敗しました: {e}")
    
    # 施設名正規化のキャッシュ
    facility_cache = {}
    
    # 沖縄県内施設のセットを作成
    okinawa_facilities_set = set()
    for facility in OKINAWA_FACILITIES_RAW:
        normalized = normalize_facility_name(facility, client=client, cache=facility_cache)
        if normalized:
            okinawa_facilities_set.add(normalized)
    
    # 各期ごとに処理
    periods_data = []
    all_statistics = []
    
    for ki_num in range(47, 60):
        df_ki = df_filtered[df_filtered['期番号'] == ki_num].copy()
        
        if len(df_ki) == 0:
            continue
        
        # 正規化された名前でグループ化し、各人の最終年データを取得
        final_records = []
        
        for normalized_name, group in df_ki.groupby('名前_正規化'):
            if not normalized_name:
                continue
            
            end_records = group[group['進路'].isin(end_statuses)]
            
            if len(end_records) > 0:
                final_record = end_records.loc[end_records['年度'].idxmax()]
            else:
                final_record = group.loc[group['年度'].idxmax()]
            
            final_records.append(final_record)
        
        # DataFrameに変換
        df_final = pd.DataFrame(final_records)
        
        # ふりがなでソート
        if 'ふりがな' in df_final.columns:
            df_final['ソートキー'] = df_final['ふりがな'].fillna(df_final['名前'])
            df_final = df_final.sort_values('ソートキー')
            df_final = df_final.drop(columns=['ソートキー'])
        else:
            df_final = df_final.sort_values('名前')
        
        # 不要な列を削除
        cols_to_drop = ['期番号', '名前_正規化']
        df_final = df_final.drop(columns=[col for col in cols_to_drop if col in df_final.columns])
        
        # 集計を実行
        statistics = calculate_statistics(df_final, facility_cache, okinawa_facilities_set, client=client)
        statistics['期'] = ki_num
        
        # 各カテゴリの名前リストを取得
        names_by_category = get_names_by_category(df_final, facility_cache, okinawa_facilities_set, client=client)
        
        # データを辞書形式に変換
        display_headers = ['年度', '学年', ki_column, 'PHS', '名前', 'ふりがな', '性別',
                           '専門科', '進路', '動向調査', '本籍', '出身大学', '備考']
        
        period_data = []
        for _, row in df_final.iterrows():
            row_dict = {}
            for header in display_headers:
                col_name = ki_column if header == '初・後' else header
                if col_name in row.index:
                    value = row[col_name]
                    row_dict[header] = value if pd.notna(value) else ''
                else:
                    row_dict[header] = ''
            period_data.append(row_dict)
        
        periods_data.append({
            'period': ki_num,
            'data': period_data,
            'statistics': statistics,
            'names_by_category': names_by_category
        })
        
        all_statistics.append(statistics)
    
    return {
        'periods': periods_data,
        'summary_statistics': all_statistics
    }
