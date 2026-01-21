"""
勤怠管理システム用のユーティリティ関数
年度判定、時間計算、日数換算などのロジックを提供
"""
from datetime import date, datetime
from typing import Tuple


def calculate_fiscal_year(target_date: date) -> int:
    """
    日付から年度を計算（7月1日〜翌年6月30日を1年度とする）
    
    Args:
        target_date: 対象日付
    
    Returns:
        年度（例：2025年7月〜2026年6月は2025年度）
    
    Examples:
        >>> calculate_fiscal_year(date(2025, 7, 1))
        2025
        >>> calculate_fiscal_year(date(2026, 6, 30))
        2025
        >>> calculate_fiscal_year(date(2026, 1, 15))
        2025
    """
    year = target_date.year
    month = target_date.month
    # 7月以上ならその年、6月以下なら前年が年度
    if month >= 7:
        return year
    else:
        return year - 1


def calculate_duration_hours(start_time: str, end_time: str) -> float:
    """
    開始時間と終了時間から取得時間を計算
    
    Args:
        start_time: 開始時間（HH:MM形式、例: "09:00"）
        end_time: 終了時間（HH:MM形式、例: "17:00"）
    
    Returns:
        取得時間（時間単位、小数点以下2桁）
    
    Examples:
        >>> calculate_duration_hours("09:00", "17:00")
        8.0
        >>> calculate_duration_hours("13:00", "17:00")
        4.0
        >>> calculate_duration_hours("09:00", "09:00")
        0.0
    """
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        duration = (end - start).total_seconds() / 3600
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
