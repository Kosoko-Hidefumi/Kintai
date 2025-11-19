# Streamlit Cloud デプロイガイド

## 📋 前提条件

- ✅ GitHubリポジトリが作成済み
- ✅ リポジトリURL: `https://github.com/Kosoko-Hidefumi/streamlit-dashboard.git`
- ✅ Streamlitアプリが完成している

## 🚀 デプロイ手順

### ステップ1: Streamlit Cloudにアクセス

1. **Streamlit Cloudにアクセス**
   - https://share.streamlit.io/ にアクセス
   - または https://streamlit.io/cloud から「Sign up」をクリック

2. **GitHubアカウントでログイン**
   - 「Sign in with GitHub」をクリック
   - GitHubアカウントで認証
   - Streamlit Cloudへのアクセス権限を許可

### ステップ2: 新しいアプリを作成

1. **「New app」ボタンをクリック**
   - Streamlit Cloudのダッシュボードから「New app」をクリック

2. **リポジトリを選択**
   - **Repository**: `Kosoko-Hidefumi/streamlit-dashboard` を選択
   - リポジトリが表示されない場合は、GitHubアカウントの認証を確認してください

3. **ブランチを選択**
   - **Branch**: `master` を選択

4. **メインファイルのパスを指定**
   - **Main file path**: `python/streamlit/app.py`
   - ⚠️ 重要: リポジトリのルートからの相対パスを指定

5. **Advanced settings（オプション）**
   - **Python version**: 3.12（または最新）
   - **Secrets**: 必要に応じて環境変数を設定（今回は不要）

### ステップ3: デプロイ設定の確認

Streamlit Cloudは自動的に以下を検出します：
- ✅ `requirements.txt` の場所: `python/streamlit/requirements.txt`
- ✅ データファイル: `python/streamlit/data/sample-data.csv`

### ステップ4: デプロイを開始

1. **「Deploy!」ボタンをクリック**
2. デプロイが開始されます（数分かかります）
3. デプロイが完了すると、アプリのURLが表示されます
   - 例: `https://streamlit-dashboard-xxxxx.streamlit.app`

## ⚙️ 設定の詳細

### メインファイルのパス

リポジトリの構造：
```
streamlit-dashboard/
├── python/
│   └── streamlit/
│       ├── app.py          ← メインファイル
│       ├── requirements.txt
│       └── data/
│           └── sample-data.csv
```

**設定**: `python/streamlit/app.py`

### Requirements.txtのパス

Streamlit Cloudは自動的に `requirements.txt` を検索しますが、サブディレクトリにある場合は明示的に指定する必要がある場合があります。

現在の構造では、`python/streamlit/requirements.txt` が自動的に検出されるはずです。

### データファイルのパス

アプリ内でデータファイルを読み込む際のパス：
```python
df = pd.read_csv("data/sample-data.csv")
```

このパスは、`app.py` からの相対パスなので、`python/streamlit/` ディレクトリ内の `data/sample-data.csv` を指します。

## 🔧 トラブルシューティング

### デプロイが失敗する場合

1. **Requirements.txtの確認**
   - すべての依存パッケージが正しく記載されているか確認
   - バージョン指定が正しいか確認

2. **ファイルパスの確認**
   - メインファイルのパスが正しいか確認
   - データファイルのパスが正しいか確認

3. **ログの確認**
   - Streamlit Cloudのダッシュボードで「Logs」を確認
   - エラーメッセージを確認

### データファイルが見つからない場合

データファイルのパスを絶対パスに変更する必要がある場合があります：

```python
# app.py内で
import os

# データファイルのパスを取得
data_path = os.path.join(os.path.dirname(__file__), "data", "sample-data.csv")
df = pd.read_csv(data_path)
```

### パッケージのインストールエラー

`requirements.txt` に問題がある場合：

1. バージョン指定を緩和する
2. 互換性のないパッケージを確認する
3. 必要に応じて `packages.txt` を作成する

## 📝 デプロイ後の確認事項

### ✅ デプロイ成功の確認

1. **アプリが正常に起動するか**
   - URLにアクセスしてアプリが表示されるか確認

2. **データが正しく読み込まれるか**
   - ダッシュボードが正常に表示されるか確認

3. **すべての機能が動作するか**
   - フィルター機能
   - グラフの表示
   - データテーブル

### 🔄 更新方法

コードを更新したら：

1. **変更をコミット**
   ```powershell
   git add .
   git commit -m "更新内容"
   git push origin master
   ```

2. **Streamlit Cloudが自動的に再デプロイ**
   - GitHubにプッシュすると、自動的に再デプロイが開始されます
   - 「Always rerun」オプションで手動で再デプロイも可能

## 🔗 参考リンク

- [Streamlit Cloud公式ドキュメント](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Cloudダッシュボード](https://share.streamlit.io/)
- [デプロイガイド](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

## 📌 重要な注意事項

1. **無料プランの制限**
   - アプリは一定時間非アクティブになるとスリープします
   - 再アクセス時に自動的に起動します

2. **データファイルのサイズ**
   - 大きなデータファイルはGitHubにコミットしないことを推奨
   - 必要に応じて外部ストレージを使用

3. **シークレット情報**
   - APIキーなどの機密情報は「Secrets」機能を使用
   - コードに直接書かない

4. **パフォーマンス**
   - データのキャッシュを適切に使用（`@st.cache_data`）
   - 大量のデータ処理は最適化する

