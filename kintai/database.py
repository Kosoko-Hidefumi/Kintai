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
            return pd.DataFrame(columns=["post_id", "timestamp", "author", "title", "content"])
        
        df = pd.DataFrame(data)
        
        # 列名の前後の空白を削除
        df.columns = df.columns.str.strip()
        
        # post_id列がない場合は追加（既存データ対応）
        if "post_id" not in df.columns:
            import uuid
            df["post_id"] = [str(uuid.uuid4()) for _ in range(len(df))]
        
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
            headers = ["post_id", "timestamp", "author", "title", "content"]
            worksheet.append_row(headers)
        
        # post_idを追加（UUIDを使用）
        import uuid
        if "post_id" not in post_data:
            post_data["post_id"] = str(uuid.uuid4())
        
        # データを追加
        row = [
            post_data.get("post_id", ""),
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


def delete_bulletin_post(spreadsheet_id: str, post_id: str) -> bool:
    """
    指定されたpost_idを持つ投稿を削除
    """
    worksheet = get_worksheet(spreadsheet_id, "bulletin_board")
    if worksheet is None:
        return False
    
    try:
        # 全データを取得
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:  # ヘッダーのみ
            return False
        
        # post_idが一致する行を探して削除
        for i in range(len(all_values) - 1, 0, -1):  # 最後の行から2行目まで
            row = all_values[i]
            if len(row) > 0 and row[0] == post_id:  # post_idは最初の列
                worksheet.delete_rows(i + 1)  # 1-indexed
                # キャッシュをクリア
                read_bulletin_board.clear()
                return True
        
        return False
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"投稿の削除に失敗しました: {e}")
        return False


def update_bulletin_post(spreadsheet_id: str, post_id: str, post_data: Dict[str, Any]) -> bool:
    """
    指定されたpost_idを持つ投稿を更新
    """
    worksheet = get_worksheet(spreadsheet_id, "bulletin_board")
    if worksheet is None:
        return False
    
    try:
        # 全データを取得
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:  # ヘッダーのみ
            return False
        
        # post_idが一致する行を探して更新
        for i in range(1, len(all_values)):  # 2行目から（ヘッダーをスキップ）
            row = all_values[i]
            if len(row) > 0 and row[0] == post_id:  # post_idは最初の列
                # 行を更新（post_idは変更しない）
                updated_row = [
                    post_id,  # post_idは維持
                    post_data.get("timestamp", row[1] if len(row) > 1 else ""),
                    post_data.get("author", row[2] if len(row) > 2 else ""),
                    post_data.get("title", row[3] if len(row) > 3 else ""),
                    post_data.get("content", row[4] if len(row) > 4 else "")
                ]
                worksheet.update(f"A{i+1}:E{i+1}", [updated_row])  # 1-indexed
                # キャッシュをクリア
                read_bulletin_board.clear()
                return True
        
        return False
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"投稿の更新に失敗しました: {e}")
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
            return pd.DataFrame(columns=["event_id", "start_date", "end_date", "title", "description", "color", "start_time", "end_time"])
        df = pd.DataFrame(data)
        # 列名の前後の空白を除去
        df.columns = df.columns.str.strip()
        # 列名から特殊文字（|など）を除去して正規化
        # "end_date |" -> "end_date" のように変換
        df.columns = [col.replace("|", "").strip() for col in df.columns]
        # 文字列型の列の値の前後の空白を除去
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
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
            headers = ["event_id", "start_date", "end_date", "title", "description", "color", "start_time", "end_time"]
            worksheet.append_row(headers)
        else:
            # 既存のヘッダーを確認して、start_timeとend_timeがなければ追加
            headers = existing_data[0]
            headers_updated = False
            if "start_time" not in headers:
                headers.append("start_time")
                headers_updated = True
            if "end_time" not in headers:
                headers.append("end_time")
                headers_updated = True
            
            if headers_updated:
                # ヘッダー行を更新
                header_range = f"A1:{chr(64 + len(headers))}1"
                worksheet.update(header_range, [headers])
        
        # データを追加（ヘッダーの数に合わせて）
        row = [
            event_data.get("event_id", ""),
            event_data.get("start_date", ""),
            event_data.get("end_date", ""),
            event_data.get("title", ""),
            event_data.get("description", ""),
            event_data.get("color", "#95A5A6")
        ]
        
        # start_timeとend_timeがヘッダーにある場合は追加
        current_headers = worksheet.row_values(1) if existing_data else headers
        if "start_time" in current_headers:
            row.append(event_data.get("start_time", ""))
        if "end_time" in current_headers:
            row.append(event_data.get("end_time", ""))
        
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


def delete_all_bulletin_posts(spreadsheet_id: str) -> bool:
    """
    掲示板の投稿をすべて削除（ヘッダー以外）
    """
    worksheet = get_worksheet(spreadsheet_id, "bulletin_board")
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
        st.error(f"掲示板投稿の削除に失敗しました: {e}")
        return False


def delete_attendance_log(spreadsheet_id: str, event_id: str) -> bool:
    """
    指定されたevent_idを持つ勤怠ログをすべて削除（複数日の場合も対応）
    """
    worksheet = get_worksheet(spreadsheet_id, "attendance_logs")
    if worksheet is None:
        return False
    
    try:
        # 全データを取得
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:  # ヘッダーのみ
            return False
        
        # event_idが一致する行を後ろから削除（インデックスがずれないように）
        deleted_count = 0
        for i in range(len(all_values) - 1, 0, -1):  # 最後の行から2行目まで
            row = all_values[i]
            if len(row) > 0 and row[0] == event_id:  # event_idは最初の列
                worksheet.delete_rows(i + 1)  # 1-indexed
                deleted_count += 1
        
        if deleted_count > 0:
            # キャッシュをクリア
            read_attendance_logs.clear()
            return True
        return False
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


