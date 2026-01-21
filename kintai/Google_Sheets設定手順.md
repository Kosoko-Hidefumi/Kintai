# Google Sheets設定手順

このドキュメントでは、勤怠管理アプリでGoogleスプレッドシートを使用するための設定手順を説明します。

## 目次
1. [Google Cloud Consoleでの設定](#1-google-cloud-consoleでの設定)
2. [サービスアカウントの作成](#2-サービスアカウントの作成)
3. [認証情報（JSONキー）のダウンロード](#3-認証情報jsonキーのダウンロード)
4. [Streamlit secrets.tomlの設定](#4-streamlit-secretstomlの設定)
5. [スプレッドシートの作成とシート準備](#5-スプレッドシートの作成とシート準備)
6. [サービスアカウントへの権限付与](#6-サービスアカウントへの権限付与)
7. [動作確認](#7-動作確認)

---

## 1. Google Cloud Consoleでの設定

### 1.1 プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 画面上部のプロジェクト選択ドロップダウンをクリック
3. 「新しいプロジェクト」をクリック
4. プロジェクト名を入力（例：`勤怠管理システム`）
5. 「作成」をクリック
6. 作成したプロジェクトを選択

### 1.2 Google Sheets APIの有効化

1. 左側のメニューから「APIとサービス」→「ライブラリ」を選択
2. 検索バーに「Google Sheets API」と入力
3. 「Google Sheets API」を選択
4. 「有効にする」ボタンをクリック

---

## 2. サービスアカウントの作成

### 2.1 サービスアカウントの作成

1. 左側のメニューから「APIとサービス」→「認証情報」を選択
2. 画面上部の「+ 認証情報を作成」をクリック
3. 「サービスアカウント」を選択

### 2.2 サービスアカウントの詳細設定

1. **サービスアカウント名**: 任意の名前を入力（例：`勤怠管理アプリ`）
2. **サービスアカウントID**: 自動生成されます（変更可能）
3. **説明**: 任意の説明を入力（例：`勤怠管理システム用のサービスアカウント`）
4. 「作成して続行」をクリック

### 2.3 ロールの割り当て（スキップ可能）

- このステップはスキップして「完了」をクリックしても問題ありません
- 後でスプレッドシートに直接権限を付与します

---

## 3. 認証情報（JSONキー）のダウンロード

### 3.1 キーの作成

1. 作成したサービスアカウントをクリック
2. 「キー」タブを選択
3. 「キーを追加」→「新しいキーを作成」をクリック
4. **キーのタイプ**: 「JSON」を選択
5. 「作成」をクリック

### 3.2 JSONファイルの保存

- JSONファイルが自動的にダウンロードされます
- ファイル名は `プロジェクト名-ランダム文字列.json` の形式です
- **重要**: このファイルは安全な場所に保管してください（Gitにコミットしないでください）

---

## 4. Streamlit secrets.tomlの設定

### 4.1 .streamlitディレクトリの作成

プロジェクトルートに `.streamlit` ディレクトリを作成します：

**Windows (PowerShell):**
```powershell
mkdir .streamlit
```

**Mac/Linux:**
```bash
mkdir -p .streamlit
```

### 4.2 secrets.tomlファイルの作成

`.streamlit/secrets.toml` ファイルを作成し、ダウンロードしたJSONファイルの内容を以下の形式で記述します：

```toml
[gcp_service_account]
type = "service_account"
project_id = "あなたのプロジェクトID"
private_key_id = "プライベートキーID"
private_key = '''-----BEGIN PRIVATE KEY-----
（プライベートキーの内容）
-----END PRIVATE KEY-----'''
client_email = "サービスアカウントのメールアドレス@プロジェクトID.iam.gserviceaccount.com"
client_id = "クライアントID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "証明書URL"
```

### 4.3 JSONからTOMLへの変換方法

ダウンロードしたJSONファイルを開き、以下のように変換します：

**JSONファイルの例:**
```json
{
  "type": "service_account",
  "project_id": "my-project-123456",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "my-service@my-project-123456.iam.gserviceaccount.com",
  ...
}
```

**TOMLファイルへの変換:**
- `private_key` の値は、改行文字 `\n` を実際の改行に変換するか、`'''` で囲む必要があります
- 他の値はそのままコピーできます

### 4.4 簡単な変換方法（Pythonスクリプト）

以下のPythonスクリプトを使用して自動変換できます：

```python
import json
import toml

# JSONファイルを読み込む
with open('ダウンロードしたJSONファイル.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# TOML形式に変換
toml_data = {
    'gcp_service_account': json_data
}

# secrets.tomlに書き込む
with open('.streamlit/secrets.toml', 'w', encoding='utf-8') as f:
    toml.dump(toml_data, f)

print("secrets.tomlが作成されました！")
```

**実行方法:**
```bash
python convert_json_to_toml.py
```

---

## 5. スプレッドシートの作成とシート準備

### 5.1 スプレッドシートの作成

1. [Googleスプレッドシート](https://sheets.google.com/) にアクセス
2. 「空白」をクリックして新しいスプレッドシートを作成
3. スプレッドシート名を変更（例：`勤怠管理システム`）

### 5.2 スプレッドシートIDの取得

スプレッドシートのURLからIDを取得します：

```
https://docs.google.com/spreadsheets/d/[ここがスプレッドシートID]/edit
```

例：
- URL: `https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit`
- スプレッドシートID: `1a2b3c4d5e6f7g8h9i0j`

### 5.3 シートの作成と準備

#### 5.3.1 attendance_logsシートの作成

1. スプレッドシートの下部にある「シート1」を右クリック
2. 「名前を変更」を選択
3. 名前を `attendance_logs` に変更
4. 1行目に以下のヘッダーを入力：

| A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|
| event_id | date | staff_name | type | start_time | end_time | duration_hours | day_equivalent | fiscal_year | remarks |

#### 5.3.2 bulletin_boardシートの作成

1. 左下の「+」ボタンをクリックして新しいシートを追加
2. シート名を `bulletin_board` に変更
3. 1行目に以下のヘッダーを入力：

| A | B | C | D |
|---|---|---|---|
| timestamp | author | title | content |


---

## 6. サービスアカウントへの権限付与

### 6.1 サービスアカウントのメールアドレスを確認

サービスアカウントのメールアドレスは、以下の2つの方法で確認できます：

#### 方法1: テーブルから直接確認（簡単）

1. Google Cloud Consoleの「サービスアカウント」ページで、サービスアカウントの一覧テーブルを確認
2. 「メール」列に表示されているメールアドレスをコピー
   - 例：`id-165@arctic-badge-484907-n8.iam.gserviceaccount.com`
   - このメールアドレスをクリックすると詳細ページが開きます

#### 方法2: 詳細ページから確認

1. サービスアカウントの一覧テーブルで、メールアドレスをクリックするか、「操作」列の「⋮」（三点リーダー）をクリック
2. 「詳細を表示」または「編集」を選択
3. サービスアカウントの詳細ページが開きます
4. 「詳細」タブ（または「基本情報」タブ）で「メール」を確認
   - 例：`my-service@my-project-123456.iam.gserviceaccount.com`

**注意**: どちらの方法でも同じメールアドレスが表示されます。テーブルから直接コピーする方が簡単です。

### 6.2 スプレッドシートへの共有設定

1. 作成したスプレッドシートを開く
2. 右上の「共有」ボタンをクリック
3. 「ユーザーやグループを追加」欄に、サービスアカウントのメールアドレスを入力
4. **権限**: 「編集者」を選択
5. 「送信」をクリック
   - **注意**: 「リンクを知っている全員に通知」のチェックは外しておきます

### 6.3 権限の確認

サービスアカウントのメールアドレスが共有リストに表示され、権限が「編集者」になっていることを確認してください。

---

## 7. 動作確認

### 7.1 アプリでの設定

1. Streamlitアプリを起動：
   ```bash
   streamlit run app.py
   ```

2. サイドバーの「GoogleスプレッドシートID」欄に、取得したスプレッドシートIDを入力

3. 「ユーザーを選択」で職員を選択

### 7.2 テスト実行

1. **休暇申請ページ**でテストデータを入力して送信
2. スプレッドシートの `attendance_logs` シートにデータが追加されることを確認

3. **掲示板ページ**でテスト投稿を作成
4. スプレッドシートの `bulletin_board` シートに投稿が追加されることを確認

5. **カレンダーページ**でデータが表示されることを確認

### 7.3 エラーが発生した場合

#### 認証エラー
```
認証情報の取得に失敗しました
```
**対処法:**
- `.streamlit/secrets.toml` の内容を確認
- JSONファイルの内容が正しく変換されているか確認
- `private_key` の改行が正しく設定されているか確認

#### 権限エラー
```
スプレッドシートの取得に失敗しました
```
**対処法:**
- サービスアカウントのメールアドレスが正しく共有されているか確認
- 権限が「編集者」になっているか確認
- スプレッドシートIDが正しいか確認

#### シート名エラー
```
シート 'attendance_logs' の取得に失敗しました
```
**対処法:**
- シート名が正確に `attendance_logs` と `bulletin_board` になっているか確認
- 大文字小文字が一致しているか確認

---

## 8. セキュリティに関する注意事項

### 8.1 secrets.tomlの保護

- `.streamlit/secrets.toml` は `.gitignore` に含まれているため、Gitにコミットされません
- このファイルは機密情報を含むため、他人と共有しないでください

### 8.2 JSONキーの保護

- ダウンロードしたJSONキーファイルは安全に保管してください
- Gitリポジトリにコミットしないでください（`.gitignore` に `*.json` が含まれています）

### 8.3 サービスアカウントの権限

- サービスアカウントには必要最小限の権限のみを付与してください
- 不要になった場合は、スプレッドシートの共有設定から削除してください

---

## 9. トラブルシューティング

### Q: JSONファイルが見つからない
**A:** ブラウザのダウンロードフォルダを確認してください。ファイル名は `プロジェクト名-ランダム文字列.json` の形式です。

### Q: private_keyの改行がうまくいかない
**A:** TOMLファイルでは、`'''` で囲むことで複数行の文字列を記述できます。または、`\n` をそのまま使用することもできます。

### Q: スプレッドシートIDがわからない
**A:** スプレッドシートのURLの `/d/` と `/edit` の間の文字列がスプレッドシートIDです。

### Q: サービスアカウントのメールアドレスがわからない
**A:** Google Cloud Consoleの「認証情報」→「サービスアカウント」→ 該当アカウントの「詳細」タブで確認できます。

---

## 10. 参考リンク

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Sheets API ドキュメント](https://developers.google.com/sheets/api)
- [Streamlit secrets管理](https://docs.streamlit.io/library/advanced-features/secrets-management)
- [gspread ドキュメント](https://gspread.readthedocs.io/)

---

以上で設定は完了です。問題が発生した場合は、エラーメッセージを確認し、上記のトラブルシューティングを参照してください。
