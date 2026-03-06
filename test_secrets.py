"""secrets.tomlの読み込みテスト"""
import streamlit as st

# Streamlitのsecretsをテスト
try:
    if hasattr(st, 'secrets'):
        print("secrets object exists")
        print(f"Type: {type(st.secrets)}")
        if hasattr(st.secrets, 'keys'):
            keys = list(st.secrets.keys())
            print(f"Keys: {keys}")
        if "spreadsheet_id" in st.secrets:
            print(f"spreadsheet_id: {st.secrets['spreadsheet_id']}")
        else:
            print("spreadsheet_id not found in secrets")
            # すべてのキーを確認
            if hasattr(st.secrets, '__dict__'):
                print(f"secrets.__dict__: {st.secrets.__dict__}")
except Exception as e:
    print(f"Error: {e}")
