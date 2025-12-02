"""
Streamlit ダッシュボード - ステップ2（機能追加版）
経費管理データ可視化ダッシュボード
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# ページ設定
st.set_page_config(
    page_title="経費管理データダッシュボード",
    page_icon="💰",
    layout="wide"
)

# データの読み込みと前処理
@st.cache_data
def load_data():
    """CSVファイルを読み込んで前処理する"""
    # ファイルのパスを取得（app.pyからの相対パス）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "Logistic.csv")
    
    try:
        # 1行目からカテゴリ名を取得
        with open(data_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # カテゴリ列の位置を特定（カンマ区切りで分割）
            category_names = [cat.strip() for cat in first_line.split(',') if cat.strip()]
        
        # CSVファイルを読み込む（最初の2行をスキップしてヘッダーを正しく読み込む）
        df = pd.read_csv(data_path, skiprows=1)
        
        # カテゴリ列の名前を設定（Unnamed列にカテゴリ名を割り当て）
        category_columns = ['Travel', 'Per Diem', 'Bks/Jrnls/AV', 'EQUIP', 'Other', 'Commun.', 'Supplies/Misc', 'Short-term consultants']
        unnamed_cols = [col for col in df.columns if 'Unnamed' in col]
        
        # カテゴリ列をマッピング（Unnamed列のインデックスに対応）
        # 実際のCSVでは、カテゴリ列は8列目以降にある
        for i, cat_col in enumerate(category_columns):
            if i < len(unnamed_cols):
                df.rename(columns={unnamed_cols[i]: cat_col}, inplace=True)
        
        # 空行や合計行を削除
        # Date列が空でない行のみを保持
        df = df[df['Date'].notna()]
        
        # Vendor列が空でない行のみを保持（実際のデータ行）
        df = df[df['Vendor'].notna()]
        
        # EXP列を数値型に変換
        df['EXP'] = pd.to_numeric(df['EXP'], errors='coerce')
        
        # EXP列が有効な数値の行のみを保持
        df = df[df['EXP'].notna()]
        df = df[df['EXP'] > 0]  # 0より大きい値のみ
        
        # 日付列を日付型に変換
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y', errors='coerce')
        df['E&E Date'] = pd.to_datetime(df['E&E Date'], format='%m/%d/%y', errors='coerce')
        
        # カテゴリ列を数値型に変換
        for col in category_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # カテゴリを特定する関数
        def determine_category(row):
            """行のカテゴリを特定する"""
            # まず、カテゴリ列に値が入っているか確認
            for col in category_columns:
                if col in df.columns:
                    if pd.notna(row.get(col, 0)) and row.get(col, 0) != 0:
                        return col
            
            # カテゴリが特定できない場合は、Descriptionから推測
            desc = str(row.get('Description', '')).lower()
            if 'airfare' in desc or 'travel' in desc:
                return 'Travel'
            elif 'lodging' in desc or 'm&ie' in desc or 'per diem' in desc.lower():
                return 'Per Diem'
            elif 'book' in desc or 'journal' in desc or 'subscription' in desc:
                return 'Bks/Jrnls/AV'
            elif 'equipment' in desc or 'equip' in desc.lower():
                return 'EQUIP'
            elif 'communication' in desc or 'hotspot' in desc or 'wire' in desc:
                return 'Commun.'
            elif 'postage' in desc or 'supply' in desc.lower():
                return 'Supplies/Misc'
            elif 'consultant' in desc.lower():
                return 'Short-term consultants'
            else:
                return 'Other'
        
        # カテゴリ列を追加
        df['Category'] = df.apply(determine_category, axis=1)
        
        # 不要な列を削除（空の列や不要な列）
        columns_to_keep = ['Date', 'Vendor', 'Description', 'O/S', 'EXP', 'E&E Date', 'Faculty', 'Official', 'Category']
        df = df[[col for col in columns_to_keep if col in df.columns]]
        
        # 日付が有効な行のみを保持
        df = df[df['Date'].notna()]
        
        # Vendor列の空白を処理
        df['Vendor'] = df['Vendor'].fillna('Unknown')
        
        # Description列の空白を処理
        df['Description'] = df['Description'].fillna('')
        
        return df
    
    except FileNotFoundError:
        st.error(f"データファイルが見つかりません: {data_path}")
        st.info(f"現在のディレクトリ: {os.getcwd()}")
        st.info(f"ファイルの場所: {current_dir}")
        st.info(f"データファイルのパス: {data_path}")
        return None
    except Exception as e:
        st.error(f"データの読み込み中にエラーが発生しました: {str(e)}")
        st.info(f"エラーの詳細: {type(e).__name__}")
        import traceback
        st.code(traceback.format_exc())
        return None

# データ読み込み
df = load_data()

if df is not None and len(df) > 0:
    # サイドバー - フィルター設定
    st.sidebar.header("📋 フィルター設定")
    
    # 期間フィルター
    st.sidebar.subheader("期間")
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "日付の期間を選択",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # カテゴリフィルター
    st.sidebar.subheader("カテゴリ")
    categories = st.sidebar.multiselect(
        "カテゴリを選択",
        options=sorted(df['Category'].unique()),
        default=sorted(df['Category'].unique()),
        label_visibility="collapsed"
    )
    
    # ベンダーフィルター
    st.sidebar.subheader("ベンダー")
    vendors = st.sidebar.multiselect(
        "ベンダーを選択",
        options=sorted(df['Vendor'].unique()),
        default=sorted(df['Vendor'].unique()),
        label_visibility="collapsed"
    )
    
    # 支出金額フィルター
    st.sidebar.subheader("支出金額")
    amount_min = float(df['EXP'].min())
    amount_max = float(df['EXP'].max())
    amount_range = st.sidebar.slider(
        "支出金額の範囲（$）",
        min_value=amount_min,
        max_value=amount_max,
        value=(amount_min, amount_max),
        step=100.0,
        label_visibility="collapsed"
    )
    
    # データフィルタリング
    filtered_df = df.copy()
    
    # 期間フィルター
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered_df = filtered_df[
            (filtered_df['Date'] >= start_date) & 
            (filtered_df['Date'] <= end_date)
        ]
    
    if len(categories) > 0:
        filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
    if len(vendors) > 0:
        filtered_df = filtered_df[filtered_df['Vendor'].isin(vendors)]
    
    # 支出金額フィルター
    filtered_df = filtered_df[
        (filtered_df['EXP'] >= amount_range[0]) & 
        (filtered_df['EXP'] <= amount_range[1])
    ]
    
    # メインコンテンツ
    if len(filtered_df) > 0:
        # YearMonth列を一度だけ追加（全タブで使用）
        filtered_df = filtered_df.copy()
        filtered_df['YearMonth'] = filtered_df['Date'].dt.to_period('M').astype(str)
        
        # タブ作成
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 概要ダッシュボード",
            "📅 時系列分析",
            "📁 カテゴリ分析",
            "🏢 ベンダー分析",
            "🔍 詳細データ探索"
        ])
        
        # ========== タブ1: 概要ダッシュボード ==========
        with tab1:
            st.title("📊 経費管理データ 概要ダッシュボード")
            st.markdown("---")
            
            # 主要KPI指標（8列）
            st.subheader("主要指標")
            col1, col2, col3, col4 = st.columns(4)
            col5, col6, col7, col8 = st.columns(4)
            
            total_expense = filtered_df['EXP'].sum()
            avg_monthly_expense = filtered_df.groupby(filtered_df['Date'].dt.to_period('M'))['EXP'].sum().mean()
            total_transactions = len(filtered_df)
            avg_transaction = filtered_df['EXP'].mean()
            max_expense = filtered_df['EXP'].max()
            min_expense = filtered_df['EXP'].min()
            num_categories = len(filtered_df['Category'].unique())
            num_vendors = len(filtered_df['Vendor'].unique())
            
            with col1:
                st.metric("総支出額", f"${total_expense:,.2f}")
            
            with col2:
                st.metric("平均月間支出", f"${avg_monthly_expense:,.2f}")
            
            with col3:
                st.metric("総取引件数", f"{total_transactions:,}件")
            
            with col4:
                st.metric("平均取引額", f"${avg_transaction:,.2f}")
            
            with col5:
                st.metric("最大支出額", f"${max_expense:,.2f}")
            
            with col6:
                st.metric("最小支出額", f"${min_expense:,.2f}")
            
            with col7:
                st.metric("支出カテゴリ数", f"{num_categories:,}種類")
            
            with col8:
                st.metric("ベンダー数", f"{num_vendors:,}社")
            
            st.markdown("---")
            
            # トレンド表示（2列）
            st.subheader("トレンド分析")
            
            # 月別集計
            monthly_expense = filtered_df.groupby('YearMonth')['EXP'].sum().reset_index()
            monthly_expense.columns = ['年月', '支出額']
            
            monthly_count = filtered_df.groupby('YearMonth').size().reset_index()
            monthly_count.columns = ['年月', '取引件数']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_expense = px.line(
                    monthly_expense,
                    x='年月',
                    y='支出額',
                    title="月別支出推移",
                    markers=True,
                    labels={'支出額': '支出額（$）', '年月': '年月'}
                )
                fig_expense.update_xaxes(tickangle=45)
                st.plotly_chart(fig_expense, use_container_width=True)
            
            with col2:
                fig_count = px.bar(
                    monthly_count,
                    x='年月',
                    y='取引件数',
                    title="月別取引件数推移",
                    labels={'取引件数': '取引件数（件）', '年月': '年月'}
                )
                fig_count.update_xaxes(tickangle=45)
                st.plotly_chart(fig_count, use_container_width=True)
            
            st.markdown("---")
            
            # 主要インサイト（3列）
            st.subheader("主要インサイト")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category_expense = filtered_df.groupby('Category')['EXP'].sum().reset_index()
                category_expense = category_expense.sort_values('EXP', ascending=False)
                fig_category = px.pie(
                    category_expense,
                    values='EXP',
                    names='Category',
                    title="カテゴリ別支出シェア"
                )
                st.plotly_chart(fig_category, use_container_width=True)
            
            with col2:
                vendor_expense = filtered_df.groupby('Vendor')['EXP'].sum().reset_index()
                vendor_expense = vendor_expense.sort_values('EXP', ascending=False).head(10)
                fig_vendor = px.bar(
                    vendor_expense,
                    x='EXP',
                    y='Vendor',
                    orientation='h',
                    title="トップベンダー別支出（上位10社）",
                    labels={'EXP': '支出額（$）', 'Vendor': 'ベンダー'}
                )
                st.plotly_chart(fig_vendor, use_container_width=True)
            
            with col3:
                monthly_expense_bar = filtered_df.groupby('YearMonth')['EXP'].sum().reset_index()
                monthly_expense_bar.columns = ['年月', '支出額']
                fig_monthly = px.bar(
                    monthly_expense_bar,
                    x='年月',
                    y='支出額',
                    title="月別支出比較",
                    labels={'支出額': '支出額（$）', '年月': '年月'}
                )
                fig_monthly.update_xaxes(tickangle=45)
                st.plotly_chart(fig_monthly, use_container_width=True)
        
        # ========== タブ2: 時系列分析 ==========
        with tab2:
            st.title("📅 時系列分析")
            st.markdown("---")
            
            # 月別トレンド
            st.subheader("月別トレンド")
            
            monthly_trend = filtered_df.groupby('YearMonth').agg({
                'EXP': ['sum', 'mean', 'count']
            }).reset_index()
            monthly_trend.columns = ['年月', '総支出', '平均取引額', '取引件数']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig_sales_trend = px.line(
                    monthly_trend,
                    x='年月',
                    y='総支出',
                    title="月別総支出推移",
                    markers=True,
                    labels={'総支出': '支出額（$）', '年月': '年月'}
                )
                fig_sales_trend.update_xaxes(tickangle=45)
                st.plotly_chart(fig_sales_trend, use_container_width=True)
            
            with col2:
                fig_count_trend = px.line(
                    monthly_trend,
                    x='年月',
                    y='取引件数',
                    title="月別取引件数推移",
                    markers=True,
                    labels={'取引件数': '取引件数（件）', '年月': '年月'}
                )
                fig_count_trend.update_xaxes(tickangle=45)
                st.plotly_chart(fig_count_trend, use_container_width=True)
            
            with col3:
                fig_avg_trend = px.line(
                    monthly_trend,
                    x='年月',
                    y='平均取引額',
                    title="月別平均取引額推移",
                    markers=True,
                    labels={'平均取引額': '平均取引額（$）', '年月': '年月'}
                )
                fig_avg_trend.update_xaxes(tickangle=45)
                st.plotly_chart(fig_avg_trend, use_container_width=True)
            
            st.markdown("---")
            
            # 累積支出推移
            st.subheader("累積支出推移")
            monthly_trend_sorted = monthly_trend.sort_values('年月')
            monthly_trend_sorted['累積支出'] = monthly_trend_sorted['総支出'].cumsum()
            
            fig_cumulative = px.area(
                monthly_trend_sorted,
                x='年月',
                y='累積支出',
                title="累積支出推移",
                labels={'累積支出': '累積支出額（$）', '年月': '年月'}
            )
            fig_cumulative.update_xaxes(tickangle=45)
            st.plotly_chart(fig_cumulative, use_container_width=True)
            
            st.markdown("---")
            
            # 年別比較
            st.subheader("年別比較")
            
            filtered_df['年'] = filtered_df['Date'].dt.year
            filtered_df['月'] = filtered_df['Date'].dt.month
            
            yearly_comparison = filtered_df.groupby(['年', '月'])['EXP'].sum().reset_index()
            
            fig_yearly = px.line(
                yearly_comparison,
                x='月',
                y='EXP',
                color='年',
                title="2024年 vs 2025年 月別比較",
                markers=True,
                labels={'EXP': '支出額（$）', '月': '月', '年': '年'}
            )
            st.plotly_chart(fig_yearly, use_container_width=True)
        
        # ========== タブ3: カテゴリ分析 ==========
        with tab3:
            st.title("📁 カテゴリ分析")
            st.markdown("---")
            
            # カテゴリ別概要
            st.subheader("カテゴリ別概要")
            
            category_stats = filtered_df.groupby('Category').agg({
                'EXP': ['sum', 'mean', 'count']
            }).reset_index()
            category_stats.columns = ['カテゴリ', '総支出額', '平均取引額', '取引件数']
            
            total_expense_all = filtered_df['EXP'].sum()
            category_stats['支出シェア'] = (category_stats['総支出額'] / total_expense_all * 100).round(2)
            
            # カテゴリ別詳細分析
            st.subheader("カテゴリ別詳細分析")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig_cat_sales = px.bar(
                    category_stats.sort_values('総支出額', ascending=False),
                    x='総支出額',
                    y='カテゴリ',
                    orientation='h',
                    title="カテゴリ別総支出",
                    labels={'総支出額': '総支出額（$）', 'カテゴリ': 'カテゴリ'}
                )
                st.plotly_chart(fig_cat_sales, use_container_width=True)
            
            with col2:
                fig_cat_avg = px.bar(
                    category_stats.sort_values('平均取引額', ascending=False),
                    x='平均取引額',
                    y='カテゴリ',
                    orientation='h',
                    title="カテゴリ別平均取引額",
                    labels={'平均取引額': '平均取引額（$）', 'カテゴリ': 'カテゴリ'}
                )
                st.plotly_chart(fig_cat_avg, use_container_width=True)
            
            with col3:
                fig_cat_count = px.bar(
                    category_stats.sort_values('取引件数', ascending=False),
                    x='取引件数',
                    y='カテゴリ',
                    orientation='h',
                    title="カテゴリ別取引件数",
                    labels={'取引件数': '取引件数（件）', 'カテゴリ': 'カテゴリ'}
                )
                st.plotly_chart(fig_cat_count, use_container_width=True)
            
            st.markdown("---")
            
            # カテゴリ別の月別支出推移
            st.subheader("カテゴリ別の月別支出推移")
            
            category_monthly = filtered_df.groupby(['YearMonth', 'Category'])['EXP'].sum().reset_index()
            category_monthly.columns = ['年月', 'カテゴリ', '支出額']
            
            fig_category_monthly = px.line(
                category_monthly,
                x='年月',
                y='支出額',
                color='カテゴリ',
                title="カテゴリ別の月別支出推移",
                markers=True,
                labels={'支出額': '支出額（$）', '年月': '年月', 'カテゴリ': 'カテゴリ'}
            )
            fig_category_monthly.update_xaxes(tickangle=45)
            st.plotly_chart(fig_category_monthly, use_container_width=True)
        
        # ========== タブ4: ベンダー分析 ==========
        with tab4:
            st.title("🏢 ベンダー分析")
            st.markdown("---")
            
            # ベンダー別概要
            st.subheader("ベンダー別概要")
            
            vendor_stats = filtered_df.groupby('Vendor').agg({
                'EXP': ['sum', 'mean', 'count']
            }).reset_index()
            vendor_stats.columns = ['ベンダー', '総支出額', '平均取引額', '取引件数']
            
            total_expense_all = filtered_df['EXP'].sum()
            vendor_stats['支出シェア'] = (vendor_stats['総支出額'] / total_expense_all * 100).round(2)
            
            # トップベンダー分析
            st.subheader("トップベンダー分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_vendor_sales = px.bar(
                    vendor_stats.nlargest(10, '総支出額'),
                    x='総支出額',
                    y='ベンダー',
                    orientation='h',
                    title="支出額上位10ベンダー",
                    labels={'総支出額': '総支出額（$）', 'ベンダー': 'ベンダー'}
                )
                st.plotly_chart(fig_vendor_sales, use_container_width=True)
            
            with col2:
                fig_vendor_count = px.bar(
                    vendor_stats.nlargest(10, '取引件数'),
                    x='取引件数',
                    y='ベンダー',
                    orientation='h',
                    title="取引件数上位10ベンダー",
                    labels={'取引件数': '取引件数（件）', 'ベンダー': 'ベンダー'}
                )
                st.plotly_chart(fig_vendor_count, use_container_width=True)
            
            st.markdown("---")
            
            # 主要ベンダーの月別支出推移
            st.subheader("主要ベンダーの月別支出推移")
            
            top_vendor_names = vendor_stats.nlargest(5, '総支出額')['ベンダー'].tolist()
            vendor_monthly = filtered_df[filtered_df['Vendor'].isin(top_vendor_names)].groupby(['YearMonth', 'Vendor'])['EXP'].sum().reset_index()
            vendor_monthly.columns = ['年月', 'ベンダー', '支出額']
            
            fig_vendor_monthly = px.line(
                vendor_monthly,
                x='年月',
                y='支出額',
                color='ベンダー',
                title="主要ベンダーの月別支出推移（上位5社）",
                markers=True,
                labels={'支出額': '支出額（$）', '年月': '年月', 'ベンダー': 'ベンダー'}
            )
            fig_vendor_monthly.update_xaxes(tickangle=45)
            st.plotly_chart(fig_vendor_monthly, use_container_width=True)
        
        # ========== タブ5: 詳細データ探索 ==========
        with tab5:
            st.title("🔍 詳細データ探索")
            st.markdown("---")
            
            # 検索機能
            st.subheader("検索")
            col_search1, col_search2 = st.columns(2)
            
            with col_search1:
                vendor_search = st.text_input("ベンダー名で検索（空欄の場合は全件表示）")
            
            with col_search2:
                description_search = st.text_input("説明文で検索（空欄の場合は全件表示）")
            
            # 検索フィルター適用
            search_df = filtered_df.copy()
            if vendor_search:
                search_df = search_df[search_df['Vendor'].str.contains(vendor_search, case=False, na=False)]
            if description_search:
                search_df = search_df[search_df['Description'].str.contains(description_search, case=False, na=False)]
            
            st.markdown("---")
            
            # ソート機能（複数カラム）
            st.subheader("ソート設定")
            col_sort1, col_sort2 = st.columns(2)
            
            with col_sort1:
                sort_column1 = st.selectbox(
                    "第1ソートカラム",
                    options=['Date', 'EXP', 'Vendor', 'Category', 'Description'],
                    index=0
                )
                sort_ascending1 = st.checkbox("第1ソート: 昇順", value=True)
            
            with col_sort2:
                sort_column2 = st.selectbox(
                    "第2ソートカラム",
                    options=['なし', 'Date', 'EXP', 'Vendor', 'Category', 'Description'],
                    index=0
                )
                sort_ascending2 = st.checkbox("第2ソート: 昇順", value=True) if sort_column2 != 'なし' else True
            
            # ソート適用
            if sort_column2 != 'なし' and sort_column1 != sort_column2:
                sorted_df = search_df.sort_values(
                    by=[sort_column1, sort_column2],
                    ascending=[sort_ascending1, sort_ascending2]
                )
            else:
                sorted_df = search_df.sort_values(
                    by=sort_column1,
                    ascending=sort_ascending1
                )
            
            st.markdown("---")
            
            # データテーブル表示
            display_columns = ['Date', 'Vendor', 'Description', 'Category', 'EXP', 'E&E Date']
            display_df = sorted_df[display_columns].copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
            display_df['E&E Date'] = display_df['E&E Date'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            
            st.markdown("---")
            
            # CSVダウンロード
            st.subheader("データエクスポート")
            csv = sorted_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 フィルター済みデータをCSVでダウンロード",
                data=csv,
                file_name="filtered_expense_data.csv",
                mime="text/csv"
            )
            
            # データサマリー
            st.markdown("---")
            st.subheader("データサマリー")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**表示中のレコード数**: {len(sorted_df):,}件")
                st.write(f"**表示中のベンダー数**: {len(sorted_df['Vendor'].unique()):,}社")
                st.write(f"**表示中のカテゴリ数**: {len(sorted_df['Category'].unique()):,}種類")
            
            with col2:
                if len(sorted_df) > 0:
                    st.write(f"**期間**: {sorted_df['Date'].min().strftime('%Y-%m-%d')} ～ {sorted_df['Date'].max().strftime('%Y-%m-%d')}")
                    st.write(f"**合計金額**: ${sorted_df['EXP'].sum():,.2f}")
                    st.write(f"**平均金額**: ${sorted_df['EXP'].mean():,.2f}")
    
    else:
        st.warning("フィルター条件に一致するデータがありません。フィルター設定を変更してください。")

else:
    st.info("データファイルを配置して、アプリを再読み込みしてください。")

