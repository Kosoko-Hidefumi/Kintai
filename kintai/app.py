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
    read_events,
    write_event,
    delete_all_attendance_logs,
    delete_all_events,
    delete_all_bulletin_posts,
    delete_attendance_log,
    update_attendance_logs,
    delete_event,
    update_event
)
from utils import (
    calculate_fiscal_year,
    calculate_duration_hours,
    calculate_day_equivalent
)

# ページ設定
st.set_page_config(
    page_title="勤怠管理・掲示板システム",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 定数定義
STAFF_MEMBERS = ["職員A", "職員B", "職員C", "職員D", "職員E"]
LEAVE_TYPES = ["年休", "夏休み", "代休"]
ADMIN_USER = "管理者"

# セッション状態の初期化
if "selected_user" not in st.session_state:
    st.session_state.selected_user = None
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

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
        "代休": "#FFE66D"       # 黄色
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
    
    # 休暇ログを連続する日付でグループ化してカレンダーイベントに変換
    if not df_logs.empty:
        # 日付をdatetime型に変換
        df_logs["date"] = pd.to_datetime(df_logs["date"], errors="coerce")
        df_logs = df_logs.sort_values(["staff_name", "type", "date"])
        
        # 連続する日付をグループ化
        current_group = None
        for _, row in df_logs.iterrows():
            event_date = row.get("date")
            event_id = row.get("event_id", "")
            staff_name = row.get("staff_name", "")
            leave_type = row.get("type", "")
            start_time = row.get("start_time", "")
            end_time = row.get("end_time", "")
            remarks = row.get("remarks", "")
            
            if pd.isna(event_date):
                continue
            
            event_date_str = event_date.strftime("%Y-%m-%d")
            
            # 新しいグループの開始、または前のグループと連続していない場合
            if (current_group is None or 
                current_group["staff_name"] != staff_name or 
                current_group["leave_type"] != leave_type or
                (event_date - current_group["end_date"]).days > 1):
                
                # 前のグループがあればイベントとして追加
                if current_group is not None:
                    start_date_str = current_group["start_date"].strftime("%Y-%m-%d")
                    # FullCalendarではendは終了日の翌日を指定（排他的）
                    end_date_str = (current_group["end_date"] + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
                    
                    title = f"{current_group['staff_name']} - {current_group['leave_type']}"
                    if current_group["start_date"] != current_group["end_date"]:
                        title += f" ({current_group['start_date'].strftime('%m/%d')}〜{current_group['end_date'].strftime('%m/%d')})"
                    
                    event = {
                        "title": title,
                        "start": start_date_str,
                        "end": end_date_str,
                        "allDay": True,  # 終日イベントとして設定
                        "color": leave_type_colors.get(current_group["leave_type"], "#95A5A6"),
                        "resource": current_group["leave_type"],
                        "extendedProps": {
                            "event_id": current_group.get("event_id", ""),
                            "staff_name": current_group["staff_name"],
                            "leave_type": current_group["leave_type"],
                            "start_date_display": current_group["start_date"].strftime("%Y年%m月%d日"),
                            "end_date_display": current_group["end_date"].strftime("%Y年%m月%d日"),
                            "time_range": f"{current_group['start_time']} - {current_group['end_time']}" if current_group["start_time"] and current_group["end_time"] else "",
                            "remarks": current_group["remarks"],
                            "event_type": "attendance"
                        }
                    }
                    calendar_events.append(event)
                
                # 新しいグループを開始
                current_group = {
                    "event_id": event_id,
                    "staff_name": staff_name,
                    "leave_type": leave_type,
                    "start_date": event_date,
                    "end_date": event_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "remarks": remarks
                }
            else:
                # 同じグループの終了日を更新
                current_group["end_date"] = event_date
        
        # 最後のグループを追加
        if current_group is not None:
            start_date_str = current_group["start_date"].strftime("%Y-%m-%d")
            # FullCalendarではendは終了日の翌日を指定（排他的）
            end_date_str = (current_group["end_date"] + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            
            title = f"{current_group['staff_name']} - {current_group['leave_type']}"
            if current_group["start_date"] != current_group["end_date"]:
                title += f" ({current_group['start_date'].strftime('%m/%d')}〜{current_group['end_date'].strftime('%m/%d')})"
            
            event = {
                "title": title,
                "start": start_date_str,
                "end": end_date_str,
                "allDay": True,  # 終日イベントとして設定
                "color": leave_type_colors.get(current_group["leave_type"], "#95A5A6"),
                "resource": current_group["leave_type"],
                "extendedProps": {
                    "event_id": current_group.get("event_id", ""),
                    "staff_name": current_group["staff_name"],
                    "leave_type": current_group["leave_type"],
                    "start_date_display": current_group["start_date"].strftime("%Y年%m月%d日"),
                    "end_date_display": current_group["end_date"].strftime("%Y年%m月%d日"),
                    "time_range": f"{current_group['start_time']} - {current_group['end_time']}" if current_group["start_time"] and current_group["end_time"] else "",
                    "remarks": current_group["remarks"],
                    "event_type": "attendance"
                }
            }
            calendar_events.append(event)
    
    # イベントをカレンダーイベントに変換（職員名なし、複数日対応）
    for _, row in df_events.iterrows():
        event_id = row.get("event_id", "")
        start_date_str = row.get("start_date", "")
        end_date_str = row.get("end_date", "")
        title = row.get("title", "")
        description = row.get("description", "")
        color = row.get("color", "#95A5A6")
        
        if not start_date_str:
            continue
        
        # 終了日が設定されていない場合は開始日と同じにする
        if not end_date_str or end_date_str == start_date_str:
            end_date_str = start_date_str
        
        # 日付をdatetime型に変換
        try:
            start_date = pd.to_datetime(start_date_str)
            end_date = pd.to_datetime(end_date_str)
            # FullCalendarではendは終了日の翌日を指定（排他的）
            end_date_exclusive = (end_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            start_date_formatted = start_date.strftime("%Y-%m-%d")
        except:
            # 日付の変換に失敗した場合はそのまま使用
            start_date_formatted = start_date_str
            end_date_exclusive = end_date_str
        
        # イベントオブジェクトを作成（複数日対応）
        event = {
            "title": title,
            "start": start_date_formatted,
            "end": end_date_exclusive,
            "allDay": True,  # 終日イベントとして設定
            "color": color,
            "resource": "event",
            "extendedProps": {
                "event_id": event_id,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "event_title": title,
                "description": description,
                "event_color": color,
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
            
            st.info(f"""
            **職員**: {staff_name}  
            **休暇種別**: {leave_type}  
            **期間**: {period_display}  
            **時間**: {time_range}  
            **備考**: {remarks}
            """)
            
            # 削除ボタン（管理者または本人のみ）
            can_edit = (st.session_state.selected_user == ADMIN_USER and st.session_state.admin_authenticated) or \
                       (st.session_state.selected_user == staff_name)
            
            st.markdown("---")
            if can_edit:
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ 削除", key=f"del_att_{event_id}", type="secondary"):
                        spreadsheet_id = get_spreadsheet_id()
                        if spreadsheet_id and delete_attendance_log(spreadsheet_id, event_id):
                            st.success("✅ 休暇申請を削除しました。")
                            st.rerun()
                        else:
                            st.error("❌ 削除に失敗しました。")
            else:
                st.warning("この休暇申請を削除できるのは、本人または管理者のみです。")
        
        # 一般イベントの場合
        elif event_type == "general_event" and event_id:
            st.markdown("---")
            st.subheader("📅 イベントの詳細")
            
            event_title = clicked_event.get('extendedProps', {}).get('event_title', '不明')
            start_date_str = clicked_event.get('extendedProps', {}).get('start_date', '')
            end_date_str = clicked_event.get('extendedProps', {}).get('end_date', '')
            description = clicked_event.get('extendedProps', {}).get('description', 'なし')
            
            # 日付のフォーマット
            try:
                start_date_display = pd.to_datetime(start_date_str).strftime("%Y年%m月%d日")
                end_date_display = pd.to_datetime(end_date_str).strftime("%Y年%m月%d日")
                if start_date_display == end_date_display:
                    period_display = start_date_display
                else:
                    period_display = f"{start_date_display} 〜 {end_date_display}"
            except:
                period_display = "不明"
            
            st.info(f"""
            **イベント名**: {event_title}  
            **期間**: {period_display}  
            **説明**: {description}
            """)
            
            # 削除ボタン（誰でも削除可能）
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🗑️ 削除", key=f"del_evt_{event_id}", type="secondary"):
                    spreadsheet_id = get_spreadsheet_id()
                    if spreadsheet_id and delete_event(spreadsheet_id, event_id):
                        st.success("✅ イベントを削除しました。")
                        st.rerun()
                    else:
                        st.error("❌ 削除に失敗しました。")
        
        # その他のイベント（デバッグ用）
        else:
            st.warning(f"イベントタイプ: {event_type}, イベントID: {event_id}")
    
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
    
    st.markdown("---")
    
    with st.form("leave_application_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            staff_name = st.selectbox("職員名", STAFF_MEMBERS, 
                                     index=STAFF_MEMBERS.index(st.session_state.selected_user) 
                                     if st.session_state.selected_user in STAFF_MEMBERS else 0)
            leave_type = st.selectbox("休暇種別", LEAVE_TYPES)
        
        with col2:
            start_time = st.time_input("開始時間", value=datetime.strptime("09:00", "%H:%M").time())
            end_time = st.time_input("終了時間", value=datetime.strptime("17:00", "%H:%M").time())
        
        remarks = st.text_area("備考", height=100)
        
        submitted = st.form_submit_button("申請を送信", type="primary")
        
        if submitted:
            # 日付の妥当性チェック
            if end_date < start_date:
                st.error("❌ 終了日は開始日以降を選択してください。")
                return
            
            spreadsheet_id = get_spreadsheet_id()
            if not spreadsheet_id:
                st.error("スプレッドシートIDが設定されていません。サイドバーで設定してください。")
                return
            
            # 開始日から終了日までの各日について登録
            from datetime import timedelta
            current_date = start_date
            success_count = 0
            total_days = (end_date - start_date).days + 1
            
            while current_date <= end_date:
                # 時間計算
                start_str = start_time.strftime("%H:%M")
                end_str = end_time.strftime("%H:%M")
                duration_hours = calculate_duration_hours(start_str, end_str)
                day_equivalent = calculate_day_equivalent(duration_hours)
                fiscal_year = calculate_fiscal_year(current_date)
                
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
                st.success(f"休暇申請が正常に登録されました！（{total_days}日分）")
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
        
        st.markdown("---")
        
        with st.form("event_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                event_title = st.text_input("イベント名", placeholder="例: 会議、研修、イベントなど")
            
            with col2:
                event_color = st.color_picker("色", value="#4285F4", help="カレンダーでの表示色を選択")
            
            description = st.text_area("説明", height=100, placeholder="イベントの詳細や備考")
            
            submitted = st.form_submit_button("イベントを登録", type="primary")
            
            if submitted:
                if not event_title:
                    st.warning("イベント名を入力してください。")
                elif end_date < start_date:
                    st.error("❌ 終了日は開始日以降を選択してください。")
                else:
                    event_data = {
                        "event_id": str(uuid.uuid4()),
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "title": event_title,
                        "description": description,
                        "color": event_color
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
                    if row.get("description"):
                        st.markdown(f"**説明**: {row.get('description')}")
                with col2:
                    color = row.get("color", "#95A5A6")
                    st.markdown(f'<div style="background-color: {color}; padding: 20px; border-radius: 5px; min-height: 50px;"></div>', unsafe_allow_html=True)
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
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {row.get('title', 'タイトルなし')}")
                    st.markdown(f"{row.get('content', '')}")
                with col2:
                    st.caption(f"**投稿者**: {row.get('author', '不明')}")
                    st.caption(f"**日時**: {row.get('timestamp', '不明')}")
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
        df_logs["fiscal_year"] = pd.to_numeric(df_logs["fiscal_year"], errors="coerce")
        df_year = df_logs[df_logs["fiscal_year"] == selected_year]
        
        if df_year.empty:
            st.warning(f"{selected_year}年度のデータがありません。")
        else:
            # 職員ごと、休暇種別ごとに集計
            df_year["day_equivalent"] = pd.to_numeric(df_year["day_equivalent"], errors="coerce")
            
            # 集計用のデータフレームを作成
            summary_data = []
            
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
                
                for staff in STAFF_MEMBERS:
                    row = {"職員名": staff}
                    staff_data = df_type[df_type["staff_name"] == staff]
                    
                    # 年度の月範囲（7月〜翌6月）
                    for month in range(7, 13):  # 7-12月
                        month_data = staff_data[staff_data["month"] == month]
                        used = month_data["day_equivalent"].sum() if not month_data.empty else 0
                        row[f"{month}月"] = round(used, 1) if used > 0 else "-"
                    
                    for month in range(1, 7):  # 1-6月
                        month_data = staff_data[staff_data["month"] == month]
                        used = month_data["day_equivalent"].sum() if not month_data.empty else 0
                        row[f"{month}月"] = round(used, 1) if used > 0 else "-"
                    
                    # 合計
                    total = staff_data["day_equivalent"].sum()
                    row["合計"] = round(total, 1)
                    
                    monthly_summary.append(row)
                
                # DataFrameに変換
                df_monthly = pd.DataFrame(monthly_summary)
                
                # 月の順序を設定（7月〜6月）
                month_columns = ["職員名"] + [f"{m}月" for m in range(7, 13)] + [f"{m}月" for m in range(1, 7)] + ["合計"]
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
                            df_chart[col] = df_chart[col].replace("-", 0)
                            df_chart[col] = pd.to_numeric(df_chart[col], errors="coerce").fillna(0)
                        
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
    
    st.markdown("---")
    
    # TODO: 集計ロジックの実装
    df = read_attendance_logs(spreadsheet_id)
    if not df.empty:
        st.subheader("勤怠ログ一覧")
        st.dataframe(df, width='stretch')


def main():
    """メイン関数"""
    # サイドバー
    with st.sidebar:
        st.title("📅 勤怠管理システム")
        
        # ユーザー選択（先に表示）
        st.subheader("ユーザー選択")
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
            if selected_user != ADMIN_USER:
                st.session_state.admin_authenticated = False
            st.rerun()
        
        if st.session_state.selected_user:
            st.info(f"現在のユーザー: **{st.session_state.selected_user}**")
        
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
