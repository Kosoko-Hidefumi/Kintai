# 職場勤怠管理・掲示板アプリ

Streamlitを使用した職員5名向けの勤怠管理と情報共有を行うWebアプリケーションです。

## セットアップ手順

### 1. 仮想環境の作成と有効化

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. Google Sheets API認証情報の設定

1. Google Cloud Consoleでプロジェクトを作成
2. Google Sheets APIを有効化
3. サービスアカウントを作成し、認証情報（JSON）をダウンロード
4. `.streamlit/secrets.toml` を作成し、以下の形式で認証情報を設定：

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

または、認証情報JSONファイルを `credentials.json` として配置（.gitignoreに含まれています）

### 4. Googleスプレッドシートの準備

1. 新しいスプレッドシートを作成
2. 以下の2つのシートを作成：
   - `attendance_logs`（勤怠ログ）
   - `bulletin_board`（掲示板）
3. サービスアカウントのメールアドレスにスプレッドシートの編集権限を付与

### 5. アプリの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 機能

- 🗓 **カレンダー**: 全員の休暇予定を月間表示
- 📝 **休暇申請**: 休暇の申請と登録
- 📋 **掲示板**: 情報共有のための掲示板
- 📈 **管理者用集計**: 職員別の休暇取得状況の集計（管理者のみ）

## 年度設定

- 年度は7月1日〜翌年6月30日を1つの年度とします
- 例：2025年7月1日〜2026年6月30日は「2025年度」

## 時間換算

- 8時間 = 1日としてカウント
- 例：4時間の休暇取得 = 0.5日
