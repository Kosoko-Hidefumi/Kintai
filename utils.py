"""
勤怠管理システム用のユーティリティ関数
年度判定、時間計算、日数換算などのロジックを提供
"""
from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, datetime
from functools import lru_cache
from typing import Dict, Set, Tuple

import jpholiday

# この日以降の残業・代休だけを積立・残高に計上する（それ以前は「その他」申請で管理）
COMPENSATORY_LEAVE_EFFECTIVE_DATE = date(2026, 7, 1)


def calculate_fiscal_year(target_date: date) -> int:
    """
    日付から年度を計算（1月1日〜12月31日を1年度とする）
    
    Args:
        target_date: 対象日付
    
    Returns:
        年度（例：2026年1月〜2026年12月は2026年度）
    
    Examples:
        >>> calculate_fiscal_year(date(2026, 1, 1))
        2026
        >>> calculate_fiscal_year(date(2026, 12, 31))
        2026
        >>> calculate_fiscal_year(date(2026, 6, 15))
        2026
    """
    # 1月〜12月をそのまま年度とする
    return target_date.year


def calculate_duration_hours(start_time: str, end_time: str) -> float:
    """
    開始時間と終了時間から取得時間を計算
    12:00-13:00の昼休み時間は除外する
    
    Args:
        start_time: 開始時間（HH:MM形式、例: "09:00"）
        end_time: 終了時間（HH:MM形式、例: "17:00"）
    
    Returns:
        取得時間（時間単位、小数点以下2桁、昼休み1時間を除外）
    
    Examples:
        >>> calculate_duration_hours("09:00", "17:00")
        7.0  # 8時間 - 1時間（昼休み）= 7時間
        >>> calculate_duration_hours("13:00", "17:00")
        4.0  # 昼休みと重複しない
        >>> calculate_duration_hours("09:00", "12:00")
        3.0  # 昼休みと重複しない
        >>> calculate_duration_hours("11:00", "14:00")
        2.0  # 3時間 - 1時間（昼休み）= 2時間
    """
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        # 基本の時間を計算
        duration = (end - start).total_seconds() / 3600
        
        # 12:00-13:00の昼休み時間が含まれているかチェック
        lunch_start = datetime.strptime("12:00", "%H:%M")
        lunch_end = datetime.strptime("13:00", "%H:%M")
        
        # 開始時間が12:00より前で、終了時間が13:00より後の場合、昼休み1時間を除外
        if start < lunch_start and end > lunch_end:
            duration -= 1.0  # 昼休み1時間を除外
        
        return round(max(0, duration), 2)  # 負の値は0に、小数点以下2桁
    except (ValueError, TypeError):
        return 0.0


def calculate_day_equivalent(hours: float) -> float:
    """
    時間を日数に換算（8時間 = 1日）
    
    Args:
        hours: 時間数
    
    Returns:
        日数（小数点以下2桁）
    
    Examples:
        >>> calculate_day_equivalent(8.0)
        1.0
        >>> calculate_day_equivalent(4.0)
        0.5
        >>> calculate_day_equivalent(16.0)
        2.0
    """
    return round(hours / 8, 2)


def parse_time_string(time_str: str) -> Tuple[int, int]:
    """
    時間文字列（HH:MM）を時と分に分解
    
    Args:
        time_str: 時間文字列（HH:MM形式）
    
    Returns:
        (時, 分)のタプル
    
    Examples:
        >>> parse_time_string("09:30")
        (9, 30)
        >>> parse_time_string("17:00")
        (17, 0)
    """
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.hour, time_obj.minute
    except (ValueError, TypeError):
        return 0, 0


@lru_cache(maxsize=120)
def japanese_business_calendar_dates_in_month(year: int, month: int) -> frozenset[date]:
    """
    指定月について、土日および国民祝日・振替休日を除いた日の集合（出勤ベースの暦算用）。
    """
    _, last_day = calendar.monthrange(year, month)
    bucket: list[date] = []
    for day in range(1, last_day + 1):
        d = date(year, month, day)
        if d.weekday() >= 5:
            continue
        if jpholiday.is_holiday(d):
            continue
        bucket.append(d)
    return frozenset(bucket)


def count_presumed_attendance_days_in_month(
    year: int,
    month: int,
    full_day_leave_dates: Set[date],
) -> int:
    """営業日（土日・祝除く）から、終日休暇（caller が渡す日付セット）が重なる日だけを除外した日数。"""
    workdays = japanese_business_calendar_dates_in_month(year, month)
    return len(workdays - full_day_leave_dates)


def build_staff_full_day_leave_dates_from_logs(df_logs) -> Dict[str, Set[date]]:
    """
    勤怠ログのうち、アプリが「1日休み」と同様に登録される 08:30〜17:00 の記録を職員別の日付集合にまとめる。
    """
    import pandas as pd

    out: dict[str, set[date]] = defaultdict(set)
    if df_logs is None or getattr(df_logs, "empty", True):
        return {}

    needed = {"date", "staff_name", "start_time", "end_time"}
    if not needed <= set(df_logs.columns):
        return {}

    for _, row in df_logs.iterrows():
        st_raw = row.get("start_time", "")
        et_raw = row.get("end_time", "")
        if pd.isna(st_raw) or pd.isna(et_raw):
            continue
        st = str(st_raw).strip()
        et = str(et_raw).strip()
        if st.lower() == "nan" or et.lower() == "nan":
            continue

        try:
            t_st = datetime.strptime(st, "%H:%M").time()
            t_et = datetime.strptime(et, "%H:%M").time()
        except (ValueError, TypeError):
            continue

        if (
            t_st.hour != 8
            or t_st.minute != 30
            or t_et.hour != 17
            or t_et.minute != 0
        ):
            continue

        ds = pd.to_datetime(row.get("date"), errors="coerce")
        if pd.isna(ds):
            continue
        dt = ds.date()

        staff = row.get("staff_name", "")
        if pd.isna(staff):
            continue
        name = str(staff).strip()
        if name:
            out[name].add(dt)

    return dict(out)


