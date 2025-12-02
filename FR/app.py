"""
Streamlit ダッシュボード - ステップ3（完全版）
経費管理データ可視化ダッシュボード
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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
    
    # 期間のプリセット
    from datetime import date, timedelta
    today = date.today()
    
    # プリセットの計算
    from calendar import monthrange
    
    if today.month == 1:
        this_month_start = date(today.year, 1, 1)
        last_month_start = date(today.year - 1, 12, 1)
        last_month_end = date(today.year - 1, 12, 31)
    else:
        this_month_start = date(today.year, today.month, 1)
        last_month_start = date(today.year, today.month - 1, 1)
        # 前月の最終日を正確に計算
        _, last_day = monthrange(today.year, today.month - 1)
        last_month_end = date(today.year, today.month - 1, last_day)
    
    # 四半期の計算
    current_quarter = (today.month - 1) // 3 + 1
    quarter_start_month = (current_quarter - 1) * 3 + 1
    quarter_start = date(today.year, quarter_start_month, 1)
    
    # 年間の計算
    year_start = date(today.year, 1, 1)
    
    preset_options = {
        "全期間": (min_date, max_date),
        "今月": (max(this_month_start, min_date), min(today, max_date)),
        "先月": (max(last_month_start, min_date), min(last_month_end, max_date)),
        "四半期": (max(quarter_start, min_date), min(today, max_date)),
        "年間": (max(year_start, min_date), min(today, max_date))
    }
    
    selected_preset = st.sidebar.selectbox(
        "期間プリセット",
        options=list(preset_options.keys()),
        index=0
    )
    
    preset_start, preset_end = preset_options[selected_preset]
    date_range = st.sidebar.date_input(
        "日付の期間を選択",
        value=(preset_start, preset_end),
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
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📊 概要ダッシュボード",
            "📅 時系列分析",
            "📁 カテゴリ分析",
            "🏢 ベンダー分析",
            "💰 支出分析",
            "📆 月別比較分析",
            "🔗 カテゴリ×ベンダー分析",
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
            
            st.markdown("---")
            
            # 四半期別トレンド
            st.subheader("四半期別トレンド")
            
            filtered_df['四半期'] = filtered_df['Date'].dt.to_period('Q').astype(str)
            quarterly_trend = filtered_df.groupby('四半期').agg({
                'EXP': ['sum', 'count']
            }).reset_index()
            quarterly_trend.columns = ['四半期', '総支出', '取引件数']
            quarterly_trend = quarterly_trend.sort_values('四半期')
            
            # 成長率を計算
            quarterly_trend['成長率'] = quarterly_trend['総支出'].pct_change() * 100
            quarterly_trend['成長率'] = quarterly_trend['成長率'].fillna(0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_quarterly = px.bar(
                    quarterly_trend,
                    x='四半期',
                    y='総支出',
                    title="四半期別総支出",
                    labels={'総支出': '総支出（$）', '四半期': '四半期'}
                )
                fig_quarterly.update_xaxes(tickangle=45)
                st.plotly_chart(fig_quarterly, use_container_width=True)
            
            with col2:
                fig_growth = px.line(
                    quarterly_trend,
                    x='四半期',
                    y='成長率',
                    title="四半期別成長率",
                    markers=True,
                    labels={'成長率': '成長率（%）', '四半期': '四半期'}
                )
                fig_growth.add_hline(y=0, line_dash="dash", line_color="gray")
                fig_growth.update_xaxes(tickangle=45)
                st.plotly_chart(fig_growth, use_container_width=True)
            
            st.markdown("---")
            
            # 季節性分析
            st.subheader("季節性分析")
            
            filtered_df['月'] = filtered_df['Date'].dt.month
            monthly_avg = filtered_df.groupby('月')['EXP'].mean().reset_index()
            monthly_avg.columns = ['月', '平均支出']
            monthly_avg['月名'] = monthly_avg['月'].apply(lambda x: f"{x}月")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_seasonal = px.bar(
                    monthly_avg,
                    x='月名',
                    y='平均支出',
                    title="月別支出の平均値（季節性の可視化）",
                    labels={'平均支出': '平均支出（$）', '月名': '月'}
                )
                st.plotly_chart(fig_seasonal, use_container_width=True)
            
            with col2:
                # 曜日別分析
                filtered_df['曜日'] = filtered_df['Date'].dt.day_name()
                weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_jp = {'Monday': '月', 'Tuesday': '火', 'Wednesday': '水', 'Thursday': '木', 'Friday': '金', 'Saturday': '土', 'Sunday': '日'}
                filtered_df['曜日JP'] = filtered_df['曜日'].map(weekday_jp)
                
                weekday_expense = filtered_df.groupby('曜日JP')['EXP'].sum().reset_index()
                weekday_expense.columns = ['曜日', '支出額']
                weekday_order_jp = ['月', '火', '水', '木', '金', '土', '日']
                weekday_expense['曜日'] = pd.Categorical(weekday_expense['曜日'], categories=weekday_order_jp, ordered=True)
                weekday_expense = weekday_expense.sort_values('曜日')
                
                fig_weekday = px.bar(
                    weekday_expense,
                    x='曜日',
                    y='支出額',
                    title="曜日別支出",
                    labels={'支出額': '支出額（$）', '曜日': '曜日'}
                )
                st.plotly_chart(fig_weekday, use_container_width=True)
            
            st.markdown("---")
            
            # カテゴリ別の累積支出推移
            st.subheader("カテゴリ別の累積支出推移")
            
            category_cumulative = filtered_df.groupby(['YearMonth', 'Category'])['EXP'].sum().reset_index()
            category_cumulative.columns = ['年月', 'カテゴリ', '支出額']
            category_cumulative = category_cumulative.sort_values('年月')
            
            # 各カテゴリの累積値を計算
            category_cumulative['累積支出'] = category_cumulative.groupby('カテゴリ')['支出額'].cumsum()
            
            fig_category_cumulative = px.area(
                category_cumulative,
                x='年月',
                y='累積支出',
                color='カテゴリ',
                title="カテゴリ別の累積支出推移（積み上げエリアチャート）",
                labels={'累積支出': '累積支出額（$）', '年月': '年月', 'カテゴリ': 'カテゴリ'}
            )
            fig_category_cumulative.update_xaxes(tickangle=45)
            st.plotly_chart(fig_category_cumulative, use_container_width=True)
        
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
            
            st.markdown("---")
            
            # カテゴリ別の支出分布（箱ひげ図）
            st.subheader("カテゴリ別の支出分布")
            
            fig_box = px.box(
                filtered_df,
                x='Category',
                y='EXP',
                title="カテゴリ別の支出分布（箱ひげ図）",
                labels={'EXP': '支出額（$）', 'Category': 'カテゴリ'}
            )
            fig_box.update_xaxes(tickangle=45)
            st.plotly_chart(fig_box, use_container_width=True)
            
            st.markdown("---")
            
            # カテゴリ×月別の支出（ヒートマップ）
            st.subheader("カテゴリ×月別の支出（ヒートマップ）")
            
            category_monthly_pivot = category_monthly.pivot(index='カテゴリ', columns='年月', values='支出額').fillna(0)
            
            fig_cat_month_heatmap = go.Figure(data=go.Heatmap(
                z=category_monthly_pivot.values,
                x=category_monthly_pivot.columns,
                y=category_monthly_pivot.index,
                colorscale='YlGnBu',
                text=category_monthly_pivot.values,
                texttemplate='%{text:.0f}',
                textfont={"size": 10}
            ))
            
            fig_cat_month_heatmap.update_layout(
                title="カテゴリ×月別の支出（ヒートマップ）",
                xaxis_title="年月",
                yaxis_title="カテゴリ"
            )
            
            st.plotly_chart(fig_cat_month_heatmap, use_container_width=True)
        
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
            
            st.markdown("---")
            
            # ベンダー×カテゴリ分析
            st.subheader("ベンダー×カテゴリ分析")
            
            vendor_category_expense = filtered_df.groupby(['Vendor', 'Category'])['EXP'].sum().reset_index()
            vendor_category_expense.columns = ['ベンダー', 'カテゴリ', '総支出']
            
            # 主要ベンダーのみに絞る
            top_vendors_for_heatmap = vendor_stats.nlargest(10, '総支出額')['ベンダー'].tolist()
            vendor_category_filtered = vendor_category_expense[vendor_category_expense['ベンダー'].isin(top_vendors_for_heatmap)]
            
            vc_expense_pivot = vendor_category_filtered.pivot(index='ベンダー', columns='カテゴリ', values='総支出').fillna(0)
            
            fig_vc_heatmap = go.Figure(data=go.Heatmap(
                z=vc_expense_pivot.values,
                x=vc_expense_pivot.columns,
                y=vc_expense_pivot.index,
                colorscale='Reds',
                text=vc_expense_pivot.values,
                texttemplate='%{text:.0f}',
                textfont={"size": 8}
            ))
            
            fig_vc_heatmap.update_layout(
                title="ベンダー×カテゴリ別の支出（ヒートマップ）",
                xaxis_title="カテゴリ",
                yaxis_title="ベンダー",
                height=500
            )
            
            st.plotly_chart(fig_vc_heatmap, use_container_width=True)
            
            st.markdown("---")
            
            # 主要ベンダーのカテゴリ内訳（積み上げ棒グラフ）
            st.subheader("主要ベンダーのカテゴリ内訳")
            
            top_vendors_stack = vendor_stats.nlargest(5, '総支出額')['ベンダー'].tolist()
            vendor_category_stack = filtered_df[filtered_df['Vendor'].isin(top_vendors_stack)].groupby(['Vendor', 'Category'])['EXP'].sum().reset_index()
            vendor_category_stack.columns = ['ベンダー', 'カテゴリ', '支出額']
            
            fig_vendor_cat_stack = px.bar(
                vendor_category_stack,
                x='ベンダー',
                y='支出額',
                color='カテゴリ',
                title="主要ベンダーのカテゴリ内訳（積み上げ棒グラフ）",
                labels={'支出額': '支出額（$）', 'ベンダー': 'ベンダー', 'カテゴリ': 'カテゴリ'}
            )
            fig_vendor_cat_stack.update_xaxes(tickangle=45)
            st.plotly_chart(fig_vendor_cat_stack, use_container_width=True)
        
        # ========== タブ5: 支出分析 ==========
        with tab5:
            st.title("💰 支出分析")
            st.markdown("---")
            
            # 支出概要
            st.subheader("支出概要")
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            total_expense_amount = filtered_df['EXP'].sum()
            avg_unit_price = filtered_df['EXP'].mean()
            max_amount = filtered_df['EXP'].max()
            min_amount = filtered_df['EXP'].min()
            median_amount = filtered_df['EXP'].median()
            std_amount = filtered_df['EXP'].std()
            
            with col1:
                st.metric("総支出高", f"${total_expense_amount:,.2f}")
            
            with col2:
                st.metric("平均取引額", f"${avg_unit_price:,.2f}")
            
            with col3:
                st.metric("最大取引額", f"${max_amount:,.2f}")
            
            with col4:
                st.metric("最小取引額", f"${min_amount:,.2f}")
            
            with col5:
                st.metric("中央値取引額", f"${median_amount:,.2f}")
            
            with col6:
                st.metric("標準偏差", f"${std_amount:,.2f}")
            
            st.markdown("---")
            
            # 支出分布
            st.subheader("支出分布")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hist = px.histogram(
                    filtered_df,
                    x='EXP',
                    nbins=30,
                    title="取引金額の分布",
                    labels={'EXP': '取引金額（$）', 'count': '件数'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # 累積分布
                sorted_expenses = filtered_df['EXP'].sort_values()
                cumulative_pct = (sorted_expenses.cumsum() / sorted_expenses.sum() * 100).reset_index(drop=True)
                cumulative_df = pd.DataFrame({
                    '取引金額': sorted_expenses.values,
                    '累積割合': cumulative_pct.values
                })
                
                fig_cumulative = px.line(
                    cumulative_df,
                    x='取引金額',
                    y='累積割合',
                    title="取引金額の累積分布",
                    labels={'取引金額': '取引金額（$）', '累積割合': '累積割合（%）'}
                )
                st.plotly_chart(fig_cumulative, use_container_width=True)
            
            st.markdown("---")
            
            # 金額帯別分析
            st.subheader("金額帯別分析")
            
            # 金額帯の定義
            def categorize_amount(amount):
                if amount < 500:
                    return "0-500"
                elif amount < 1000:
                    return "500-1,000"
                elif amount < 5000:
                    return "1,000-5,000"
                elif amount < 10000:
                    return "5,000-10,000"
                elif amount < 50000:
                    return "10,000-50,000"
                else:
                    return "50,000以上"
            
            filtered_df_copy = filtered_df.copy()
            filtered_df_copy['金額帯'] = filtered_df_copy['EXP'].apply(categorize_amount)
            
            amount_range_stats = filtered_df_copy.groupby('金額帯').agg({
                'EXP': ['sum', 'count', 'mean']
            }).reset_index()
            amount_range_stats.columns = ['金額帯', '総支出額', '取引件数', '平均取引額']
            amount_range_order = ["0-500", "500-1,000", "1,000-5,000", "5,000-10,000", "10,000-50,000", "50,000以上"]
            amount_range_stats['金額帯'] = pd.Categorical(amount_range_stats['金額帯'], categories=amount_range_order, ordered=True)
            amount_range_stats = amount_range_stats.sort_values('金額帯')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig_amount_count = px.bar(
                    amount_range_stats,
                    x='金額帯',
                    y='取引件数',
                    title="金額帯別の取引件数",
                    labels={'取引件数': '取引件数（件）', '金額帯': '金額帯（$）'}
                )
                fig_amount_count.update_xaxes(tickangle=45)
                st.plotly_chart(fig_amount_count, use_container_width=True)
            
            with col2:
                fig_amount_sum = px.bar(
                    amount_range_stats,
                    x='金額帯',
                    y='総支出額',
                    title="金額帯別の総支出額",
                    labels={'総支出額': '総支出額（$）', '金額帯': '金額帯（$）'}
                )
                fig_amount_sum.update_xaxes(tickangle=45)
                st.plotly_chart(fig_amount_sum, use_container_width=True)
            
            with col3:
                fig_amount_avg = px.bar(
                    amount_range_stats,
                    x='金額帯',
                    y='平均取引額',
                    title="金額帯別の平均取引額",
                    labels={'平均取引額': '平均取引額（$）', '金額帯': '金額帯（$）'}
                )
                fig_amount_avg.update_xaxes(tickangle=45)
                st.plotly_chart(fig_amount_avg, use_container_width=True)
            
            st.markdown("---")
            
            # 高額取引分析
            st.subheader("高額取引分析")
            
            top_expenses = filtered_df.nlargest(10, 'EXP')[['Date', 'Vendor', 'Description', 'Category', 'EXP']].copy()
            top_expenses['Date'] = top_expenses['Date'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                top_expenses,
                use_container_width=True,
                height=300
            )
            
            st.markdown("---")
            
            # 支出パターン分析
            st.subheader("支出パターン分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # パレート分析
                sorted_expenses_desc = filtered_df['EXP'].sort_values(ascending=False)
                top_20_pct_count = int(len(sorted_expenses_desc) * 0.2)
                top_20_pct_amount = sorted_expenses_desc.head(top_20_pct_count).sum()
                total_amount = sorted_expenses_desc.sum()
                pareto_ratio = (top_20_pct_amount / total_amount * 100) if total_amount > 0 else 0
                
                st.metric("パレート分析", f"上位20%の取引が{pareto_ratio:.1f}%の支出を占める")
                
                # パレートチャート
                cumulative_pct_expenses = (sorted_expenses_desc.cumsum() / sorted_expenses_desc.sum() * 100).reset_index(drop=True)
                pareto_df = pd.DataFrame({
                    '取引順位': range(1, len(sorted_expenses_desc) + 1),
                    '累積支出割合': cumulative_pct_expenses.values,
                    '取引金額': sorted_expenses_desc.values
                })
                
                fig_pareto = px.line(
                    pareto_df,
                    x='取引順位',
                    y='累積支出割合',
                    title="パレート分析（累積支出割合）",
                    labels={'累積支出割合': '累積支出割合（%）', '取引順位': '取引順位'}
                )
                st.plotly_chart(fig_pareto, use_container_width=True)
            
            with col2:
                # ローレンツ曲線
                n = len(sorted_expenses_desc)
                cumulative_pct_transactions = (np.arange(1, n + 1) / n * 100)
                cumulative_pct_expenses_lorenz = (sorted_expenses_desc.cumsum() / sorted_expenses_desc.sum() * 100).reset_index(drop=True)
                
                lorenz_df = pd.DataFrame({
                    '取引累積割合': cumulative_pct_transactions,
                    '支出累積割合': cumulative_pct_expenses_lorenz.values
                })
                
                # 完全平等線を追加
                equality_df = pd.DataFrame({
                    '取引累積割合': [0, 100],
                    '支出累積割合': [0, 100]
                })
                
                fig_lorenz = px.line(
                    lorenz_df,
                    x='取引累積割合',
                    y='支出累積割合',
                    title="ローレンツ曲線（支出の集中度）",
                    labels={'支出累積割合': '支出累積割合（%）', '取引累積割合': '取引累積割合（%）'}
                )
                
                # 完全平等線を追加
                fig_lorenz.add_scatter(
                    x=equality_df['取引累積割合'],
                    y=equality_df['支出累積割合'],
                    mode='lines',
                    name='完全平等線',
                    line=dict(dash='dash', color='gray')
                )
                
                st.plotly_chart(fig_lorenz, use_container_width=True)
        
        # ========== タブ6: 月別比較分析 ==========
        with tab6:
            st.title("📆 月別比較分析")
            st.markdown("---")
            
            # 月別概要
            st.subheader("月別概要")
            
            monthly_summary = filtered_df.groupby('YearMonth').agg({
                'EXP': ['sum', 'mean', 'count']
            }).reset_index()
            monthly_summary.columns = ['年月', '総支出', '平均取引額', '取引件数']
            monthly_summary = monthly_summary.sort_values('年月')
            
            # 前月比を計算
            monthly_summary['前月比'] = monthly_summary['総支出'].pct_change() * 100
            monthly_summary['前月比'] = monthly_summary['前月比'].fillna(0)
            
            # 月別KPI表示（コンパクトに）
            st.write("**月別KPI**")
            for idx, row in monthly_summary.iterrows():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(f"{row['年月']} - 総支出", f"${row['総支出']:,.2f}")
                with col2:
                    st.metric(f"{row['年月']} - 平均取引額", f"${row['平均取引額']:,.2f}")
                with col3:
                    st.metric(f"{row['年月']} - 取引件数", f"{int(row['取引件数']):,}件")
                with col4:
                    delta_color = "normal" if row['前月比'] >= 0 else "inverse"
                    st.metric(f"{row['年月']} - 前月比", f"{row['前月比']:+.1f}%", delta=f"{row['前月比']:+.1f}%")
            
            st.markdown("---")
            
            # 月別詳細分析
            st.subheader("月別詳細分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 月別総支出（前月比を色分け）
                fig_monthly_expense = px.bar(
                    monthly_summary,
                    x='年月',
                    y='総支出',
                    title="月別総支出（前月比で色分け）",
                    color=monthly_summary['前月比'],
                    color_continuous_scale='RdYlGn',
                    labels={'総支出': '総支出（$）', '年月': '年月'}
                )
                fig_monthly_expense.update_xaxes(tickangle=45)
                st.plotly_chart(fig_monthly_expense, use_container_width=True)
            
            with col2:
                # 月別の前月比推移
                fig_mom_change = px.line(
                    monthly_summary,
                    x='年月',
                    y='前月比',
                    title="月別の前月比推移",
                    markers=True,
                    labels={'前月比': '前月比（%）', '年月': '年月'}
                )
                fig_mom_change.add_hline(y=0, line_dash="dash", line_color="gray")
                fig_mom_change.update_xaxes(tickangle=45)
                st.plotly_chart(fig_mom_change, use_container_width=True)
            
            st.markdown("---")
            
            # 月別のカテゴリ構成比
            st.subheader("月別のカテゴリ構成比")
            
            category_monthly_stack = filtered_df.groupby(['YearMonth', 'Category'])['EXP'].sum().reset_index()
            category_monthly_stack.columns = ['年月', 'カテゴリ', '支出額']
            category_monthly_stack = category_monthly_stack.sort_values('年月')
            
            fig_category_stack = px.bar(
                category_monthly_stack,
                x='年月',
                y='支出額',
                color='カテゴリ',
                title="月別のカテゴリ構成比（積み上げ）",
                labels={'支出額': '支出額（$）', '年月': '年月', 'カテゴリ': 'カテゴリ'}
            )
            fig_category_stack.update_xaxes(tickangle=45)
            st.plotly_chart(fig_category_stack, use_container_width=True)
            
            st.markdown("---")
            
            # 月別のカテゴリ別支出（ヒートマップ）
            st.subheader("月別のカテゴリ別支出（ヒートマップ）")
            
            category_monthly_pivot = category_monthly_stack.pivot(index='カテゴリ', columns='年月', values='支出額').fillna(0)
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=category_monthly_pivot.values,
                x=category_monthly_pivot.columns,
                y=category_monthly_pivot.index,
                colorscale='Viridis',
                text=category_monthly_pivot.values,
                texttemplate='%{text:.0f}',
                textfont={"size": 10}
            ))
            
            fig_heatmap.update_layout(
                title="月別のカテゴリ別支出（ヒートマップ）",
                xaxis_title="年月",
                yaxis_title="カテゴリ"
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # ========== タブ7: カテゴリ×ベンダー分析 ==========
        with tab7:
            st.title("🔗 カテゴリ×ベンダー分析")
            st.markdown("---")
            
            # カテゴリ×ベンダーマトリックス
            st.subheader("カテゴリ×ベンダーマトリックス")
            
            category_vendor_expense = filtered_df.groupby(['Category', 'Vendor'])['EXP'].sum().reset_index()
            category_vendor_expense.columns = ['カテゴリ', 'ベンダー', '総支出']
            
            category_vendor_count = filtered_df.groupby(['Category', 'Vendor']).size().reset_index()
            category_vendor_count.columns = ['カテゴリ', 'ベンダー', '取引件数']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 総支出のヒートマップ
                cv_expense_pivot = category_vendor_expense.pivot(index='カテゴリ', columns='ベンダー', values='総支出').fillna(0)
                
                fig_cv_expense = go.Figure(data=go.Heatmap(
                    z=cv_expense_pivot.values,
                    x=cv_expense_pivot.columns,
                    y=cv_expense_pivot.index,
                    colorscale='YlOrRd',
                    text=cv_expense_pivot.values,
                    texttemplate='%{text:.0f}',
                    textfont={"size": 8}
                ))
                
                fig_cv_expense.update_layout(
                    title="カテゴリ×ベンダー別の総支出（ヒートマップ）",
                    xaxis_title="ベンダー",
                    yaxis_title="カテゴリ",
                    height=400
                )
                
                st.plotly_chart(fig_cv_expense, use_container_width=True)
            
            with col2:
                # 取引件数のヒートマップ
                cv_count_pivot = category_vendor_count.pivot(index='カテゴリ', columns='ベンダー', values='取引件数').fillna(0)
                
                fig_cv_count = go.Figure(data=go.Heatmap(
                    z=cv_count_pivot.values,
                    x=cv_count_pivot.columns,
                    y=cv_count_pivot.index,
                    colorscale='Blues',
                    text=cv_count_pivot.values,
                    texttemplate='%{text:.0f}',
                    textfont={"size": 8}
                ))
                
                fig_cv_count.update_layout(
                    title="カテゴリ×ベンダー別の取引件数（ヒートマップ）",
                    xaxis_title="ベンダー",
                    yaxis_title="カテゴリ",
                    height=400
                )
                
                st.plotly_chart(fig_cv_count, use_container_width=True)
            
            st.markdown("---")
            
            # 主要カテゴリのベンダー分析
            st.subheader("主要カテゴリのベンダー分析")
            
            top_categories = filtered_df.groupby('Category')['EXP'].sum().nlargest(3).index.tolist()
            
            for category in top_categories:
                st.write(f"**{category}カテゴリ**")
                category_vendors = filtered_df[filtered_df['Category'] == category].groupby('Vendor')['EXP'].sum().reset_index()
                category_vendors = category_vendors.sort_values('EXP', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_cat_vendor = px.bar(
                        category_vendors,
                        x='EXP',
                        y='Vendor',
                        orientation='h',
                        title=f"{category}カテゴリのベンダー別支出",
                        labels={'EXP': '支出額（$）', 'Vendor': 'ベンダー'}
                    )
                    st.plotly_chart(fig_cat_vendor, use_container_width=True)
                
                with col2:
                    category_vendor_count_cat = filtered_df[filtered_df['Category'] == category].groupby('Vendor').size().reset_index()
                    category_vendor_count_cat.columns = ['Vendor', '取引件数']
                    category_vendor_count_cat = category_vendor_count_cat.sort_values('取引件数', ascending=False)
                    
                    fig_cat_vendor_count = px.bar(
                        category_vendor_count_cat,
                        x='取引件数',
                        y='Vendor',
                        orientation='h',
                        title=f"{category}カテゴリのベンダー別取引件数",
                        labels={'取引件数': '取引件数（件）', 'Vendor': 'ベンダー'}
                    )
                    st.plotly_chart(fig_cat_vendor_count, use_container_width=True)
                
                st.markdown("---")
            
            # 主要ベンダーのカテゴリ分析
            st.subheader("主要ベンダーのカテゴリ分析")
            
            top_vendors = filtered_df.groupby('Vendor')['EXP'].sum().nlargest(3).index.tolist()
            
            for vendor in top_vendors:
                st.write(f"**{vendor}**")
                vendor_categories = filtered_df[filtered_df['Vendor'] == vendor].groupby('Category')['EXP'].sum().reset_index()
                vendor_categories = vendor_categories.sort_values('EXP', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_vendor_cat = px.bar(
                        vendor_categories,
                        x='EXP',
                        y='Category',
                        orientation='h',
                        title=f"{vendor}のカテゴリ別支出",
                        labels={'EXP': '支出額（$）', 'Category': 'カテゴリ'}
                    )
                    st.plotly_chart(fig_vendor_cat, use_container_width=True)
                
                with col2:
                    vendor_cat_count = filtered_df[filtered_df['Vendor'] == vendor].groupby('Category').size().reset_index()
                    vendor_cat_count.columns = ['Category', '取引件数']
                    vendor_cat_count = vendor_cat_count.sort_values('取引件数', ascending=False)
                    
                    fig_vendor_cat_count = px.bar(
                        vendor_cat_count,
                        x='取引件数',
                        y='Category',
                        orientation='h',
                        title=f"{vendor}のカテゴリ別取引件数",
                        labels={'取引件数': '取引件数（件）', 'Category': 'カテゴリ'}
                    )
                    st.plotly_chart(fig_vendor_cat_count, use_container_width=True)
                
                st.markdown("---")
        
        # ========== タブ8: 詳細データ探索 ==========
        with tab8:
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
            
            # データエクスポート
            st.subheader("データエクスポート")
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                csv = sorted_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 フィルター済みデータをCSVでダウンロード",
                    data=csv,
                    file_name="filtered_expense_data.csv",
                    mime="text/csv"
                )
            
            with col_export2:
                # Excel形式でのエクスポート
                try:
                    from io import BytesIO
                    excel_buffer = BytesIO()
                    sorted_df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    excel_data = excel_buffer.getvalue()
                    
                    st.download_button(
                        label="📊 フィルター済みデータをExcelでダウンロード",
                        data=excel_data,
                        file_name="filtered_expense_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.warning(f"Excelエクスポート機能は利用できません: {str(e)}")
            
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

