"""
職場勤怠管理・掲示板アプリ
Streamlitを使用した職員5名向けの勤怠管理と情報共有アプリケーション
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
from streamlit_calendar import calendar
import jpholiday
from database import (
    read_attendance_logs,
    write_attendance_log,
    read_bulletin_board,
    write_bulletin_post,
    delete_bulletin_post,
    update_bulletin_post,
    read_events,
    write_event,
    delete_all_attendance_logs,
    delete_all_events,
    delete_all_bulletin_posts,
    delete_attendance_log,
    update_attendance_logs,
    delete_event,
    update_event,
    read_staff,
    write_staff,
    delete_staff,
    update_staff
)
from utils import (
    calculate_fiscal_year,
    calculate_duration_hours,
    calculate_day_equivalent
)

# ページ設定
st.set_page_config(
    page_title="ハワイ大学システム",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 定数定義
LEAVE_TYPES = ["年休", "夏休み", "代休"]
ADMIN_USER = "管理者"

# 職員リストを動的に取得する関数
def get_staff_list():
    """
    スプレッドシートから職員リストを取得
    データがない場合はデフォルトリストを返す
    """
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        return ["職員A", "職員B", "職員C", "職員D", "職員E"]
    
    try:
        df_staff = read_staff(spreadsheet_id)
        if df_staff.empty:
            return ["職員A", "職員B", "職員C", "職員D", "職員E"]
        
        # name列から職員名のリストを取得
        staff_names = df_staff["name"].tolist()
        return staff_names if staff_names else ["職員A", "職員B", "職員C", "職員D", "職員E"]
    except Exception:
        return ["職員A", "職員B", "職員C", "職員D", "職員E"]

# セッション状態の初期化
if "selected_user" not in st.session_state:
    st.session_state.selected_user = None
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "staff_authenticated" not in st.session_state:
    st.session_state.staff_authenticated = False
if "current_staff_id" not in st.session_state:
    st.session_state.current_staff_id = None

# スプレッドシートIDの初期化（デフォルト値の読み込み）
if "spreadsheet_id" not in st.session_state:
    default_id = ""
    try:
        # secrets.tomlからデフォルト値を読み込む
        if hasattr(st, 'secrets') and "spreadsheet_id" in st.secrets:
            default_id = st.secrets["spreadsheet_id"]
            st.session_state.spreadsheet_id = default_id
        else:
            st.session_state.spreadsheet_id = ""
    except Exception as e:
        # エラーが発生した場合は空文字
        st.session_state.spreadsheet_id = ""


def get_spreadsheet_id():
    """スプレッドシートIDを取得（セッション状態またはデフォルト値）"""
    # デフォルト値の取得
    default_id = ""
    try:
        # secrets.tomlファイルを直接読み込む
        import tomllib
        import os
        secrets_path = os.path.join(".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            with open(secrets_path, "rb") as f:
                secrets_data = tomllib.load(f)
                # ルートレベルから取得を試す
                default_id = secrets_data.get("spreadsheet_id", "")
                # gcp_service_accountセクション内にもある場合（誤って配置された場合）
                if not default_id and "gcp_service_account" in secrets_data:
                    gcp_data = secrets_data["gcp_service_account"]
                    if isinstance(gcp_data, dict) and "spreadsheet_id" in gcp_data:
                        default_id = gcp_data["spreadsheet_id"]
    except Exception as e:
        # エラーが発生した場合も続行
        pass
    
    # セッション状態が空でデフォルト値がある場合、セッション状態を更新
    if not st.session_state.spreadsheet_id and default_id:
        st.session_state.spreadsheet_id = default_id
    
    result = st.session_state.spreadsheet_id or default_id
    return result


def show_calendar_page():
    """カレンダーページを表示"""
    st.header("🗓 カレンダー")
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        st.error("スプレッドシートIDが設定されていません。サイドバーで設定してください。")
        return
    
    # 休暇種別ごとの色設定
    leave_type_colors = {
        "年休": "#FF6B6B",      # 赤
        "夏休み": "#4ECDC4",    # 青緑
        "代休": "#87CEEB"       # 薄い青（スカイブルー）
    }
    
    # 勤怠ログを読み込む
    df_logs = read_attendance_logs(spreadsheet_id)
    
    # イベントデータを読み込む
    df_events = read_events(spreadsheet_id)
    
    if df_logs.empty and df_events.empty:
        st.info("まだ予定が登録されていません。")
        return
    
    # カレンダー用のイベントデータを作成
    calendar_events = []
    
    # 休暇ログを各日ごとに個別のイベントとして変換（グループ化しない）
    if not df_logs.empty:
        # 日付をdatetime型に変換
        df_logs["date"] = pd.to_datetime(df_logs["date"], errors="coerce")
        df_logs = df_logs.sort_values(["staff_name", "type", "date"])
        
        # 各日を個別のイベントとして処理
        for _, row in df_logs.iterrows():
            event_date = row.get("date")
            event_id = row.get("event_id", "")
            staff_name = row.get("staff_name", "")
            leave_type = row.get("type", "")
            start_time = str(row.get("start_time", "")).strip()
            end_time = str(row.get("end_time", "")).strip()
            duration_hours = row.get("duration_hours", 0)
            remarks = row.get("remarks", "")
            
            if pd.isna(event_date):
                continue
            
            event_date_str = event_date.strftime("%Y-%m-%d")
            # FullCalendarではendは終了日の翌日を指定（排他的）
            end_date_str = (event_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            
            # タイトルの生成（時間指定がある場合は時間も表示）
            # 1日休みかどうかを判定（08:30-17:00）
            is_full_day_leave = (start_time == "08:30" and end_time == "17:00")
            
            if is_full_day_leave:
                # 1日休みの場合: 名前 - one day
                title = f"{staff_name} - one day"
            elif start_time and end_time:
                # 時間指定の場合: 名前：開始時間-終了時間
                title = f"{staff_name}：{start_time}-{end_time}"
            else:
                # 時間が設定されていない場合: 名前 - 休暇種別
                title = f"{staff_name} - {leave_type}"
            
            event = {
                "title": title,
                "start": event_date_str,
                "end": end_date_str,
                "allDay": True,  # 終日イベントとして設定
                "color": leave_type_colors.get(leave_type, "#95A5A6"),
                "resource": leave_type,
                "extendedProps": {
                    "event_id": event_id,
                    "staff_name": staff_name,
                    "leave_type": leave_type,
                    "start_date_display": event_date.strftime("%Y年%m月%d日"),
                    "end_date_display": event_date.strftime("%Y年%m月%d日"),
                    "time_range": f"{start_time} - {end_time}" if start_time and end_time else "",
                    "remarks": remarks,
                    "event_type": "attendance"
                }
            }
            calendar_events.append(event)
    
    # イベントをカレンダーイベントに変換（職員名なし、複数日対応）
    for _, row in df_events.iterrows():
        event_id = row.get("event_id", "")
        # 列名にスペースや特殊文字が含まれている可能性があるので、複数のパターンで取得を試みる
        start_date_str = ""
        end_date_str = ""
        
        # start_dateの取得を試みる（列名のバリエーションをチェック）
        for col_name in df_events.columns:
            if "start_date" in col_name.lower():
                val = row.get(col_name)
                if val is not None and str(val).strip() != "" and str(val).strip().lower() != "nan":
                    start_date_str = str(val).strip()
                    break
        
        # end_dateの取得を試みる（列名のバリエーションをチェック）
        # "end_date |" のような特殊文字を含む列名にも対応
        for col_name in df_events.columns:
            if "end_date" in col_name.lower():
                val = row.get(col_name)
                if val is not None and str(val).strip() != "" and str(val).strip().lower() != "nan":
                    end_date_str = str(val).strip()
                    break
        
        title = row.get("title", "")
        description = row.get("description", "")
        color = row.get("color", "#95A5A6")
        start_time = str(row.get("start_time", "")).strip() if row.get("start_time") and str(row.get("start_time")).strip() != "" and str(row.get("start_time")).strip().lower() != "nan" else ""
        end_time = str(row.get("end_time", "")).strip() if row.get("end_time") and str(row.get("end_time")).strip() != "" and str(row.get("end_time")).strip().lower() != "nan" else ""
        
        if not start_date_str:
            continue
        
        # 終了日が設定されていない場合は開始日と同じにする
        if not end_date_str or end_date_str == "" or pd.isna(end_date_str) or end_date_str == "nan":
            end_date_str = start_date_str
        
        # 日付をdatetime型に変換
        try:
            start_date = pd.to_datetime(start_date_str)
            end_date = pd.to_datetime(end_date_str)
            # FullCalendarではendは終了日の翌日を指定（排他的）
            end_date_exclusive = (end_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            start_date_formatted = start_date.strftime("%Y-%m-%d")
            end_date_formatted = end_date.strftime("%Y-%m-%d")
        except Exception as e:
            # 日付の変換に失敗した場合はそのまま使用
            start_date_formatted = start_date_str
            end_date_formatted = end_date_str if end_date_str and end_date_str != "" else start_date_str
            end_date_exclusive = end_date_str if end_date_str and end_date_str != "" else start_date_str
        
        # 時間指定がある場合は時間を計算して判定
        duration_hours = 0
        if start_time and end_time:
            duration_hours = calculate_duration_hours(start_time, end_time)
        
        # タイトルの生成（時間指定がある場合は時間も表示）
        # 1日休み（08:30-17:00）の場合は時間を表示しない
        display_title = title
        if start_time and end_time:
            # 1日休みかどうかを判定（08:30-17:00）
            is_full_day_event = (start_time == "08:30" and end_time == "17:00")
            
            if not is_full_day_event:
                try:
                    duration_float = float(duration_hours)
                    is_partial_day = (duration_float < 8.0)
                except (ValueError, TypeError):
                    is_partial_day = False
                
                if is_partial_day:
                    # 時間指定の場合: イベント名：開始時間-終了時間
                    display_title = f"{title}：{start_time}-{end_time}"
        
        # イベントオブジェクトを作成（複数日対応）
        event = {
            "title": display_title,
            "start": start_date_formatted,
            "end": end_date_exclusive,
            "allDay": True,  # 終日イベントとして設定
            "color": color,
            "resource": "event",
            "extendedProps": {
                "event_id": event_id,
                "start_date": start_date_formatted,
                "end_date": end_date_formatted,  # 変換後の日付を使用
                "event_title": title,
                "description": description,
                "event_color": color,
                "time_range": f"{start_time} - {end_time}" if start_time and end_time else "",
                "event_type": "general_event"
            }
        }
        calendar_events.append(event)
    
    # 日本の祝日を追加（前後1年分）
    today = date.today()
    start_range = date(today.year - 1, 1, 1)
    end_range = date(today.year + 1, 12, 31)
    
    current_date = start_range
    while current_date <= end_range:
        holiday_name = jpholiday.is_holiday_name(current_date)
        if holiday_name:
            holiday_event = {
                "title": f"🎌 {holiday_name}",
                "start": current_date.strftime("%Y-%m-%d"),
                "end": (current_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                "allDay": True,
                "color": "#FFB6C1",  # 淡いピンク色（祝日背景）
                "textColor": "#000000",  # 文字色を黒に
                "resource": "holiday",
                "extendedProps": {
                    "holiday_name": holiday_name,
                    "event_type": "holiday"
                }
            }
            calendar_events.append(holiday_event)
        current_date += timedelta(days=1)
    
    # カレンダー表示オプション
    calendar_options = {
        "editable": False,
        "navLinks": True,
        "dayMaxEvents": True,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "initialView": "dayGridMonth",
        "locale": "ja",
        "height": "auto"
    }
    
    # カレンダーを表示
    calendar_result = calendar(
        events=calendar_events,
        options=calendar_options,
        custom_css="""
        .fc-event-title {
            white-space: normal;
            word-wrap: break-word;
        }
        """
    )
    
    # イベントクリック時の詳細表示と編集・削除機能
    if calendar_result and "eventClick" in calendar_result:
        clicked_event = calendar_result["eventClick"]["event"]
        event_type = clicked_event.get('extendedProps', {}).get('event_type', '')
        event_id = clicked_event.get('extendedProps', {}).get('event_id', '')
        
        # 祝日の場合は詳細表示のみ
        if event_type == "holiday":
            holiday_name = clicked_event.get('extendedProps', {}).get('holiday_name', '祝日')
            st.info(f"🎌 **{holiday_name}**")
        
        # 休暇申請の場合
        elif event_type == "attendance" and event_id:
            st.markdown("---")
            st.subheader("📝 休暇申請の詳細")
            
            staff_name = clicked_event.get('extendedProps', {}).get('staff_name', '不明')
            leave_type = clicked_event.get('extendedProps', {}).get('leave_type', '不明')
            start_date_display = clicked_event.get('extendedProps', {}).get('start_date_display', '不明')
            end_date_display = clicked_event.get('extendedProps', {}).get('end_date_display', '不明')
            time_range = clicked_event.get('extendedProps', {}).get('time_range', '不明')
            remarks = clicked_event.get('extendedProps', {}).get('remarks', 'なし')
            
            # 期間の表示
            if start_date_display == end_date_display:
                period_display = start_date_display
            else:
                period_display = f"{start_date_display} 〜 {end_date_display}"
            
            # 編集モードでない場合は詳細表示
            if not st.session_state.get(f"editing_calendar_attendance_{event_id}", False):
                st.info(f"""
                **職員**: {staff_name}  
                **休暇種別**: {leave_type}  
                **期間**: {period_display}  
                **時間**: {time_range}  
                **備考**: {remarks}
                """)
                
                # 編集・削除ボタン（管理者または本人のみ）
                can_edit = (st.session_state.selected_user == ADMIN_USER and st.session_state.admin_authenticated) or \
                           (st.session_state.selected_user == staff_name)
                
                st.markdown("---")
                if can_edit:
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("✏️ 編集", key=f"edit_cal_att_{event_id}", type="secondary"):
                            st.session_state[f"editing_calendar_attendance_{event_id}"] = True
                            st.rerun()
                    with col2:
                        if st.button("🗑️ 削除", key=f"del_att_{event_id}", type="secondary"):
                            spreadsheet_id = get_spreadsheet_id()
                            if spreadsheet_id and delete_attendance_log(spreadsheet_id, event_id):
                                st.success("✅ 休暇申請を削除しました。")
                                st.rerun()
                            else:
                                st.error("❌ 削除に失敗しました。")
                else:
                    st.warning("この休暇申請を編集・削除できるのは、本人または管理者のみです。")
            
            # 編集フォーム
            else:
                st.markdown("#### 休暇申請を編集")
                
                # 既存の休暇申請データを取得
                spreadsheet_id = get_spreadsheet_id()
                df_logs = read_attendance_logs(spreadsheet_id)
                attendance_row = df_logs[df_logs["event_id"] == event_id]
                
                if attendance_row.empty:
                    st.error("休暇申請データが見つかりません。")
                    del st.session_state[f"editing_calendar_attendance_{event_id}"]
                    st.rerun()
                else:
                    # 既存データを取得
                    existing_row = attendance_row.iloc[0]
                    edit_start_date_str = existing_row.get("date", "")
                    edit_leave_type = existing_row.get("type", leave_type)
                    edit_start_time_str = existing_row.get("start_time", "")
                    edit_end_time_str = existing_row.get("end_time", "")
                    edit_remarks = existing_row.get("remarks", "")
                    
                    # 日付の初期値を取得
                    try:
                        edit_start_date = pd.to_datetime(edit_start_date_str).date()
                    except:
                        edit_start_date = date.today()
                    
                    # 日付選択（フォームの外で）
                    col_date1, col_date2 = st.columns(2)
                    with col_date1:
                        edit_start = st.date_input("開始日", value=edit_start_date, key=f"cal_edit_att_start_{event_id}")
                    with col_date2:
                        edit_end = st.date_input("終了日", 
                                                value=edit_start,
                                                min_value=edit_start,
                                                key=f"cal_edit_att_end_{event_id}",
                                                help="複数日にまたがる場合は終了日を設定してください")
                    
                    # 時間の初期値を取得
                    try:
                        edit_start_time = datetime.strptime(edit_start_time_str, "%H:%M").time()
                    except:
                        edit_start_time = datetime.strptime("08:30", "%H:%M").time()
                    
                    try:
                        edit_end_time = datetime.strptime(edit_end_time_str, "%H:%M").time()
                    except:
                        edit_end_time = datetime.strptime("17:00", "%H:%M").time()
                    
                    # その他の項目はフォーム内で
                    with st.form(f"cal_edit_attendance_form_{event_id}"):
                        edit_leave_type_input = st.selectbox(
                            "休暇種別",
                            options=["年休", "夏休み", "代休"],
                            index=["年休", "夏休み", "代休"].index(edit_leave_type) if edit_leave_type in ["年休", "夏休み", "代休"] else 0
                        )
                        
                        # 時間入力
                        col_time1, col_time2 = st.columns(2)
                        with col_time1:
                            edit_start_time_input = st.time_input("開始時間", value=edit_start_time, key=f"cal_edit_att_start_time_{event_id}")
                        with col_time2:
                            edit_end_time_input = st.time_input("終了時間", value=edit_end_time, key=f"cal_edit_att_end_time_{event_id}")
                        
                        edit_remarks_input = st.text_area("備考", value=edit_remarks if edit_remarks != 'なし' else '', height=100)
                        
                        col_submit, col_cancel = st.columns([1, 3])
                        with col_submit:
                            submitted = st.form_submit_button("更新", type="primary")
                        
                        if submitted:
                            if edit_end < edit_start:
                                st.error("終了日は開始日以降を選択してください。")
                            else:
                                # 既存の休暇申請を削除
                                if delete_attendance_log(spreadsheet_id, event_id):
                                    # 新しい日付範囲で休暇申請を再登録
                                    current_date = edit_start
                                    success_count = 0
                                    
                                    while current_date <= edit_end:
                                        # 時間計算
                                        start_str = edit_start_time_input.strftime("%H:%M")
                                        end_str = edit_end_time_input.strftime("%H:%M")
                                        duration_hours = calculate_duration_hours(start_str, end_str)
                                        day_equivalent = calculate_day_equivalent(duration_hours)
                                        fiscal_year = calculate_fiscal_year(current_date)
                                        
                                        # ログデータを作成
                                        log_data = {
                                            "event_id": str(uuid.uuid4()),
                                            "date": current_date.strftime("%Y-%m-%d"),
                                            "staff_name": staff_name,
                                            "type": edit_leave_type_input,
                                            "start_time": start_str,
                                            "end_time": end_str,
                                            "duration_hours": duration_hours,
                                            "day_equivalent": day_equivalent,
                                            "fiscal_year": fiscal_year,
                                            "remarks": edit_remarks_input
                                        }
                                        
                                        if write_attendance_log(spreadsheet_id, log_data):
                                            success_count += 1
                                        
                                        current_date += timedelta(days=1)
                                    
                                    if success_count == (edit_end - edit_start).days + 1:
                                        st.success("✅ 休暇申請を更新しました。")
                                        del st.session_state[f"editing_calendar_attendance_{event_id}"]
                                        st.rerun()
                                    else:
                                        st.error("❌ 更新に失敗しました。")
                                else:
                                    st.error("❌ 既存の休暇申請の削除に失敗しました。")
                        
                        with col_cancel:
                            if st.form_submit_button("キャンセル"):
                                del st.session_state[f"editing_calendar_attendance_{event_id}"]
                                st.rerun()
        
        # 一般イベントの場合
        elif event_type == "general_event" and event_id:
            st.markdown("---")
            st.subheader("📅 イベントの詳細")
            
            event_title = clicked_event.get('extendedProps', {}).get('event_title', '不明')
            start_date_str = clicked_event.get('extendedProps', {}).get('start_date', '')
            end_date_str = clicked_event.get('extendedProps', {}).get('end_date', '')
            event_color = clicked_event.get('extendedProps', {}).get('event_color', '#4285F4')
            description = clicked_event.get('extendedProps', {}).get('description', 'なし')
            time_range = clicked_event.get('extendedProps', {}).get('time_range', '')
            
            # 日付のフォーマット
            try:
                # 空文字列やNoneの場合は開始日を使用
                if not end_date_str or end_date_str == "" or pd.isna(end_date_str) or end_date_str == "nan":
                    end_date_str = start_date_str
                
                start_date_display = pd.to_datetime(start_date_str).strftime("%Y年%m月%d日")
                end_date_display = pd.to_datetime(end_date_str).strftime("%Y年%m月%d日")
                if start_date_display == end_date_display:
                    period_display = start_date_display
                else:
                    period_display = f"{start_date_display} 〜 {end_date_display}"
            except Exception as e:
                # エラーの場合は開始日のみ表示
                try:
                    start_date_display = pd.to_datetime(start_date_str).strftime("%Y年%m月%d日")
                    period_display = start_date_display
                except:
                    period_display = "不明"
            
            # 編集モードでない場合は詳細表示
            if not st.session_state.get(f"editing_calendar_event_{event_id}", False):
                # 1日（08:30-17:00）の場合は時間を表示しない
                is_full_day_event = (time_range == "08:30 - 17:00")
                time_info = f"**時間**: {time_range}" if time_range and not is_full_day_event else ""
                st.info(f"""
                **イベント名**: {event_title}  
                **期間**: {period_display}  
                {time_info}
                **説明**: {description}
                """)
                
                # 編集・削除ボタン
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    if st.button("✏️ 編集", key=f"edit_cal_evt_{event_id}", type="secondary"):
                        st.session_state[f"editing_calendar_event_{event_id}"] = True
                        st.rerun()
                with col2:
                    if st.button("🗑️ 削除", key=f"del_evt_{event_id}", type="secondary"):
                        spreadsheet_id = get_spreadsheet_id()
                        if spreadsheet_id and delete_event(spreadsheet_id, event_id):
                            st.success("✅ イベントを削除しました。")
                            st.rerun()
                        else:
                            st.error("❌ 削除に失敗しました。")
            
            # 編集フォーム
            else:
                st.markdown("#### イベントを編集")
                
                # 日付の初期値を取得
                try:
                    edit_start_date = pd.to_datetime(start_date_str).date()
                except:
                    edit_start_date = date.today()
                
                try:
                    edit_end_date = pd.to_datetime(end_date_str).date()
                except:
                    edit_end_date = date.today()
                
                # 日付選択（フォームの外で）
                col_date1, col_date2 = st.columns(2)
                with col_date1:
                    edit_start = st.date_input("開始日", value=edit_start_date, key=f"cal_edit_start_{event_id}")
                with col_date2:
                    edit_end = st.date_input("終了日", 
                                            value=max(edit_end_date, edit_start),
                                            min_value=edit_start,
                                            key=f"cal_edit_end_{event_id}")
                
                # 時間の初期値を取得
                edit_start_time_str = time_range.split(" - ")[0] if time_range and " - " in time_range else "08:30"
                edit_end_time_str = time_range.split(" - ")[1] if time_range and " - " in time_range else "17:00"
                
                try:
                    edit_start_time = datetime.strptime(edit_start_time_str, "%H:%M").time()
                except:
                    edit_start_time = datetime.strptime("08:30", "%H:%M").time()
                
                try:
                    edit_end_time = datetime.strptime(edit_end_time_str, "%H:%M").time()
                except:
                    edit_end_time = datetime.strptime("17:00", "%H:%M").time()
                
                # その他の項目はフォーム内で
                with st.form(f"cal_edit_event_form_{event_id}"):
                    col_edit1, col_edit2 = st.columns(2)
                    with col_edit1:
                        edit_title = st.text_input("イベント名", value=event_title)
                    with col_edit2:
                        edit_color = st.color_picker("色", value=event_color)
                    
                    # 時間入力
                    col_time1, col_time2 = st.columns(2)
                    with col_time1:
                        edit_start_time_input = st.time_input("開始時間", value=edit_start_time)
                    with col_time2:
                        edit_end_time_input = st.time_input("終了時間", value=edit_end_time)
                    
                    edit_description = st.text_area("説明", value=description if description != 'なし' else '', height=100)
                    
                    col_submit, col_cancel = st.columns([1, 3])
                    with col_submit:
                        submitted = st.form_submit_button("更新", type="primary")
                    
                    if submitted:
                        if not edit_title:
                            st.warning("イベント名を入力してください。")
                        elif edit_end < edit_start:
                            st.error("終了日は開始日以降を選択してください。")
                        else:
                            spreadsheet_id = get_spreadsheet_id()
                            updated_data = {
                                "event_id": event_id,
                                "start_date": edit_start.strftime("%Y-%m-%d"),
                                "end_date": edit_end.strftime("%Y-%m-%d"),
                                "title": edit_title,
                                "description": edit_description,
                                "color": edit_color,
                                "start_time": edit_start_time_input.strftime("%H:%M"),
                                "end_time": edit_end_time_input.strftime("%H:%M")
                            }
                            if spreadsheet_id and update_event(spreadsheet_id, event_id, updated_data):
                                st.success("✅ イベントを更新しました。")
                                del st.session_state[f"editing_calendar_event_{event_id}"]
                                st.rerun()
                            else:
                                st.error("❌ 更新に失敗しました。")
                
                # キャンセルボタン
                if st.button("キャンセル", key=f"cal_cancel_event_{event_id}"):
                    del st.session_state[f"editing_calendar_event_{event_id}"]
                    st.rerun()
    
    # 凡例を表示
    st.markdown("---")
    st.subheader("凡例")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div style="background-color: {leave_type_colors["年休"]}; padding: 10px; border-radius: 5px; color: white; text-align: center;"><strong>年休</strong></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="background-color: {leave_type_colors["夏休み"]}; padding: 10px; border-radius: 5px; color: white; text-align: center;"><strong>夏休み</strong></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="background-color: {leave_type_colors["代休"]}; padding: 10px; border-radius: 5px; color: white; text-align: center;"><strong>代休</strong></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div style="background-color: #FFB6C1; padding: 10px; border-radius: 5px; color: black; text-align: center;"><strong>🎌 祝日</strong></div>', unsafe_allow_html=True)


def show_leave_application_page():
    """休暇申請ページを表示"""
    st.header("📝 休暇申請")
    
    if st.session_state.selected_user is None or st.session_state.selected_user == ADMIN_USER:
        st.warning("職員を選択してください。")
        return
    
    # 日付選択（フォームの外で、リアルタイムに連動させる）
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日", value=date.today(), key="leave_start_date")
    with col2:
        end_date = st.date_input("終了日", 
                                 value=start_date,
                                 min_value=start_date,
                                 key="leave_end_date",
                                 help="複数日にまたがる場合は終了日を設定してください")
    
    # 時間入力タイプの選択
    st.markdown("### 休暇時間の設定")
    
    time_input_type = st.radio(
        "時間の入力方法",
        options=["1日休み（8時間）", "時間を指定"],
        index=0,
        horizontal=True,
        help="1日休みは08:30-17:00で自動計算されます",
        key="time_input_type_leave"
    )
    
    is_full_day = (time_input_type == "1日休み（8時間）")
    
    if is_full_day:
        st.info("🕐 時間: 08:30 - 17:00")
    else:
        st.info("🕐 開始時間と終了時間を指定してください")
    
    st.markdown("---")
    
    with st.form("leave_application_form"):
        col1, col2 = st.columns(2)
        
        STAFF_MEMBERS = get_staff_list()
        
        with col1:
            staff_name = st.selectbox("職員名", STAFF_MEMBERS, 
                                     index=STAFF_MEMBERS.index(st.session_state.selected_user) 
                                     if st.session_state.selected_user in STAFF_MEMBERS else 0)
            leave_type = st.selectbox("休暇種別", LEAVE_TYPES)
        
        with col2:
            if not is_full_day:
                start_time = st.time_input("開始時間", value=datetime.strptime("08:30", "%H:%M").time())
                end_time = st.time_input("終了時間", value=datetime.strptime("17:00", "%H:%M").time())
            else:
                # 1日休みの場合は固定値
                start_time = datetime.strptime("08:30", "%H:%M").time()
                end_time = datetime.strptime("17:00", "%H:%M").time()
                st.write("")  # スペース調整
        
        remarks = st.text_area("備考", height=100)
        
        submitted = st.form_submit_button("申請を送信", type="primary")
        
        if submitted:
            # 1日休みの場合は時間を強制的に08:30-17:00に設定
            if is_full_day:
                start_time = datetime.strptime("08:30", "%H:%M").time()
                end_time = datetime.strptime("17:00", "%H:%M").time()
            
            # 日付の妥当性チェック
            if end_date < start_date:
                st.error("❌ 終了日は開始日以降を選択してください。")
                return
            
            spreadsheet_id = get_spreadsheet_id()
            if not spreadsheet_id:
                st.error("スプレッドシートIDが設定されていません。サイドバーで設定してください。")
                return
            
            # 開始日から終了日までの各日について登録
            current_date = start_date
            success_count = 0
            total_days = (end_date - start_date).days + 1
            total_day_equivalent = 0.0  # 実際の取得日数を合計
            
            while current_date <= end_date:
                # 時間計算
                start_str = start_time.strftime("%H:%M")
                end_str = end_time.strftime("%H:%M")
                duration_hours = calculate_duration_hours(start_str, end_str)
                day_equivalent = calculate_day_equivalent(duration_hours)
                fiscal_year = calculate_fiscal_year(current_date)
                
                # 実際の取得日数を累積
                total_day_equivalent += day_equivalent
                
                # ログデータを作成
                log_data = {
                    "event_id": str(uuid.uuid4()),
                    "date": current_date.strftime("%Y-%m-%d"),
                    "staff_name": staff_name,
                    "type": leave_type,
                    "start_time": start_str,
                    "end_time": end_str,
                    "duration_hours": duration_hours,
                    "day_equivalent": day_equivalent,
                    "fiscal_year": fiscal_year,
                    "remarks": remarks
                }
                
                # データベースに保存
                if write_attendance_log(spreadsheet_id, log_data):
                    success_count += 1
                
                # 次の日へ
                current_date += timedelta(days=1)
            
            if success_count == total_days:
                st.success("✅ 休暇申請が正常に登録されました！")
                st.balloons()
            elif success_count > 0:
                st.warning(f"一部の登録に失敗しました。（成功: {success_count}/{total_days}）")
            else:
                st.error("休暇申請の登録に失敗しました。")


def show_events_page():
    """イベントページを表示"""
    st.header("📅 イベント")
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        st.error("スプレッドシートIDが設定されていません。サイドバーで設定してください。")
        return
    
    # イベント登録フォーム
    with st.expander("📝 新しいイベントを登録", expanded=False):
        # 日付選択（フォームの外で、リアルタイムに連動させる）
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", value=date.today(), key="event_start_date")
        with col2:
            end_date = st.date_input("終了日", 
                                     value=start_date,
                                     min_value=start_date,
                                     key="event_end_date",
                                     help="複数日にまたがる場合は終了日を設定してください")
        
        # 時間入力タイプの選択
        st.markdown("### 時間の設定")
        
        event_time_input_type = st.radio(
            "時間の入力方法",
            options=["1日", "時間を指定"],
            index=0,
            horizontal=True,
            help="1日は08:30-17:00で自動計算されます",
            key="event_time_input_type"
        )
        
        is_event_full_day = (event_time_input_type == "1日")
        
        if is_event_full_day:
            st.info("🕐 時間: 08:30 - 17:00")
        else:
            st.info("🕐 開始時間と終了時間を指定してください")
        
        st.markdown("---")
        
        with st.form("event_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                event_title = st.text_input("イベント名", placeholder="例: 会議、研修、イベントなど")
            
            with col2:
                event_color = st.color_picker("色", value="#4285F4", help="カレンダーでの表示色を選択")
            
            # 時間入力
            if not is_event_full_day:
                col3, col4 = st.columns(2)
                with col3:
                    event_start_time = st.time_input("開始時間", value=datetime.strptime("08:30", "%H:%M").time())
                with col4:
                    event_end_time = st.time_input("終了時間", value=datetime.strptime("17:00", "%H:%M").time())
            else:
                # 1日休みの場合は固定値
                event_start_time = datetime.strptime("08:30", "%H:%M").time()
                event_end_time = datetime.strptime("17:00", "%H:%M").time()
            
            description = st.text_area("説明", height=100, placeholder="イベントの詳細や備考")
            
            submitted = st.form_submit_button("イベントを登録", type="primary")
            
            if submitted:
                if not event_title:
                    st.warning("イベント名を入力してください。")
                elif end_date < start_date:
                    st.error("❌ 終了日は開始日以降を選択してください。")
                else:
                    # 1日休みの場合は時間を強制的に08:30-17:00に設定
                    if is_event_full_day:
                        event_start_time = datetime.strptime("08:30", "%H:%M").time()
                        event_end_time = datetime.strptime("17:00", "%H:%M").time()
                    
                    event_data = {
                        "event_id": str(uuid.uuid4()),
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "title": event_title,
                        "description": description,
                        "color": event_color,
                        "start_time": event_start_time.strftime("%H:%M"),
                        "end_time": event_end_time.strftime("%H:%M")
                    }
                    
                    if write_event(spreadsheet_id, event_data):
                        st.success("イベントが登録されました！")
                        st.rerun()
                    else:
                        st.error("イベントの登録に失敗しました。")
    
    # イベント一覧表示
    st.subheader("イベント一覧")
    df = read_events(spreadsheet_id)
    
    if df.empty:
        st.info("まだイベントが登録されていません。")
    else:
        # 日付順にソート
        if "start_date" in df.columns:
            df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
            df = df.sort_values("start_date")
        
        # カード型レイアウトで表示
        for idx, row in df.iterrows():
            event_id = row.get('event_id', '')
            
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([4, 1])
                with col1:
                    start_d = row.get("start_date", "")
                    end_d = row.get("end_date", "")
                    
                    # 日付のフォーマット処理
                    try:
                        if pd.notna(start_d):
                            if isinstance(start_d, str):
                                start_date_obj = pd.to_datetime(start_d)
                            elif hasattr(start_d, 'strftime'):
                                start_date_obj = start_d
                            else:
                                start_date_obj = pd.to_datetime(str(start_d))
                            start_d_formatted = start_date_obj.strftime("%Y年%m月%d日")
                        else:
                            start_d_formatted = "不明"
                            
                        if pd.notna(end_d):
                            if isinstance(end_d, str):
                                end_date_obj = pd.to_datetime(end_d)
                            elif hasattr(end_d, 'strftime'):
                                end_date_obj = end_d
                            else:
                                end_date_obj = pd.to_datetime(str(end_d))
                            end_d_formatted = end_date_obj.strftime("%Y年%m月%d日")
                        else:
                            end_d_formatted = "不明"
                    except:
                        start_d_formatted = str(start_d) if start_d else "不明"
                        end_d_formatted = str(end_d) if end_d else "不明"
                    
                    # 期間の表示
                    if start_d_formatted == end_d_formatted:
                        date_str = f"{start_d_formatted}"
                    else:
                        date_str = f"{start_d_formatted} 〜 {end_d_formatted}"
                    
                    st.markdown(f"### {row.get('title', 'タイトルなし')}")
                    st.markdown(f"**期間**: {date_str}")
                    # 時間の表示（1日（08:30-17:00）の場合は表示しない）
                    start_time = row.get("start_time", "")
                    end_time = row.get("end_time", "")
                    if start_time and end_time:
                        # 1日休みかどうかを判定（08:30-17:00）
                        is_full_day_event = (str(start_time).strip() == "08:30" and str(end_time).strip() == "17:00")
                        if not is_full_day_event:
                            st.markdown(f"**時間**: {start_time} - {end_time}")
                    if row.get("description"):
                        st.markdown(f"**説明**: {row.get('description')}")
                with col2:
                    color = row.get("color", "#95A5A6")
                    st.markdown(f'<div style="background-color: {color}; padding: 20px; border-radius: 5px; min-height: 50px;"></div>', unsafe_allow_html=True)
                
                # 編集・削除ボタン
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
                with col_btn1:
                    if st.button("✏️ 編集", key=f"edit_event_{event_id}_{idx}", type="secondary"):
                        st.session_state[f"editing_event_{event_id}"] = True
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ 削除", key=f"delete_event_{event_id}_{idx}", type="secondary"):
                        if delete_event(spreadsheet_id, event_id):
                            st.success("イベントを削除しました。")
                            st.rerun()
                        else:
                            st.error("削除に失敗しました。")
                
                # 編集フォーム
                if st.session_state.get(f"editing_event_{event_id}", False):
                    st.markdown("#### イベントを編集")
                    
                    # 日付の初期値を取得
                    try:
                        edit_start_date = pd.to_datetime(row.get('start_date')).date()
                    except:
                        edit_start_date = date.today()
                    
                    try:
                        edit_end_date = pd.to_datetime(row.get('end_date')).date()
                    except:
                        edit_end_date = date.today()
                    
                    # 日付選択（フォームの外で、連動させる）
                    col_date1, col_date2 = st.columns(2)
                    with col_date1:
                        edit_start = st.date_input("開始日", value=edit_start_date, key=f"edit_start_{event_id}_{idx}")
                    with col_date2:
                        edit_end = st.date_input("終了日", 
                                                value=max(edit_end_date, edit_start),
                                                min_value=edit_start,
                                                key=f"edit_end_{event_id}_{idx}")
                    
                    # 時間の初期値を取得
                    edit_start_time_str = row.get("start_time", "08:30")
                    edit_end_time_str = row.get("end_time", "17:00")
                    
                    try:
                        edit_start_time = datetime.strptime(edit_start_time_str, "%H:%M").time()
                    except:
                        edit_start_time = datetime.strptime("08:30", "%H:%M").time()
                    
                    try:
                        edit_end_time = datetime.strptime(edit_end_time_str, "%H:%M").time()
                    except:
                        edit_end_time = datetime.strptime("17:00", "%H:%M").time()
                    
                    # その他の項目はフォーム内で
                    with st.form(f"edit_event_form_{event_id}_{idx}"):
                        col_edit1, col_edit2 = st.columns(2)
                        with col_edit1:
                            edit_title = st.text_input("イベント名", value=row.get('title', ''))
                        with col_edit2:
                            edit_color = st.color_picker("色", value=row.get('color', '#4285F4'))
                        
                        # 時間入力
                        col_time1, col_time2 = st.columns(2)
                        with col_time1:
                            edit_start_time_input = st.time_input("開始時間", value=edit_start_time, key=f"edit_start_time_{event_id}_{idx}")
                        with col_time2:
                            edit_end_time_input = st.time_input("終了時間", value=edit_end_time, key=f"edit_end_time_{event_id}_{idx}")
                        
                        edit_description = st.text_area("説明", value=row.get('description', ''), height=100)
                        
                        col_submit, col_cancel = st.columns([1, 3])
                        with col_submit:
                            submitted = st.form_submit_button("更新", type="primary")
                        
                        if submitted:
                            if not edit_title:
                                st.warning("イベント名を入力してください。")
                            elif edit_end < edit_start:
                                st.error("終了日は開始日以降を選択してください。")
                            else:
                                updated_data = {
                                    "event_id": event_id,
                                    "start_date": edit_start.strftime("%Y-%m-%d"),
                                    "end_date": edit_end.strftime("%Y-%m-%d"),
                                    "title": edit_title,
                                    "description": edit_description,
                                    "color": edit_color,
                                    "start_time": edit_start_time_input.strftime("%H:%M"),
                                    "end_time": edit_end_time_input.strftime("%H:%M")
                                }
                                if update_event(spreadsheet_id, event_id, updated_data):
                                    st.success("イベントを更新しました。")
                                    del st.session_state[f"editing_event_{event_id}"]
                                    st.rerun()
                                else:
                                    st.error("更新に失敗しました。")
                    
                    # キャンセルボタン
                    if st.button("キャンセル", key=f"cancel_event_{event_id}_{idx}"):
                        del st.session_state[f"editing_event_{event_id}"]
                        st.rerun()
                
                st.markdown("")


def show_bulletin_board_page():
    """掲示板ページを表示"""
    st.header("📋 掲示板")
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        st.error("スプレッドシートIDが設定されていません。サイドバーで設定してください。")
        return
    
    # 投稿フォーム
    with st.expander("📝 新しい投稿を作成", expanded=False):
        with st.form("bulletin_post_form"):
            title = st.text_input("タイトル")
            content = st.text_area("本文", height=150)
            submitted = st.form_submit_button("投稿", type="primary")
            
            if submitted:
                if not title or not content:
                    st.warning("タイトルと本文を入力してください。")
                elif st.session_state.selected_user is None:
                    st.warning("ユーザーを選択してください。")
                else:
                    post_data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "author": st.session_state.selected_user,
                        "title": title,
                        "content": content
                    }
                    
                    if write_bulletin_post(spreadsheet_id, post_data):
                        st.success("投稿が完了しました！")
                        st.rerun()
                    else:
                        st.error("投稿に失敗しました。")
    
    # 投稿一覧表示
    st.subheader("投稿一覧")
    df = read_bulletin_board(spreadsheet_id)
    
    if df.empty:
        st.info("まだ投稿がありません。最初の投稿を作成してみましょう！")
    else:
        # カード型レイアウトで表示
        for idx, row in df.iterrows():
            post_id = row.get('post_id', '')
            
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {row.get('title', 'タイトルなし')}")
                    st.markdown(f"{row.get('content', '')}")
                with col2:
                    st.caption(f"**投稿者**: {row.get('author', '不明')}")
                    st.caption(f"**日時**: {row.get('timestamp', '不明')}")
                
                # 編集・削除ボタン
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
                with col_btn1:
                    if st.button("✏️ 編集", key=f"edit_{post_id}_{idx}", type="secondary"):
                        st.session_state[f"editing_{post_id}"] = True
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ 削除", key=f"delete_{post_id}_{idx}", type="secondary"):
                        if delete_bulletin_post(spreadsheet_id, post_id):
                            st.success("投稿を削除しました。")
                            st.rerun()
                        else:
                            st.error("削除に失敗しました。")
                
                # 編集フォーム
                if st.session_state.get(f"editing_{post_id}", False):
                    with st.form(f"edit_form_{post_id}_{idx}"):
                        st.markdown("#### 投稿を編集")
                        edit_title = st.text_input("タイトル", value=row.get('title', ''))
                        edit_content = st.text_area("本文", value=row.get('content', ''), height=150)
                        
                        col_submit, col_cancel = st.columns([1, 3])
                        with col_submit:
                            submitted = st.form_submit_button("更新", type="primary")
                        
                        if submitted:
                            if not edit_title or not edit_content:
                                st.warning("タイトルと本文を入力してください。")
                            else:
                                updated_data = {
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "author": row.get('author', ''),
                                    "title": edit_title,
                                    "content": edit_content
                                }
                                if update_bulletin_post(spreadsheet_id, post_id, updated_data):
                                    st.success("投稿を更新しました。")
                                    del st.session_state[f"editing_{post_id}"]
                                    st.rerun()
                                else:
                                    st.error("更新に失敗しました。")
                    
                    # キャンセルボタン
                    if st.button("キャンセル", key=f"cancel_{post_id}_{idx}"):
                        del st.session_state[f"editing_{post_id}"]
                        st.rerun()
                
                st.markdown("")


def show_admin_dashboard_page():
    """管理者用集計ダッシュボードページを表示"""
    st.header("📈 管理者用集計")
    
    if st.session_state.selected_user != ADMIN_USER or not st.session_state.admin_authenticated:
        st.warning("このページは管理者のみアクセス可能です。管理者として認証してください。")
        return
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        st.error("スプレッドシートIDが設定されていません。サイドバーで設定してください。")
        return
    
    # 年度ごとの休暇残日数集計
    st.subheader("📊 年度ごとの休暇残日数")
    
    # 勤怠ログを取得
    df_logs = read_attendance_logs(spreadsheet_id)
    
    if df_logs.empty:
        st.info("勤怠ログがまだ登録されていません。")
    else:
        # 年度の選択
        current_year = date.today().year
        fiscal_year = calculate_fiscal_year(date.today())
        year_options = list(range(fiscal_year - 2, fiscal_year + 2))
        selected_year = st.selectbox("表示する年度を選択", year_options, index=year_options.index(fiscal_year))
        
        # 選択された年度のデータをフィルタリング
        # 日付から年度を再計算（スプレッドシートのfiscal_year列は使わない）
        df_logs["date"] = pd.to_datetime(df_logs["date"], errors="coerce")
        df_logs["calculated_fiscal_year"] = df_logs["date"].apply(lambda x: calculate_fiscal_year(x.date()) if pd.notna(x) else None)
        df_year = df_logs[df_logs["calculated_fiscal_year"] == selected_year]
        
        if df_year.empty:
            st.warning(f"{selected_year}年度のデータがありません。")
        else:
            # 職員ごと、休暇種別ごとに集計
            df_year["day_equivalent"] = pd.to_numeric(df_year["day_equivalent"], errors="coerce")
            
            # 集計用のデータフレームを作成
            summary_data = []
            
            STAFF_MEMBERS = get_staff_list()
            
            for staff in STAFF_MEMBERS:
                staff_data = df_year[df_year["staff_name"] == staff]
                
                # 各休暇種別ごとに使用日数を集計
                row_data = {"職員名": staff}
                
                for leave_type in LEAVE_TYPES:
                    type_data = staff_data[staff_data["type"] == leave_type]
                    used_days = type_data["day_equivalent"].sum() if not type_data.empty else 0
                    row_data[f"{leave_type}_使用"] = round(used_days, 1)
                
                summary_data.append(row_data)
            
            # DataFrameに変換
            df_summary = pd.DataFrame(summary_data)
            
            # 付与日数の設定（カスタマイズ可能）
            st.markdown("---")
            st.markdown("#### 💼 付与日数の設定")
            col1, col2, col3 = st.columns(3)
            with col1:
                annual_leave_total = st.number_input("年休（日）", min_value=0, max_value=40, value=20, step=1)
            with col2:
                summer_leave_total = st.number_input("夏休み（日）", min_value=0, max_value=20, value=5, step=1)
            with col3:
                comp_leave_total = st.number_input("代休（日）", min_value=0, max_value=20, value=0, step=1, 
                                                   help="代休は取得した分だけカウント（付与なし）")
            
            # 残日数を計算
            df_summary["年休_残"] = annual_leave_total - df_summary["年休_使用"]
            df_summary["夏休み_残"] = summer_leave_total - df_summary["夏休み_使用"]
            df_summary["代休_残"] = comp_leave_total - df_summary["代休_使用"] if comp_leave_total > 0 else "-"
            
            # 表示用に列を整形
            display_columns = ["職員名"]
            for leave_type in LEAVE_TYPES:
                display_columns.extend([f"{leave_type}_使用", f"{leave_type}_残"])
            
            df_display = df_summary[display_columns]
            
            # 表を表示
            st.markdown("---")
            st.markdown(f"#### 📅 {selected_year}年度の休暇状況")
            st.dataframe(df_display, width='stretch', hide_index=True)
            
            # 注意事項
            st.info("""
            **💡 集計について**  
            - 使用日数は `day_equivalent`（日数換算）の合計です
            - 取り消し・再登録された休暇は、現在登録されているデータのみを集計します
            - 代休の「残」は、付与日数を設定した場合のみ表示されます
            """)
            
            # 月別集計
            st.markdown("---")
            st.subheader("📅 月別の使用状況")
            
            # 休暇種別の選択
            selected_leave_type = st.selectbox("休暇種別を選択", LEAVE_TYPES, key="monthly_leave_type")
            
            # 日付をdatetime型に変換
            df_year["date"] = pd.to_datetime(df_year["date"], errors="coerce")
            df_year["month"] = df_year["date"].dt.month
            
            # 選択された休暇種別でフィルタリング
            df_type = df_year[df_year["type"] == selected_leave_type]
            
            if df_type.empty:
                st.warning(f"{selected_year}年度に{selected_leave_type}の使用実績がありません。")
            else:
                # 職員×月のピボットテーブルを作成
                monthly_summary = []
                
                STAFF_MEMBERS = get_staff_list()
                
                for staff in STAFF_MEMBERS:
                    row = {"職員名": staff}
                    staff_data = df_type[df_type["staff_name"] == staff]
                    
                    # 年度の月範囲（1月〜12月）
                    for month in range(1, 13):  # 1-12月
                        month_data = staff_data[staff_data["month"] == month]
                        used = month_data["day_equivalent"].sum() if not month_data.empty else 0
                        row[f"{month}月"] = round(used, 1) if used > 0 else "-"
                    
                    # 合計
                    total = staff_data["day_equivalent"].sum()
                    row["合計"] = round(total, 1)
                    
                    monthly_summary.append(row)
                
                # DataFrameに変換
                df_monthly = pd.DataFrame(monthly_summary)
                
                # 月の順序を設定（1月〜12月）
                month_columns = ["職員名"] + [f"{m}月" for m in range(1, 13)] + ["合計"]
                df_monthly = df_monthly[month_columns]
                
                # 表を表示
                st.markdown(f"#### {selected_leave_type}の月別使用状況（{selected_year}年度）")
                st.dataframe(df_monthly, width='stretch', hide_index=True)
                
                # 可視化（オプション）
                with st.expander("📊 グラフで表示"):
                    # 合計が0より大きい職員のみ抽出
                    df_chart = df_monthly[df_monthly["合計"] != 0].copy()
                    
                    if not df_chart.empty:
                        # 月別の列を抽出
                        month_cols = [col for col in df_chart.columns if "月" in col and col != "合計"]
                        
                        # データを整形（"-"を0に変換）
                        for col in month_cols:
                            # まず文字列型に統一してから置換
                            df_chart[col] = df_chart[col].astype(str).replace("-", "0")
                            # 数値型に変換
                            df_chart[col] = pd.to_numeric(df_chart[col], errors="coerce").fillna(0).astype(float)
                        
                        # 横棒グラフで表示
                        st.bar_chart(df_chart.set_index("職員名")[month_cols].T)
                    else:
                        st.info("表示するデータがありません。")
    
    # 一括削除機能
    st.markdown("---")
    st.subheader("🗑️ データ管理")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 勤怠ログの一括削除")
        df_logs = read_attendance_logs(spreadsheet_id)
        if not df_logs.empty:
            st.warning(f"⚠️ 現在 {len(df_logs)} 件の勤怠ログが登録されています。")
            if st.button("🗑️ すべての勤怠ログを削除", type="primary"):
                if delete_all_attendance_logs(spreadsheet_id):
                    st.success("✅ すべての勤怠ログを削除しました。")
                    st.rerun()
                else:
                    st.error("❌ 削除に失敗しました。")
        else:
            st.info("勤怠ログは登録されていません。")
    
    with col2:
        st.markdown("#### イベントの一括削除")
        df_events = read_events(spreadsheet_id)
        if not df_events.empty:
            st.warning(f"⚠️ 現在 {len(df_events)} 件のイベントが登録されています。")
            if st.button("🗑️ すべてのイベントを削除", type="primary"):
                if delete_all_events(spreadsheet_id):
                    st.success("✅ すべてのイベントを削除しました。")
                    st.rerun()
                else:
                    st.error("❌ 削除に失敗しました。")
        else:
            st.info("イベントは登録されていません。")
    
    with col3:
        st.markdown("#### 掲示板の一括削除")
        df_bulletin = read_bulletin_board(spreadsheet_id)
        if not df_bulletin.empty:
            st.warning(f"⚠️ 現在 {len(df_bulletin)} 件の投稿があります。")
            if st.button("🗑️ すべての投稿を削除", type="primary"):
                if delete_all_bulletin_posts(spreadsheet_id):
                    st.success("✅ すべての投稿を削除しました。")
                    st.rerun()
                else:
                    st.error("❌ 削除に失敗しました。")
        else:
            st.info("投稿はありません。")
    
    # 職員管理
    st.markdown("---")
    st.subheader("👥 職員管理")
    
    # 職員一覧を表示
    df_staff = read_staff(spreadsheet_id)
    
    tab1, tab2 = st.tabs(["職員一覧", "職員登録"])
    
    with tab1:
        if df_staff.empty:
            st.info("職員が登録されていません。")
        else:
            st.markdown("#### 登録済み職員一覧")
            
            # 職員ごとにカードを表示
            for idx, row in df_staff.iterrows():
                with st.expander(f"👤 {row['name']} (ID: {row['staff_id']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**職員ID**: {row['staff_id']}")
                        st.write(f"**名前**: {row['name']}")
                        st.write(f"**パスワード**: {'●' * len(str(row['password']))}")
                    
                    with col2:
                        if st.button("🗑️ 削除", key=f"del_staff_{row['staff_id']}"):
                            if delete_staff(spreadsheet_id, row['staff_id']):
                                st.success("✅ 職員を削除しました。")
                                st.rerun()
                            else:
                                st.error("❌ 削除に失敗しました。")
    
    with tab2:
        st.markdown("#### 新規職員登録")
        
        with st.form("staff_registration_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_staff_id = st.text_input("職員ID", placeholder="例: staff001")
                new_staff_name = st.text_input("職員名", placeholder="例: 田中太郎")
            
            with col2:
                new_staff_password = st.text_input("パスワード", type="password", placeholder="パスワードを入力")
                new_staff_password_confirm = st.text_input("パスワード（確認）", type="password", placeholder="もう一度入力")
            
            submitted = st.form_submit_button("➕ 職員を登録", type="primary")
            
            if submitted:
                # 入力チェック
                if not new_staff_id or not new_staff_name or not new_staff_password:
                    st.error("❌ すべての項目を入力してください。")
                elif new_staff_password != new_staff_password_confirm:
                    st.error("❌ パスワードが一致しません。")
                elif not df_staff.empty and new_staff_id in df_staff["staff_id"].values:
                    st.error("❌ この職員IDは既に登録されています。")
                elif not df_staff.empty and new_staff_name in df_staff["name"].values:
                    st.error("❌ この職員名は既に登録されています。")
                else:
                    # 職員を登録
                    staff_data = {
                        "staff_id": new_staff_id,
                        "name": new_staff_name,
                        "password": new_staff_password
                    }
                    
                    if write_staff(spreadsheet_id, staff_data):
                        st.success("✅ 職員を登録しました。")
                        st.info("💡 サイドバーのユーザー選択に反映されます。ページを再読み込みしてください。")
                        st.rerun()
                    else:
                        st.error("❌ 登録に失敗しました。")
    
    st.markdown("---")
    
    # 勤怠ログ一覧
    st.markdown("---")


def main():
    """メイン関数"""
    # サイドバー
    with st.sidebar:
        st.title("📅 ハワイ大学")
        
        # ユーザー選択（先に表示）
        st.subheader("ユーザー選択")
        STAFF_MEMBERS = get_staff_list()
        user_options = STAFF_MEMBERS + [ADMIN_USER]
        selected_user = st.selectbox(
            "ユーザーを選択",
            user_options,
            index=user_options.index(st.session_state.selected_user) 
            if st.session_state.selected_user in user_options else 0
        )
        
        if selected_user != st.session_state.selected_user:
            st.session_state.selected_user = selected_user
            # ユーザーが変更されたら認証状態をリセット
            st.session_state.admin_authenticated = False
            st.session_state.staff_authenticated = False
            st.session_state.current_staff_id = None
            st.rerun()
        
        if st.session_state.selected_user:
            st.info(f"現在のユーザー: **{st.session_state.selected_user}**")
        
        # 職員認証チェック（管理者以外の場合）
        if (st.session_state.selected_user and 
            st.session_state.selected_user != ADMIN_USER and 
            not st.session_state.staff_authenticated):
            
            st.markdown("---")
            st.subheader("🔐 職員認証")
            
            # スプレッドシートから職員データを取得
            spreadsheet_id = get_spreadsheet_id()
            if spreadsheet_id:
                df_staff = read_staff(spreadsheet_id)
                
                # DataFrameが空でない、かつnameカラムが存在するかチェック
                if not df_staff.empty and "name" in df_staff.columns:
                    # 選択された職員のデータを取得
                    staff_row = df_staff[df_staff["name"] == st.session_state.selected_user]
                    
                    if not staff_row.empty:
                        staff_id = st.text_input(
                            "職員ID",
                            placeholder="職員IDを入力",
                            help="管理者から発行された職員IDを入力してください"
                        )
                        staff_password = st.text_input(
                            "パスワード",
                            type="password",
                            placeholder="パスワードを入力",
                            help="管理者から発行されたパスワードを入力してください"
                        )
                        
                        if st.button("ログイン", type="primary", key="staff_login"):
                            correct_id = str(staff_row.iloc[0]["staff_id"]).strip()
                            correct_password = str(staff_row.iloc[0]["password"]).strip()
                            
                            # 入力値もトリミング
                            staff_id = staff_id.strip() if staff_id else ""
                            staff_password = staff_password.strip() if staff_password else ""
                            
                            if staff_id == correct_id and staff_password == correct_password:
                                st.session_state.staff_authenticated = True
                                st.session_state.current_staff_id = staff_id
                                st.success("✅ 認証成功")
                                st.rerun()
                            else:
                                st.error("❌ 職員IDまたはパスワードが正しくありません")
                                if staff_id != correct_id:
                                    st.warning("💡 職員IDが一致しません")
                                if staff_password != correct_password:
                                    st.warning("💡 パスワードが一致しません")
                    else:
                        st.warning("⚠️ この職員は未登録です。管理者に登録を依頼してください。")
                        # 未登録の場合は認証なしで使用可能
                        st.info("💡 職員が未登録の場合は、そのまま利用できます。")
                        if st.button("認証なしで続行", type="secondary"):
                            st.session_state.staff_authenticated = True
                            st.rerun()
                else:
                    # staffシートが空または存在しない場合
                    st.warning("⚠️ 職員データベースが未設定です。")
                    st.info("""
                    💡 **初回セットアップ**
                    
                    1. 管理者でログイン
                    2. 管理ダッシュボード → 職員管理で職員を登録
                    
                    または、認証なしで続行できます。
                    """)
                    if st.button("認証なしで続行", type="secondary", key="no_data_continue"):
                        st.session_state.staff_authenticated = True
                        st.rerun()
            else:
                st.warning("⚠️ スプレッドシートIDが設定されていません。")
                if st.button("認証なしで続行", type="secondary", key="no_sheet_continue"):
                    st.session_state.staff_authenticated = True
                    st.rerun()
        
        # 管理者認証チェック
        if st.session_state.selected_user == ADMIN_USER and not st.session_state.admin_authenticated:
            st.markdown("---")
            st.subheader("🔐 管理者認証")
            admin_password = st.text_input(
                "管理者パスワード",
                type="password",
                help="管理者機能にアクセスするにはパスワードが必要です"
            )
            
            # パスワードの取得（secrets.tomlから）
            correct_password = ""
            try:
                if "admin_password" in st.secrets:
                    correct_password = st.secrets["admin_password"]
            except:
                pass
            
            # secrets.tomlから直接読み込む（フォールバック）
            if not correct_password:
                try:
                    import tomllib
                    import os
                    secrets_path = os.path.join(".streamlit", "secrets.toml")
                    if os.path.exists(secrets_path):
                        with open(secrets_path, "rb") as f:
                            secrets_data = tomllib.load(f)
                            correct_password = secrets_data.get("admin_password", "")
                            if not correct_password and "gcp_service_account" in secrets_data:
                                gcp_data = secrets_data["gcp_service_account"]
                                if isinstance(gcp_data, dict) and "admin_password" in gcp_data:
                                    correct_password = gcp_data["admin_password"]
                except:
                    pass
            
            # デフォルトパスワード（secrets.tomlに設定されていない場合）
            if not correct_password:
                correct_password = "admin123"  # デフォルトパスワード（変更推奨）
                st.warning("⚠️ デフォルトパスワードが使用されています。secrets.tomlにadmin_passwordを設定してください。")
            
            if st.button("認証", type="primary"):
                if admin_password == correct_password:
                    st.session_state.admin_authenticated = True
                    st.success("✅ 認証成功")
                    st.rerun()
                else:
                    st.error("❌ パスワードが正しくありません")
        
        st.markdown("---")
        
        # スプレッドシートID設定（管理者のみ表示、認証済みの場合のみ）
        if st.session_state.selected_user == ADMIN_USER and st.session_state.admin_authenticated:
            st.subheader("設定（管理者専用）")
            # デフォルト値の取得
            default_id = ""
            try:
                if "spreadsheet_id" in st.secrets:
                    default_id = st.secrets["spreadsheet_id"]
            except:
                pass
            
            # secrets.tomlから直接読み込む（フォールバック）
            if not default_id:
                try:
                    import tomllib
                    import os
                    secrets_path = os.path.join(".streamlit", "secrets.toml")
                    if os.path.exists(secrets_path):
                        with open(secrets_path, "rb") as f:
                            secrets_data = tomllib.load(f)
                            default_id = secrets_data.get("spreadsheet_id", "")
                            if not default_id and "gcp_service_account" in secrets_data:
                                gcp_data = secrets_data["gcp_service_account"]
                                if isinstance(gcp_data, dict) and "spreadsheet_id" in gcp_data:
                                    default_id = gcp_data["spreadsheet_id"]
                except:
                    pass
            
            # セッション状態が空でデフォルト値がある場合、セッション状態を更新
            if not st.session_state.spreadsheet_id and default_id:
                st.session_state.spreadsheet_id = default_id
            
            # 現在のID（セッション状態またはデフォルト値）
            current_id = st.session_state.spreadsheet_id or default_id
            
            # デフォルト値が設定されている場合の表示
            if default_id:
                if current_id == default_id:
                    st.success(f"✅ スプレッドシートID: 設定済み（デフォルト値）")
                    with st.expander("🔧 IDを変更する", expanded=False):
                        spreadsheet_id = st.text_input(
                            "GoogleスプレッドシートID",
                            value=current_id,
                            key="spreadsheet_id_input",
                            help="スプレッドシートのURLから取得できます（例: https://docs.google.com/spreadsheets/d/[ID]/edit）"
                        )
                        if spreadsheet_id != current_id:
                            st.session_state.spreadsheet_id = spreadsheet_id
                            st.rerun()
                else:
                    st.info(f"📝 カスタムIDが設定されています")
                    spreadsheet_id = st.text_input(
                        "GoogleスプレッドシートID",
                        value=current_id,
                        help="スプレッドシートのURLから取得できます（例: https://docs.google.com/spreadsheets/d/[ID]/edit）"
                    )
                    if spreadsheet_id != st.session_state.spreadsheet_id:
                        st.session_state.spreadsheet_id = spreadsheet_id
                        st.rerun()
                    # デフォルト値に戻すボタン
                    if st.button("🔄 デフォルト値に戻す"):
                        st.session_state.spreadsheet_id = ""
                        st.rerun()
            else:
                # デフォルト値が設定されていない場合
                spreadsheet_id = st.text_input(
                    "GoogleスプレッドシートID",
                    value=st.session_state.spreadsheet_id,
                    help="スプレッドシートのURLから取得できます（例: https://docs.google.com/spreadsheets/d/[ID]/edit）\nデフォルト値は secrets.toml で設定できます。"
                )
                if spreadsheet_id != st.session_state.spreadsheet_id:
                    st.session_state.spreadsheet_id = spreadsheet_id
                    st.rerun()
            
            st.markdown("---")
        
        # ナビゲーションメニュー
        st.subheader("メニュー")
        menu_options = [
            "🗓 カレンダー",
            "📝 休暇申請",
            "📅 イベント",
            "📋 掲示板"
        ]
        
        # 管理者の場合のみ集計メニューを追加（認証済みの場合のみ）
        if st.session_state.selected_user == ADMIN_USER and st.session_state.admin_authenticated:
            menu_options.append("📈 管理者用集計")
        
        selected_menu = st.radio("ページを選択", menu_options)
    
    # メインコンテンツ
    # 認証チェック（管理者または認証済み職員のみアクセス可能）
    user_authenticated = (
        (st.session_state.selected_user == ADMIN_USER and st.session_state.admin_authenticated) or
        (st.session_state.selected_user != ADMIN_USER and st.session_state.staff_authenticated)
    )
    
    if not user_authenticated:
        st.info("🔐 サイドバーからログインしてください。")
        st.markdown("---")
        st.markdown("""
        ### 📋 使い方
        
        1. **サイドバー**でユーザーを選択
        2. **職員ID**と**パスワード**を入力してログイン
        3. ログイン後、各機能をご利用いただけます
        
        ### 👥 職員の方へ
        - 職員ID とパスワードは管理者から発行されます
        - 未登録の場合は、管理者に登録を依頼してください
        
        ### 👤 管理者の方へ
        - 管理者パスワードを入力して認証してください
        - 認証後、職員の登録・管理が可能です
        """)
    else:
        if selected_menu == "🗓 カレンダー":
            show_calendar_page()
        elif selected_menu == "📝 休暇申請":
            show_leave_application_page()
        elif selected_menu == "📅 イベント":
            show_events_page()
        elif selected_menu == "📋 掲示板":
            show_bulletin_board_page()
        elif selected_menu == "📈 管理者用集計":
            show_admin_dashboard_page()


if __name__ == "__main__":
    main()
