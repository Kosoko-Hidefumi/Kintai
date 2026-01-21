r"""
GoogleサービスアカウントのJSON認証情報を
Streamlitのsecrets.toml形式に変換するスクリプト

使い方:
  1. コマンドライン引数で指定:
     python convert_json_to_toml.py "C:/Users/YourName/Downloads/project-123456.json"
  
  2. 対話形式で実行:
     python convert_json_to_toml.py
     実行後、JSONファイルのパスを入力
"""
import json
import os
import sys
from pathlib import Path

# Windowsでの文字コード問題を回避
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def convert_json_to_toml(json_file_path: str, output_dir: str = ".streamlit"):
    """
    JSON認証情報ファイルをTOML形式に変換
    
    Args:
        json_file_path: JSONファイルのパス
        output_dir: 出力ディレクトリ（デフォルト: .streamlit）
    """
    # JSONファイルを読み込む
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"エラー: ファイル '{json_file_path}' が見つかりません。")
        return False
    except json.JSONDecodeError as e:
        print(f"エラー: JSONファイルの形式が正しくありません: {e}")
        return False
    
    # 出力ディレクトリを作成
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # TOMLファイルの内容を構築
    toml_content = "[gcp_service_account]\n"
    
    for key, value in json_data.items():
        if key == "private_key":
            # private_keyは複数行文字列として扱う
            toml_content += f'{key} = """{value}"""\n'
        else:
            # その他の値は文字列として出力
            if isinstance(value, str):
                # 文字列内の特殊文字をエスケープ
                escaped_value = value.replace('"', '\\"')
                toml_content += f'{key} = "{escaped_value}"\n'
            else:
                toml_content += f'{key} = {value}\n'
    
    # secrets.tomlに書き込む
    output_file = output_path / "secrets.toml"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(toml_content)
        print(f"[OK] secrets.tomlが作成されました: {output_file}")
        print(f"\n以下の内容が設定されました:")
        print(f"  - project_id: {json_data.get('project_id', 'N/A')}")
        print(f"  - client_email: {json_data.get('client_email', 'N/A')}")
        return True
    except Exception as e:
        print(f"エラー: ファイルの書き込みに失敗しました: {e}")
        return False


def main():
    """メイン関数"""
    print("=" * 60)
    print("Googleサービスアカウント認証情報変換ツール")
    print("=" * 60)
    print()
    
    # コマンドライン引数から取得
    if len(sys.argv) > 1:
        json_file = sys.argv[1].strip().strip('"').strip("'")
    else:
        # 対話形式で入力
        print("JSONファイルのパスを入力してください。")
        print("例: C:/Users/YourName/Downloads/project-123456.json")
        print("    または、JSONファイルをドラッグ&ドロップしてEnterキーを押してください")
        print()
        json_file = input("JSONファイルのパス: ").strip().strip('"').strip("'")
    
    if not json_file:
        print("エラー: ファイルパスが入力されていません。")
        print("\n使い方:")
        print('  python convert_json_to_toml.py "C:/path/to/file.json"')
        return
    
    # ファイルパスの正規化（Windowsのパス対応）
    json_file = os.path.normpath(json_file)
    
    if not os.path.exists(json_file):
        print(f"エラー: ファイル '{json_file}' が見つかりません。")
        print("\n確認事項:")
        print("  - ファイルパスが正しいか確認してください")
        print("  - ファイル名にスペースが含まれる場合は、ダブルクォートで囲んでください")
        print('  例: python convert_json_to_toml.py "C:/Users/My Name/file.json"')
        return
    
    # 変換実行
    print(f"\nファイルを読み込んでいます: {json_file}")
    print("変換を開始します...")
    success = convert_json_to_toml(json_file)
    
    if success:
        print("\n" + "=" * 60)
        print("変換が完了しました！")
        print("=" * 60)
        print("\n次のステップ:")
        print("1. スプレッドシートを作成し、attendance_logsとbulletin_boardシートを準備")
        print("2. サービスアカウントのメールアドレスにスプレッドシートの編集権限を付与")
        print("3. アプリでスプレッドシートIDを設定して動作確認")
    else:
        print("\n変換に失敗しました。エラーメッセージを確認してください。")


if __name__ == "__main__":
    main()
