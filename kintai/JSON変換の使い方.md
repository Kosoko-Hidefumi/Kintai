# JSON認証情報変換ツールの使い方

`convert_json_to_toml.py`スクリプトを使って、GoogleサービスアカウントのJSON認証情報を`secrets.toml`形式に変換する方法を説明します。

## 方法1: コマンドライン引数で指定（推奨）

### Windows (PowerShell)の場合

```powershell
# 仮想環境をアクティベート
.\venv\Scripts\Activate.ps1

# JSONファイルのパスを指定して実行
python convert_json_to_toml.py "C:\Users\YourName\Downloads\project-123456-abc123.json"
```

**ファイルパスにスペースが含まれる場合:**
```powershell
python convert_json_to_toml.py "C:\Users\My Name\Downloads\project-123456.json"
```

**ファイルをドラッグ&ドロップする場合:**
1. PowerShellで `python convert_json_to_toml.py ` まで入力
2. エクスプローラーからJSONファイルをドラッグ&ドロップ
3. Enterキーを押す

### Mac/Linuxの場合

```bash
# 仮想環境をアクティベート
source venv/bin/activate

# JSONファイルのパスを指定して実行
python convert_json_to_toml.py "/Users/YourName/Downloads/project-123456-abc123.json"
```

## 方法2: 対話形式で実行

スクリプトを引数なしで実行すると、対話形式でファイルパスを入力できます：

```powershell
python convert_json_to_toml.py
```

実行後、以下のように表示されます：
```
============================================================
Googleサービスアカウント認証情報変換ツール
============================================================

JSONファイルのパスを入力してください。
例: C:\Users\YourName\Downloads\project-123456.json
    または、JSONファイルをドラッグ&ドロップしてEnterキーを押してください

JSONファイルのパス: 
```

ここで、JSONファイルのパスを入力するか、ファイルをドラッグ&ドロップしてEnterキーを押します。

## 実行例

### 例1: ダウンロードフォルダにあるJSONファイルを変換

```powershell
# Windowsの場合
python convert_json_to_toml.py "$env:USERPROFILE\Downloads\my-project-123456.json"
```

### 例2: デスクトップにあるJSONファイルを変換

```powershell
# Windowsの場合
python convert_json_to_toml.py "$env:USERPROFILE\Desktop\credentials.json"
```

### 例3: 相対パスで指定

```powershell
# プロジェクトフォルダ内にJSONファイルを配置した場合
python convert_json_to_toml.py ".\credentials.json"
```

## 実行結果

正常に変換されると、以下のように表示されます：

```
============================================================
Googleサービスアカウント認証情報変換ツール
============================================================

ファイルを読み込んでいます: C:\Users\YourName\Downloads\project-123456.json
変換を開始します...
✓ secrets.tomlが作成されました: .streamlit\secrets.toml

以下の内容が設定されました:
  - project_id: my-project-123456
  - client_email: my-service@my-project-123456.iam.gserviceaccount.com

============================================================
変換が完了しました！
============================================================

次のステップ:
1. スプレッドシートを作成し、attendance_logsとbulletin_boardシートを準備
2. サービスアカウントのメールアドレスにスプレッドシートの編集権限を付与
3. アプリでスプレッドシートIDを設定して動作確認
```

## よくあるエラーと対処法

### エラー1: ファイルが見つかりません

```
エラー: ファイル 'C:\path\to\file.json' が見つかりません。
```

**対処法:**
- ファイルパスが正しいか確認
- ファイル名のスペルミスがないか確認
- ファイルパスにスペースが含まれる場合は、ダブルクォートで囲む

### エラー2: JSONファイルの形式が正しくありません

```
エラー: JSONファイルの形式が正しくありません: ...
```

**対処法:**
- JSONファイルが正しくダウンロードされているか確認
- ファイルが破損していないか確認
- Google Cloud Consoleから再度ダウンロード

### エラー3: ファイルの書き込みに失敗しました

```
エラー: ファイルの書き込みに失敗しました: ...
```

**対処法:**
- `.streamlit`ディレクトリの書き込み権限を確認
- ファイルが他のプログラムで開かれていないか確認

## 確認方法

変換が成功したら、以下のコマンドで`secrets.toml`の内容を確認できます：

```powershell
# Windowsの場合
type .streamlit\secrets.toml

# Mac/Linuxの場合
cat .streamlit/secrets.toml
```

**注意**: `secrets.toml`には機密情報が含まれているため、他人と共有しないでください。

## 次のステップ

変換が完了したら：

1. ✅ `.streamlit/secrets.toml`が作成されていることを確認
2. 📊 スプレッドシートを作成し、`attendance_logs`と`bulletin_board`シートを準備
3. 🔐 サービスアカウントのメールアドレスにスプレッドシートの編集権限を付与
4. 🚀 アプリでスプレッドシートIDを設定して動作確認
