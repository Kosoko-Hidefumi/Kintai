"""
Googleスプレッドシート接続モジュール
"""
import gspread
from gspread.exceptions import SpreadsheetNotFound, APIError
from google.oauth2 import service_account
import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any


def get_credentials():
    """
    Streamlit secretsから認証情報を取得
    """
    try:
        # secrets.tomlから認証情報を取得
        creds_dict = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        return creds
    except Exception as e:
        st.error(f"認証情報の取得に失敗しました: {e}")
        st.info("`.streamlit/secrets.toml` に認証情報が設定されているか確認してください。")
        return None


@st.cache_resource
def get_client():
    """
    gspreadクライアントを取得（キャッシュ付き）
    """
    creds = get_credentials()
    if creds is None:
        return None
    try:
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"gspreadクライアントの作成に失敗しました: {e}")
        return None


def get_spreadsheet(spreadsheet_id: str):
    """
    スプレッドシートを取得
    """
    client = get_client()
    if client is None:
        return None
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        return spreadsheet
    except SpreadsheetNotFound:
        st.error(f"❌ スプレッドシートが見つかりませんでした。")
        st.info(f"""
        **確認事項:**
        1. スプレッドシートIDが正しいか確認してください: `{spreadsheet_id}`
        2. サービスアカウントにスプレッドシートの編集権限が付与されているか確認してください
        3. サービスアカウントのメールアドレス: `id-165@arctic-badge-484907-n8.iam.gserviceaccount.com`
        
        **解決方法:**
        - スプレッドシートの「共有」設定で、上記のメールアドレスを「編集者」として追加してください
        """)
        return None
    except APIError as e:
        error_code = e.response.status_code if hasattr(e, 'response') else 'Unknown'
        if error_code == 404:
            st.error(f"❌ スプレッドシートが見つかりません（404エラー）")
            st.info(f"""
            **考えられる原因:**
            1. スプレッドシートIDが間違っている: `{spreadsheet_id}`
            2. サービスアカウントにアクセス権限がない
            
            **確認手順:**
            1. スプレッドシートを開いて、URLからIDを確認
            2. スプレッドシートの「共有」ボタンをクリック
            3. `id-165@arctic-badge-484907-n8.iam.gserviceaccount.com` が追加されているか確認
            4. 権限が「編集者」になっているか確認
            """)
        else:
            st.error(f"❌ APIエラーが発生しました: {e}")
        return None
    except Exception as e:
        st.error(f"❌ スプレッドシートの取得に失敗しました: {e}")
        st.info(f"スプレッドシートID: `{spreadsheet_id}`")
        return None


def get_worksheet(spreadsheet_id: str, sheet_name: str):
    """
    指定したシートを取得
    """
    spreadsheet = get_spreadsheet(spreadsheet_id)
    if spreadsheet is None:
        return None
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet
    except Exception as e:
        st.error(f"シート '{sheet_name}' の取得に失敗しました: {e}")
        return None


@st.cache_data(ttl=60)  # 60秒間キャッシュ
def read_attendance_logs(spreadsheet_id: str) -> pd.DataFrame:
    """
    勤怠ログを読み込む（キャッシュ付き）
    """
    worksheet = get_worksheet(spreadsheet_id, "attendance_logs")
    if worksheet is None:
        return pd.DataFrame()
    
    try:
        # ヘッダー行を含めて全データを取得
        data = worksheet.get_all_records()
        if not data:
            # 空の場合はヘッダーのみのDataFrameを返す
            return pd.DataFrame(columns=[
                "event_id", "date", "staff_name", "type", 
                "start_time", "end_time", "duration_hours", 
                "day_equivalent", "fiscal_year", "remarks"
            ])
        df = pd.DataFrame(data)
        return df
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: ページをリロードするか、1〜2分待ってから再度アクセスしてください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"勤怠ログの読み込みに失敗しました: {e}")
        return pd.DataFrame()


def write_attendance_log(spreadsheet_id: str, log_data: Dict[str, Any]):
    """
    勤怠ログを1件追加
    """
    worksheet = get_worksheet(spreadsheet_id, "attendance_logs")
    if worksheet is None:
        return False
    
    try:
        # 既存データを確認してヘッダーがあるかチェック
        existing_data = worksheet.get_all_values()
        if not existing_data:
            # ヘッダーがない場合は追加
            headers = [
                "event_id", "date", "staff_name", "type",
                "start_time", "end_time", "duration_hours",
                "day_equivalent", "fiscal_year", "remarks"
            ]
            worksheet.append_row(headers)
        
        # データを追加
        row = [
            log_data.get("event_id", ""),
            log_data.get("date", ""),
            log_data.get("staff_name", ""),
            log_data.get("type", ""),
            log_data.get("start_time", ""),
            log_data.get("end_time", ""),
            log_data.get("duration_hours", ""),
            log_data.get("day_equivalent", ""),
            log_data.get("fiscal_year", ""),
            log_data.get("remarks", "")
        ]
        worksheet.append_row(row)
        # キャッシュをクリアして最新データを反映
        read_attendance_logs.clear()
        return True
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"勤怠ログの書き込みに失敗しました: {e}")
        return False


