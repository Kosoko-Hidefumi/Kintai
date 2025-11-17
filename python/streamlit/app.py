"""
Streamlit ダッシュボード - ステップ1（ミニマム版）
顧客購買データ可視化ダッシュボード
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ページ設定
st.set_page_config(
    page_title="顧客購買データダッシュボード",
    page_icon="📊",
    layout="wide"
)

# データの読み込み
@st.cache_data
def load_data():
    """CSVファイルを読み込む"""
    try:
        df = pd.read_csv("data/sample-data.csv")
        # 購入日を日付型に変換
        df['購入日'] = pd.to_datetime(df['購入日'])
        return df
    except FileNotFoundError:
        st.error("データファイルが見つかりません: data/sample-data.csv")
        return None
    except Exception as e:
        st.error(f"データの読み込み中にエラーが発生しました: {str(e)}")
        return None

# データ読み込み
df = load_data()

if df is not None:
    # サイドバー - フィルター設定
    st.sidebar.header("📋 フィルター設定")
    
    # 地域フィルター
    regions = st.sidebar.multiselect(
        "地域を選択",
        options=sorted(df['地域'].unique()),
        default=sorted(df['地域'].unique())
    )
    
    # カテゴリーフィルター
    categories = st.sidebar.multiselect(
        "購入カテゴリーを選択",
        options=sorted(df['購入カテゴリー'].unique()),
        default=sorted(df['購入カテゴリー'].unique())
    )
    
    # データフィルタリング
    if len(regions) > 0 and len(categories) > 0:
        filtered_df = df[
            (df['地域'].isin(regions)) & 
            (df['購入カテゴリー'].isin(categories))
        ]
    else:
        filtered_df = pd.DataFrame()
        st.sidebar.warning("フィルターを1つ以上選択してください。")
    
    # メインコンテンツ
    if len(filtered_df) > 0:
        # タブ作成（トップページと詳細データ探索ページ）
        tab1, tab2 = st.tabs(["📊 概要ダッシュボード", "🔍 詳細データ探索"])
        
        # ========== タブ1: 概要ダッシュボード ==========
        with tab1:
            st.title("📊 顧客購買データ 概要ダッシュボード")
            st.markdown("---")
            
            # 主要KPI指標（4列）
            st.subheader("主要指標")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_customers = len(filtered_df['顧客ID'].unique())
                st.metric("総顧客数", f"{total_customers:,}人")
            
            with col2:
                total_sales = filtered_df['購入金額'].sum()
                st.metric("総購入金額", f"¥{total_sales:,.0f}")
            
            with col3:
                avg_sales = filtered_df['購入金額'].mean()
                st.metric("平均購入金額", f"¥{avg_sales:,.0f}")
            
            with col4:
                total_transactions = len(filtered_df)
                st.metric("総購入件数", f"{total_transactions:,}件")
            
            st.markdown("---")
            
            # トレンド表示（2列）
            st.subheader("トレンド分析")
            
            # 月別集計の準備
            filtered_df['年月'] = filtered_df['購入日'].dt.to_period('M').astype(str)
            monthly_sales = filtered_df.groupby('年月')['購入金額'].sum().reset_index()
            monthly_sales.columns = ['年月', '購入金額']
            
            monthly_count = filtered_df.groupby('年月').size().reset_index()
            monthly_count.columns = ['年月', '購入件数']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 月別売上推移（折れ線グラフ）
                fig_sales = px.line(
                    monthly_sales,
                    x='年月',
                    y='購入金額',
                    title="月別売上推移",
                    markers=True,
                    labels={'購入金額': '購入金額（円）', '年月': '年月'}
                )
                fig_sales.update_xaxes(tickangle=45)
                st.plotly_chart(fig_sales, use_container_width=True)
            
            with col2:
                # 月別購入件数推移（棒グラフ）
                fig_count = px.bar(
                    monthly_count,
                    x='年月',
                    y='購入件数',
                    title="月別購入件数推移",
                    labels={'購入件数': '購入件数（件）', '年月': '年月'}
                )
                fig_count.update_xaxes(tickangle=45)
                st.plotly_chart(fig_count, use_container_width=True)
            
            st.markdown("---")
            
            # 主要インサイト（3列）
            st.subheader("主要インサイト")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # 地域別売上シェア（円グラフ）
                region_sales = filtered_df.groupby('地域')['購入金額'].sum().reset_index()
                fig_region = px.pie(
                    region_sales,
                    values='購入金額',
                    names='地域',
                    title="地域別売上シェア"
                )
                st.plotly_chart(fig_region, use_container_width=True)
            
            with col2:
                # カテゴリー別売上シェア（円グラフ）
                category_sales = filtered_df.groupby('購入カテゴリー')['購入金額'].sum().reset_index()
                fig_category = px.pie(
                    category_sales,
                    values='購入金額',
                    names='購入カテゴリー',
                    title="カテゴリー別売上シェア"
                )
                st.plotly_chart(fig_category, use_container_width=True)
            
            with col3:
                # 支払方法別シェア（円グラフ）
                payment_sales = filtered_df.groupby('支払方法')['購入金額'].sum().reset_index()
                fig_payment = px.pie(
                    payment_sales,
                    values='購入金額',
                    names='支払方法',
                    title="支払方法別シェア"
                )
                st.plotly_chart(fig_payment, use_container_width=True)
        
        # ========== タブ2: 詳細データ探索 ==========
        with tab2:
            st.title("🔍 詳細データ探索")
            st.markdown("---")
            
            # データテーブル
            st.subheader("データテーブル")
            
            # ソート機能（1カラムのみ）
            sort_column = st.selectbox(
                "ソートするカラムを選択",
                options=['購入日', '購入金額', '年齢', '顧客ID'],
                index=0
            )
            
            sort_ascending = st.checkbox("昇順でソート", value=True)
            
            # ソート適用
            sorted_df = filtered_df.sort_values(
                by=sort_column,
                ascending=sort_ascending
            )
            
            # テーブル表示
            st.dataframe(
                sorted_df,
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
                file_name="filtered_data.csv",
                mime="text/csv"
            )
            
            # データサマリー
            st.markdown("---")
            st.subheader("データサマリー")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**表示中のレコード数**: {len(sorted_df):,}件")
                st.write(f"**表示中の顧客数**: {len(sorted_df['顧客ID'].unique()):,}人")
            
            with col2:
                st.write(f"**期間**: {sorted_df['購入日'].min().strftime('%Y-%m-%d')} ～ {sorted_df['購入日'].max().strftime('%Y-%m-%d')}")
                st.write(f"**合計金額**: ¥{sorted_df['購入金額'].sum():,.0f}")
    
    else:
        st.warning("フィルター条件に一致するデータがありません。フィルター設定を変更してください。")

else:
    st.info("データファイルを配置して、アプリを再読み込みしてください。")