def format_time_string(hour: int, minute: int) -> str:
    """
    時と分を時間文字列（HH:MM）に変換
    
    Args:
        hour: 時（0-23）
        minute: 分（0-59）
    
    Returns:
        時間文字列（HH:MM形式）
    
    Examples:
        >>> format_time_string(9, 30)
        '09:30'
        >>> format_time_string(17, 0)
        '17:00'
    """
    return f"{hour:02d}:{minute:02d}"


def calculate_compensatory_balance(spreadsheet_id: str, staff_name: str) -> dict:
    """
    残業積立から代休残高を計算して返す。
    換算レート：残業8時間 = 代休1日

    COMPENSATORY_LEAVE_EFFECTIVE_DATE 以降の残業・代休取得のみを集計する。

    返り値：
    {
        "overtime_hours": float,        # 承認済み残業時間の合計
        "overtime_days_earned": float,  # 代休取得可能日数（時間÷8）
        "comp_taken_days": float,       # 取得済み代休日数
        "balance_days": float,          # 残高（マイナスは超過取得）
        "pending_hours": float          # 承認待ちの残業時間
    }
    """
    # utils.py は database.py を参照して計算する（依存方向は app.py→utils.py と同じ）
    import pandas as pd
    from database import read_overtime_logs, read_attendance_logs

    df_ot = read_overtime_logs(spreadsheet_id)
    df_att = read_attendance_logs(spreadsheet_id)

    staff_name = str(staff_name).strip()
    cutoff = pd.Timestamp(COMPENSATORY_LEAVE_EFFECTIVE_DATE)

    # overtime_logs（適用日以降の日付のみ）
    overtime_hours_approved = 0.0
    overtime_hours_pending = 0.0
    if not df_ot.empty:
        df_ot = df_ot.copy()
        # 列が無い場合もあるため安全に変換
        if "overtime_hours" in df_ot.columns:
            df_ot["overtime_hours"] = pd.to_numeric(df_ot["overtime_hours"], errors="coerce").fillna(0.0)
        if "approved" in df_ot.columns:
            df_ot["approved"] = df_ot["approved"].astype(str).str.strip()

        mask_staff = df_ot.get("staff_name", pd.Series([""] * len(df_ot))).astype(str).str.strip() == staff_name
        if "date" in df_ot.columns:
            ot_dates = pd.to_datetime(df_ot["date"], errors="coerce")
            mask_effective = ot_dates.notna() & (ot_dates >= cutoff)
        else:
            mask_effective = pd.Series([True] * len(df_ot), index=df_ot.index)

        approved_mask = mask_staff & mask_effective & (df_ot.get("approved", "").astype(str) == "approved")
        pending_mask = mask_staff & mask_effective & (df_ot.get("approved", "").astype(str) == "pending")

        overtime_hours_approved = float(df_ot.loc[approved_mask, "overtime_hours"].sum()) if "overtime_hours" in df_ot.columns else 0.0
        overtime_hours_pending = float(df_ot.loc[pending_mask, "overtime_hours"].sum()) if "overtime_hours" in df_ot.columns else 0.0

    overtime_days_earned = round(overtime_hours_approved / 8.0, 2)
    pending_hours = round(overtime_hours_pending, 2)

    # 代休取得（attendance_logs 側に type="代休" として記録される、適用日以降のみ）
    comp_taken_days = 0.0
    if not df_att.empty:
        df_att = df_att.copy()
        if "day_equivalent" in df_att.columns:
            df_att["day_equivalent"] = pd.to_numeric(df_att["day_equivalent"], errors="coerce").fillna(0.0)

        mask_staff = df_att.get("staff_name", pd.Series([""] * len(df_att))).astype(str).str.strip() == staff_name
        mask_type = df_att.get("type", pd.Series([""] * len(df_att))).astype(str).str.strip() == "代休"
        if "date" in df_att.columns:
            att_dates = pd.to_datetime(df_att["date"], errors="coerce")
            mask_effective_att = att_dates.notna() & (att_dates >= cutoff)
        else:
            mask_effective_att = pd.Series([True] * len(df_att), index=df_att.index)

        comp_taken_days = float(df_att.loc[mask_staff & mask_type & mask_effective_att, "day_equivalent"].sum()) if "day_equivalent" in df_att.columns else 0.0

    comp_taken_days = round(comp_taken_days, 2)
    balance_days = round(overtime_days_earned - comp_taken_days, 2)

    return {
        "overtime_hours": round(float(overtime_hours_approved), 2),
        "overtime_days_earned": overtime_days_earned,
        "comp_taken_days": comp_taken_days,
        "balance_days": balance_days,
        "pending_hours": pending_hours,
    }