@st.cache_data(ttl=60)  # 60秒間キャッシュ
def read_bulletin_board(spreadsheet_id: str) -> pd.DataFrame:
    """
    掲示板データを読み込む（最新順にソート、キャッシュ付き）
    """
    worksheet = get_worksheet(spreadsheet_id, "bulletin_board")
    if worksheet is None:
        return pd.DataFrame()
    
    try:
        data = worksheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=["timestamp", "author", "title", "content"])
        
        df = pd.DataFrame(data)
        # timestampで降順ソート（最新が上）
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.sort_values("timestamp", ascending=False)
        return df
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: ページをリロードするか、1〜2分待ってから再度アクセスしてください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"掲示板データの読み込みに失敗しました: {e}")
        return pd.DataFrame()


def write_bulletin_post(spreadsheet_id: str, post_data: Dict[str, Any]):
    """
    掲示板に投稿を追加
    """
    worksheet = get_worksheet(spreadsheet_id, "bulletin_board")
    if worksheet is None:
        return False
    
    try:
        # 既存データを確認してヘッダーがあるかチェック
        existing_data = worksheet.get_all_values()
        if not existing_data:
            # ヘッダーがない場合は追加
            headers = ["timestamp", "author", "title", "content"]
            worksheet.append_row(headers)
        
        # データを追加
        row = [
            post_data.get("timestamp", ""),
            post_data.get("author", ""),
            post_data.get("title", ""),
            post_data.get("content", "")
        ]
        worksheet.append_row(row)
        # キャッシュをクリアして最新データを反映
        read_bulletin_board.clear()
        return True
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"掲示板への投稿に失敗しました: {e}")
        return False


@st.cache_data(ttl=60)  # 60秒間キャッシュ
def read_events(spreadsheet_id: str) -> pd.DataFrame:
    """
    イベントデータを読み込む（キャッシュ付き）
    """
    worksheet = get_worksheet(spreadsheet_id, "events")
    if worksheet is None:
        return pd.DataFrame()
    
    try:
        data = worksheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=["event_id", "start_date", "end_date", "title", "description", "color"])
        df = pd.DataFrame(data)
        return df
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: ページをリロードするか、1〜2分待ってから再度アクセスしてください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"イベントデータの読み込みに失敗しました: {e}")
        return pd.DataFrame()


def write_event(spreadsheet_id: str, event_data: Dict[str, Any]):
    """
    イベントを追加
    """
    worksheet = get_worksheet(spreadsheet_id, "events")
    if worksheet is None:
        return False
    
    try:
        # 既存データを確認してヘッダーがあるかチェック
        existing_data = worksheet.get_all_values()
        if not existing_data:
            # ヘッダーがない場合は追加
            headers = ["event_id", "start_date", "end_date", "title", "description", "color"]
            worksheet.append_row(headers)
        
        # データを追加
        row = [
            event_data.get("event_id", ""),
            event_data.get("start_date", ""),
            event_data.get("end_date", ""),
            event_data.get("title", ""),
            event_data.get("description", ""),
            event_data.get("color", "#95A5A6")
        ]
        worksheet.append_row(row)
        # キャッシュをクリアして最新データを反映
        read_events.clear()
        return True
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"イベントの追加に失敗しました: {e}")
        return False


def delete_all_attendance_logs(spreadsheet_id: str) -> bool:
    """
    勤怠ログをすべて削除（ヘッダー以外）
    """
    worksheet = get_worksheet(spreadsheet_id, "attendance_logs")
    if worksheet is None:
        return False
    
    try:
        # 全データを取得
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:  # ヘッダーのみ
            return True
        
        # ヘッダー以外の行を削除（2行目から最後まで）
        worksheet.delete_rows(2, len(all_values))
        # キャッシュをクリア
        read_attendance_logs.clear()
        return True
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"勤怠ログの削除に失敗しました: {e}")
        return False


def delete_all_events(spreadsheet_id: str) -> bool:
    """
    イベントをすべて削除（ヘッダー以外）
    """
    worksheet = get_worksheet(spreadsheet_id, "events")
    if worksheet is None:
        return False
    
    try:
        # 全データを取得
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:  # ヘッダーのみ
            return True
        
        # ヘッダー以外の行を削除（2行目から最後まで）
        worksheet.delete_rows(2, len(all_values))
        # キャッシュをクリア
        read_events.clear()
        return True
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"イベントの削除に失敗しました: {e}")
        return False
