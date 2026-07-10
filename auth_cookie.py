"""Cookie-based login persistence for the Kintai app."""
from __future__ import annotations

import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone

import streamlit as st
from streamlit_cookies_controller import CookieController

_COOKIE_NAME = "kintai_auth"
_VALID_HOURS = 12


def _get_cookie_secret() -> str | None:
    try:
        secret = st.secrets["cookie_secret"]
        if secret is None:
            return None
        secret_str = str(secret).strip()
        return secret_str or None
    except (KeyError, TypeError, FileNotFoundError, AttributeError):
        return None


def _cookie_enabled() -> bool:
    return _get_cookie_secret() is not None


def _sign_payload(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _write_login_cookie(controller: CookieController, user_name: str, role: str, staff_id: str) -> None:
    secret = _get_cookie_secret()
    if not secret:
        return

    exp = int(time.time()) + _VALID_HOURS * 3600
    payload = f"{user_name}::{role}::{staff_id}::{exp}"
    signature = _sign_payload(payload, secret)
    token = f"{payload}::{signature}"
    expires = datetime.now(timezone.utc) + timedelta(hours=_VALID_HOURS)

    try:
        controller.set(_COOKIE_NAME, token, expires=expires)
    except Exception:
        return


def save_login_cookie(user_name: str, role: str, staff_id: str = "") -> None:
    """ログインCookieの保存を次回実行の冒頭まで先送りする。"""
    if not _cookie_enabled():
        return
    if role not in ("admin", "staff"):
        return
    st.session_state["_pending_login_cookie"] = (user_name, role, staff_id)


def clear_login_cookie() -> None:
    """ログインCookieの削除を次回実行の冒頭まで先送りする。"""
    if not _cookie_enabled():
        return
    st.session_state["_pending_cookie_clear"] = True
    st.session_state.pop("_pending_login_cookie", None)


def process_pending_cookie_ops() -> None:
    """先送りされたCookie保存・削除を実行する（st.rerun() は呼ばない）。"""
    pending_clear = st.session_state.pop("_pending_cookie_clear", False)
    pending_save = st.session_state.pop("_pending_login_cookie", None)

    if not _cookie_enabled():
        return

    controller = CookieController()

    if pending_clear:
        try:
            controller.remove(_COOKIE_NAME)
        except Exception:
            pass

    if pending_save:
        user_name, role, staff_id = pending_save
        if role in ("admin", "staff"):
            _write_login_cookie(controller, user_name, role, staff_id)


def restore_login_from_cookie() -> tuple[str, str, str] | None:
    """Cookie を検証し、有効なら (user_name, role, staff_id) を返す。"""
    secret = _get_cookie_secret()
    if not secret:
        return None

    try:
        controller = CookieController()
        controller.refresh()
        token = controller.get(_COOKIE_NAME)
    except Exception:
        return None

    if not token or not isinstance(token, str):
        return None

    parts = token.rsplit("::", 1)
    if len(parts) != 2:
        return None

    payload, signature = parts
    expected_signature = _sign_payload(payload, secret)
    if not hmac.compare_digest(signature, expected_signature):
        return None

    fields = payload.split("::")
    if len(fields) != 4:
        return None

    user_name, role, staff_id, exp_str = fields
    if role not in ("admin", "staff"):
        return None

    try:
        exp = int(exp_str)
    except ValueError:
        return None

    if exp < int(time.time()):
        return None

    return user_name, role, staff_id
