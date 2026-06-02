"""Windows 等で Google API 接続前にシステム証明書を有効化する。"""


def ensure_system_ssl_certs() -> None:
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
