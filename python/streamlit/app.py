"""
Streamlit ダッシュボード - ステップ2（機能追加版）
顧客購買データ可視化ダッシュボード
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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

# 年齢層分類関数
def categorize_age(age):
    """年齢を年齢層に分類"""
    if age < 20:
        return "10代"
    elif age < 30:
        return "20代"
    elif age < 40:
        return "30代"
    elif age < 50:
        return "40代"
    elif age < 60:
        return "50代"
    elif age < 70:
        return "60代"
    else:
        return "70代以上"

# データ読み込み
df = load_data()

if df is not None:
    # 年齢層カラムを追加
    df['年齢層'] = df['年齢'].apply(categorize_age)
    
    # サイドバー - フィルター設定
    st.sidebar.header("📋 フィルター設定")
    
    # 期間フィルター
    st.sidebar.subheader("期間")
    min_date = df['購入日'].min().date()
    max_date = df['購入日'].max().date()
    
    date_range = st.sidebar.date_input(
        "購入日の期間を選択",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 地域フィルター
    st.sidebar.subheader("地域")
    regions = st.sidebar.multiselect(
        "地域を選択",
        options=sorted(df['地域'].unique()),
        default=sorted(df['地域'].unique()),
        label_visibility="collapsed"
    )
    
    # カテゴリーフィルター
    st.sidebar.subheader("購入カテゴリー")
    categories = st.sidebar.multiselect(
        "購入カテゴリーを選択",
        options=sorted(df['購入カテゴリー'].unique()),
        default=sorted(df['購入カテゴリー'].unique()),
        label_visibility="collapsed"
    )
    
    # 性別フィルター
    st.sidebar.subheader("性別")
    genders = st.sidebar.multiselect(
        "性別を選択",
        options=sorted(df['性別'].unique()),
        default=sorted(df['性別'].unique()),
        label_visibility="collapsed"
    )
    
    # 年齢層フィルター
    st.sidebar.subheader("年齢層")
    age_min = int(df['年齢'].min())
    age_max = int(df['年齢'].max())
    age_range = st.sidebar.slider(
        "年齢の範囲",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
        label_visibility="collapsed"
    )
    
    # 購入金額フィルター
    st.sidebar.subheader("購入金額")
    amount_min = int(df['購入金額'].min())
    amount_max = int(df['購入金額'].max())
    amount_range = st.sidebar.slider(
        "購入金額の範囲（円）",
        min_value=amount_min,
        max_value=amount_max,
        value=(amount_min, amount_max),
        step=1000,
        label_visibility="collapsed"
    )
    
    # 支払方法フィルター
    st.sidebar.subheader("支払方法")
    payment_methods = st.sidebar.multiselect(
        "支払方法を選択",
        options=sorted(df['支払方法'].unique()),
        default=sorted(df['支払方法'].unique()),
        label_visibility="collapsed"
    )
    
    # データフィルタリング
    filtered_df = df.copy()
    
    # 期間フィルター
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered_df = filtered_df[
            (filtered_df['購入日'] >= start_date) & 
            (filtered_df['購入日'] <= end_date)
        ]
    
    # その他のフィルター
    if len(regions) > 0:
        filtered_df = filtered_df[filtered_df['地域'].isin(regions)]
    if len(categories) > 0:
        filtered_df = filtered_df[filtered_df['購入カテゴリー'].isin(categories)]
    if len(genders) > 0:
        filtered_df = filtered_df[filtered_df['性別'].isin(genders)]
    if len(payment_methods) > 0:
        filtered_df = filtered_df[filtered_df['支払方法'].isin(payment_methods)]
    
    # 年齢と購入金額の範囲フィルター
    filtered_df = filtered_df[
        (filtered_df['年齢'] >= age_range[0]) & 
        (filtered_df['年齢'] <= age_range[1]) &
        (filtered_df['購入金額'] >= amount_range[0]) & 
        (filtered_df['購入金額'] <= amount_range[1])
    ]
    
    # メインコンテンツ
    if len(filtered_df) > 0:
        # タブ作成
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 概要ダッシュボード", 
            "📅 時系列分析",
            "👥 顧客分析",
            "💰 売上分析",
            "🔍 詳細データ探索"
        ])
        
        # ========== タブ1: 概要ダッシュボード ==========
        with tab1:
            st.title("📊 顧客購買データ 概要ダッシュボード")
            st.markdown("---")
            
            # 主要KPI指標（8列）
            st.subheader("主要指標")
            col1, col2, col3, col4 = st.columns(4)
            col5, col6, col7, col8 = st.columns(4)
            
            total_customers = len(filtered_df['顧客ID'].unique())
            total_sales = filtered_df['購入金額'].sum()
            avg_sales = filtered_df['購入金額'].mean()
            total_transactions = len(filtered_df)
            
            # 顧客単価の計算
            customer_value = total_sales / total_customers if total_customers > 0 else 0
            
            # 月間平均売上の計算
            filtered_df['年月'] = filtered_df['購入日'].dt.to_period('M').astype(str)
            monthly_sales = filtered_df.groupby('年月')['購入金額'].sum()
            monthly_avg_sales = monthly_sales.mean() if len(monthly_sales) > 0 else 0
            
            # リピート率の計算
            customer_purchase_count = filtered_df.groupby('顧客ID').size()
            repeat_customers = len(customer_purchase_count[customer_purchase_count > 1])
            repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
            
            # 成長率の計算（最新月と前月の比較）
            if len(monthly_sales) >= 2:
                latest_month = monthly_sales.iloc[-1]
                previous_month = monthly_sales.iloc[-2]
                growth_rate = ((latest_month - previous_month) / previous_month * 100) if previous_month > 0 else 0
            else:
                growth_rate = 0
            
            with col1:
                st.metric("総顧客数", f"{total_customers:,}人")
            
            with col2:
                st.metric("総購入金額", f"¥{total_sales:,.0f}")
            
            with col3:
                st.metric("平均購入金額", f"¥{avg_sales:,.0f}")
            
            with col4:
                st.metric("総購入件数", f"{total_transactions:,}件")
            
            with col5:
                st.metric("顧客単価", f"¥{customer_value:,.0f}")
            
            with col6:
                st.metric("月間平均売上", f"¥{monthly_avg_sales:,.0f}")
            
            with col7:
                st.metric("リピート率", f"{repeat_rate:.1f}%")
            
            with col8:
                growth_color = "normal" if growth_rate >= 0 else "inverse"
                st.metric("成長率", f"{growth_rate:+.1f}%", delta=f"{growth_rate:+.1f}%")
            
            st.markdown("---")
            
            # トレンド表示（2列）
            st.subheader("トレンド分析")
            
            monthly_sales_df = filtered_df.groupby('年月')['購入金額'].sum().reset_index()
            monthly_sales_df.columns = ['年月', '購入金額']
            
            monthly_count_df = filtered_df.groupby('年月').size().reset_index()
            monthly_count_df.columns = ['年月', '購入件数']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_sales = px.line(
                    monthly_sales_df,
                    x='年月',
                    y='購入金額',
                    title="月別売上推移",
                    markers=True,
                    labels={'購入金額': '購入金額（円）', '年月': '年月'}
                )
                fig_sales.update_xaxes(tickangle=45)
                st.plotly_chart(fig_sales, use_container_width=True)
            
            with col2:
                fig_count = px.bar(
                    monthly_count_df,
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
                region_sales = filtered_df.groupby('地域')['購入金額'].sum().reset_index()
                fig_region = px.pie(
                    region_sales,
                    values='購入金額',
                    names='地域',
                    title="地域別売上シェア"
                )
                st.plotly_chart(fig_region, use_container_width=True)
            
            with col2:
                category_sales = filtered_df.groupby('購入カテゴリー')['購入金額'].sum().reset_index()
                fig_category = px.pie(
                    category_sales,
                    values='購入金額',
                    names='購入カテゴリー',
                    title="カテゴリー別売上シェア"
                )
                st.plotly_chart(fig_category, use_container_width=True)
            
            with col3:
                payment_sales = filtered_df.groupby('支払方法')['購入金額'].sum().reset_index()
                fig_payment = px.pie(
                    payment_sales,
                    values='購入金額',
                    names='支払方法',
                    title="支払方法別シェア"
                )
                st.plotly_chart(fig_payment, use_container_width=True)
        
        # ========== タブ2: 時系列分析 ==========
        with tab2:
            st.title("📅 時系列分析")
            st.markdown("---")
            
            # 月別トレンド
            st.subheader("月別トレンド")
            
            monthly_trend = filtered_df.groupby('年月').agg({
                '購入金額': ['sum', 'mean', 'count']
            }).reset_index()
            monthly_trend.columns = ['年月', '総売上', '平均購入金額', '購入件数']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig_sales_trend = px.line(
                    monthly_trend,
                    x='年月',
                    y='総売上',
                    title="月別売上推移",
                    markers=True,
                    labels={'総売上': '売上（円）', '年月': '年月'}
                )
                fig_sales_trend.update_xaxes(tickangle=45)
                st.plotly_chart(fig_sales_trend, use_container_width=True)
            
            with col2:
                fig_count_trend = px.line(
                    monthly_trend,
                    x='年月',
                    y='購入件数',
                    title="月別購入件数推移",
                    markers=True,
                    labels={'購入件数': '購入件数（件）', '年月': '年月'}
                )
                fig_count_trend.update_xaxes(tickangle=45)
                st.plotly_chart(fig_count_trend, use_container_width=True)
            
            with col3:
                fig_avg_trend = px.line(
                    monthly_trend,
                    x='年月',
                    y='平均購入金額',
                    title="月別平均購入金額推移",
                    markers=True,
                    labels={'平均購入金額': '平均購入金額（円）', '年月': '年月'}
                )
                fig_avg_trend.update_xaxes(tickangle=45)
                st.plotly_chart(fig_avg_trend, use_container_width=True)
            
            st.markdown("---")
            
            # 年別比較
            st.subheader("年別比較")
            
            filtered_df['年'] = filtered_df['購入日'].dt.year
            filtered_df['月'] = filtered_df['購入日'].dt.month
            
            yearly_comparison = filtered_df.groupby(['年', '月'])['購入金額'].sum().reset_index()
            yearly_comparison['年月'] = yearly_comparison['月'].astype(str) + '月'
            
            fig_yearly = px.line(
                yearly_comparison,
                x='月',
                y='購入金額',
                color='年',
                title="2023年 vs 2024年 月別比較",
                markers=True,
                labels={'購入金額': '購入金額（円）', '月': '月', '年': '年'}
            )
            st.plotly_chart(fig_yearly, use_container_width=True)
        
        # ========== タブ3: 顧客分析 ==========
        with tab3:
            st.title("👥 顧客分析")
            st.markdown("---")
            
            # 年齢層別分析
            st.subheader("年齢層別分析")
            
            age_group_stats = filtered_df.groupby('年齢層').agg({
                '顧客ID': 'nunique',
                '購入金額': 'mean'
            }).reset_index()
            age_group_stats.columns = ['年齢層', '顧客数', '平均購入金額']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_age_customers = px.bar(
                    age_group_stats,
                    x='年齢層',
                    y='顧客数',
                    title="年齢層別顧客数",
                    labels={'顧客数': '顧客数（人）', '年齢層': '年齢層'},
                    category_orders={'年齢層': ['10代', '20代', '30代', '40代', '50代', '60代', '70代以上']}
                )
                st.plotly_chart(fig_age_customers, use_container_width=True)
            
            with col2:
                fig_age_sales = px.bar(
                    age_group_stats,
                    x='年齢層',
                    y='平均購入金額',
                    title="年齢層別平均購入金額",
                    labels={'平均購入金額': '平均購入金額（円）', '年齢層': '年齢層'},
                    category_orders={'年齢層': ['10代', '20代', '30代', '40代', '50代', '60代', '70代以上']}
                )
                st.plotly_chart(fig_age_sales, use_container_width=True)
            
            st.markdown("---")
            
            # 性別分析
            st.subheader("性別分析")
            
            gender_stats = filtered_df.groupby('性別').agg({
                '顧客ID': 'nunique',
                '購入金額': 'mean'
            }).reset_index()
            gender_stats.columns = ['性別', '顧客数', '平均購入金額']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_gender_customers = px.pie(
                    gender_stats,
                    values='顧客数',
                    names='性別',
                    title="性別の顧客数"
                )
                st.plotly_chart(fig_gender_customers, use_container_width=True)
            
            with col2:
                fig_gender_sales = px.bar(
                    gender_stats,
                    x='性別',
                    y='平均購入金額',
                    title="性別の平均購入金額",
                    labels={'平均購入金額': '平均購入金額（円）', '性別': '性別'}
                )
                st.plotly_chart(fig_gender_sales, use_container_width=True)
            
            st.markdown("---")
            
            # 年齢と購入金額の関係
            st.subheader("年齢と購入金額の関係")
            
            fig_scatter = px.scatter(
                filtered_df,
                x='年齢',
                y='購入金額',
                color='性別',
                title="年齢 vs 購入金額",
                labels={'年齢': '年齢（歳）', '購入金額': '購入金額（円）', '性別': '性別'},
                hover_data=['地域', '購入カテゴリー']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # ========== タブ4: 売上分析 ==========
        with tab4:
            st.title("💰 売上分析")
            st.markdown("---")
            
            # 売上概要
            st.subheader("売上概要")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_sales_amount = filtered_df['購入金額'].sum()
            avg_unit_price = filtered_df['購入金額'].mean()
            max_amount = filtered_df['購入金額'].max()
            min_amount = filtered_df['購入金額'].min()
            
            with col1:
                st.metric("総売上高", f"¥{total_sales_amount:,.0f}")
            
            with col2:
                st.metric("平均単価", f"¥{avg_unit_price:,.0f}")
            
            with col3:
                st.metric("最大購入金額", f"¥{max_amount:,.0f}")
            
            with col4:
                st.metric("最小購入金額", f"¥{min_amount:,.0f}")
            
            st.markdown("---")
            
            # 購入金額のヒストグラム
            st.subheader("購入金額の分布")
            fig_hist = px.histogram(
                filtered_df,
                x='購入金額',
                nbins=30,
                title="購入金額の分布",
                labels={'購入金額': '購入金額（円）', 'count': '件数'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            st.markdown("---")
            
            # カテゴリー別売上分析
            st.subheader("カテゴリー別売上分析")
            
            category_analysis = filtered_df.groupby('購入カテゴリー').agg({
                '購入金額': ['sum', 'mean', 'count']
            }).reset_index()
            category_analysis.columns = ['カテゴリー', '総売上', '平均購入金額', '購入件数']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig_cat_sales = px.bar(
                    category_analysis,
                    x='総売上',
                    y='カテゴリー',
                    orientation='h',
                    title="カテゴリー別総売上",
                    labels={'総売上': '総売上（円）', 'カテゴリー': 'カテゴリー'}
                )
                st.plotly_chart(fig_cat_sales, use_container_width=True)
            
            with col2:
                fig_cat_avg = px.bar(
                    category_analysis,
                    x='平均購入金額',
                    y='カテゴリー',
                    orientation='h',
                    title="カテゴリー別平均購入金額",
                    labels={'平均購入金額': '平均購入金額（円）', 'カテゴリー': 'カテゴリー'}
                )
                st.plotly_chart(fig_cat_avg, use_container_width=True)
            
            with col3:
                fig_cat_count = px.bar(
                    category_analysis,
                    x='購入件数',
                    y='カテゴリー',
                    orientation='h',
                    title="カテゴリー別購入件数",
                    labels={'購入件数': '購入件数（件）', 'カテゴリー': 'カテゴリー'}
                )
                st.plotly_chart(fig_cat_count, use_container_width=True)
            
            st.markdown("---")
            
            # 地域別売上分析
            st.subheader("地域別売上分析")
            
            region_analysis = filtered_df.groupby('地域').agg({
                '購入金額': ['sum', 'mean']
            }).reset_index()
            region_analysis.columns = ['地域', '総売上', '平均購入金額']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_region_sales = px.bar(
                    region_analysis,
                    x='総売上',
                    y='地域',
                    orientation='h',
                    title="地域別総売上",
                    labels={'総売上': '総売上（円）', '地域': '地域'}
                )
                st.plotly_chart(fig_region_sales, use_container_width=True)
            
            with col2:
                fig_region_avg = px.bar(
                    region_analysis,
                    x='平均購入金額',
                    y='地域',
                    orientation='h',
                    title="地域別平均購入金額",
                    labels={'平均購入金額': '平均購入金額（円）', '地域': '地域'}
                )
                st.plotly_chart(fig_region_avg, use_container_width=True)
        
        # ========== タブ5: 詳細データ探索 ==========
        with tab5:
            st.title("🔍 詳細データ探索")
            st.markdown("---")
            
            # 検索機能
            st.subheader("検索")
            customer_id_search = st.text_input("顧客IDで検索（空欄の場合は全件表示）")
            
            # フィルター適用
            search_df = filtered_df.copy()
            if customer_id_search:
                try:
                    customer_id = int(customer_id_search)
                    search_df = search_df[search_df['顧客ID'] == customer_id]
                except ValueError:
                    st.warning("顧客IDは数値で入力してください。")
                    search_df = pd.DataFrame()
            
            if len(search_df) > 0:
                # ソート機能（複数カラム）
                st.subheader("ソート設定")
                col1, col2 = st.columns(2)
                
                with col1:
                    sort_column1 = st.selectbox(
                        "第1ソートカラム",
                        options=['購入日', '購入金額', '年齢', '顧客ID'],
                        index=0
                    )
                    sort_ascending1 = st.checkbox("第1ソート: 昇順", value=True)
                
                with col2:
                    sort_column2 = st.selectbox(
                        "第2ソートカラム",
                        options=['なし', '購入日', '購入金額', '年齢', '顧客ID'],
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
                
                # データテーブル
                st.subheader("データテーブル")
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
                st.warning("検索条件に一致するデータがありません。")
    
    else:
        st.warning("フィルター条件に一致するデータがありません。フィルター設定を変更してください。")

else:
    st.info("データファイルを配置して、アプリを再読み込みしてください。")