def update_attendance_logs(spreadsheet_id: str, event_id: str, log_data: Dict[str, Any]) -> bool:
    """
    指定されたevent_idを持つ勤怠ログを更新
    複数日の場合は、すべての日を削除してから再登録
    """
    # 既存のデータを削除
    if not delete_attendance_log(spreadsheet_id, event_id):
        return False
    
    # 新しいデータを登録（複数日の場合は呼び出し側で対応）
    return write_attendance_log(spreadsheet_id, log_data)


def delete_event(spreadsheet_id: str, event_id: str) -> bool:
    """
    指定されたevent_idを持つイベントを削除
    """
    worksheet = get_worksheet(spreadsheet_id, "events")
    if worksheet is None:
        return False
    
    try:
        # 全データを取得
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:  # ヘッダーのみ
            return False
        
        # event_idが一致する行を探して削除
        for i in range(len(all_values) - 1, 0, -1):  # 最後の行から2行目まで
            row = all_values[i]
            if len(row) > 0 and row[0] == event_id:  # event_idは最初の列
                worksheet.delete_rows(i + 1)  # 1-indexed
                # キャッシュをクリア
                read_events.clear()
                return True
        
        return False
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


def update_event(spreadsheet_id: str, event_id: str, event_data: Dict[str, Any]) -> bool:
    """
    指定されたevent_idを持つイベントを更新
    """
    # 既存のイベントを削除
    if not delete_event(spreadsheet_id, event_id):
        return False
    
    # 新しいデータを登録
    return write_event(spreadsheet_id, event_data)


# ========== 職員管理機能 ==========

@st.cache_data(ttl=60)
def read_staff(spreadsheet_id: str) -> pd.DataFrame:
    """
    職員シートからデータを読み込む
    
    Returns:
        pd.DataFrame: 職員データ（カラム: staff_id, name, password）
    """
    worksheet = get_worksheet(spreadsheet_id, "staff")
    if worksheet is None:
        return pd.DataFrame()
    
    try:
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # カラム名の空白を除去
        if not df.empty:
            df.columns = df.columns.str.strip()
            
            # 各カラムの値も文字列の場合はトリミング
            for col in df.columns:
                if df[col].dtype == 'object':  # 文字列型の場合
                    df[col] = df[col].astype(str).str.strip()
        
        return df
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"職員データの読み込みに失敗しました: {e}")
        return pd.DataFrame()


def write_staff(spreadsheet_id: str, staff_data: Dict[str, Any]) -> bool:
    """
    職員シートにデータを追加
    
    Args:
        spreadsheet_id: スプレッドシートID
        staff_data: 職員データ（staff_id, name, password）
    
    Returns:
        bool: 成功時True、失敗時False
    """
    worksheet = get_worksheet(spreadsheet_id, "staff")
    if worksheet is None:
        return False
    
    try:
        # データを行として追加
        row = [
            staff_data.get("staff_id", ""),
            staff_data.get("name", ""),
            staff_data.get("password", "")
        ]
        worksheet.append_row(row)
        
        # キャッシュをクリア
        read_staff.clear()
        return True
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"職員データの保存に失敗しました: {e}")
        return False


def delete_staff(spreadsheet_id: str, staff_id: str) -> bool:
    """
    指定されたstaff_idを持つ職員を削除
    
    Args:
        spreadsheet_id: スプレッドシートID
        staff_id: 職員ID
    
    Returns:
        bool: 成功時True、失敗時False
    """
    worksheet = get_worksheet(spreadsheet_id, "staff")
    if worksheet is None:
        return False
    
    try:
        # 全データを取得
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:  # ヘッダーのみ
            return False
        
        # staff_idが一致する行を探して削除
        for i in range(len(all_values) - 1, 0, -1):  # 最後の行から2行目まで
            row = all_values[i]
            if len(row) > 0 and row[0] == staff_id:  # staff_idは最初の列
                worksheet.delete_rows(i + 1)  # 1-indexed
                # キャッシュをクリア
                read_staff.clear()
                return True
        
        return False
    except APIError as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            st.error("⚠️ APIのレート制限に達しました。しばらく待ってから再度お試しください。")
            st.info("💡 ヒント: 1〜2分待ってから再度お試しください。")
        else:
            st.error(f"APIエラーが発生しました: {e}")
        return False
    except Exception as e:
        st.error(f"職員の削除に失敗しました: {e}")
        return False


def update_staff(spreadsheet_id: str, staff_id: str, staff_data: Dict[str, Any]) -> bool:
    """
    指定されたstaff_idを持つ職員情報を更新
    
    Args:
        spreadsheet_id: スプレッドシートID
        staff_id: 職員ID
        staff_data: 更新する職員データ
    
    Returns:
        bool: 成功時True、失敗時False
    """
    # 既存の職員を削除
    if not delete_staff(spreadsheet_id, staff_id):
        return False
    
    # 新しいデータを登録
    return write_staff(spreadsheet_id, staff_data)
