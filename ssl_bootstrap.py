"""Windows ローカル開発向け: Google API 接続前にシステム証明書を有効化する。

Streamlit Cloud (Linux) では OS 証明書がそのまま使えるため何もしない。
pip-system-certs を requirements.txt に入れると Cloud 起動時に truststore が
二重注入され、接続がハングする原因になることがある。
"""
import sys


def ensure_system_ssl_certs() -> None:
    if sys.platform != "win32":
        return

    try:
        import truststore

        truststore.inject_into_ssl()
        return
    except Exception:
        pass

    try:
        from pip._vendor import truststore as pip_truststore

        pip_truststore.inject_into_ssl()
    except Exception:
        pass


ensure_system_ssl_certs()
