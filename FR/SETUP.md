# FR 経費管理データ ダッシュボード - 環境設定ガイド

## ✅ 環境確認結果

### Python環境
- **Pythonバージョン**: 3.12.0
- **venv環境**: `python/streamlit/venv` に存在
- **環境状態**: 正常（破損なし）

### インストール済みライブラリ

すべての必要なライブラリがインストールされています：

| ライブラリ | バージョン | 要件 | 状態 |
|-----------|----------|------|------|
| streamlit | 1.51.0 | >=1.28.0 | ✅ |
| pandas | 2.3.3 | >=2.0.0 | ✅ |
| numpy | 2.3.4 | >=1.24.0 | ✅ |
| plotly | 6.4.0 | >=5.14.0 | ✅ |
| matplotlib | 3.10.7 | >=3.7.0 | ✅ |
| seaborn | 0.13.2 | >=0.12.0 | ✅ |
| openpyxl | 3.1.5 | >=3.1.0 | ✅ |
| scipy | 1.16.3 | >=1.10.0 | ✅ |
| scikit-learn | 1.7.2 | >=1.3.0 | ✅ |

## 🚀 venv環境の有効化方法

### Windows PowerShellの場合

```powershell
# プロジェクトルートから実行
cd python/streamlit

# venv環境を有効化
.\venv\Scripts\Activate.ps1

# 有効化確認（プロンプトに(venv)が表示される）
python --version
```

**注意**: PowerShellの実行ポリシーでエラーが出る場合：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows CMDの場合

```cmd
# プロジェクトルートから実行
cd python\streamlit

# venv環境を有効化
venv\Scripts\activate.bat

# 有効化確認（プロンプトに(venv)が表示される）
python --version
```

### venv環境の無効化

```powershell
# PowerShell / CMD共通
deactivate
```

## 📦 ライブラリの再インストール（必要な場合）

venv環境を有効化した後、以下のコマンドでライブラリを再インストールできます：

```powershell
cd python/streamlit
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 🎯 アプリの実行方法

### 方法1: FRディレクトリから実行（推奨）

```powershell
# venv環境を有効化
cd python/streamlit
.\venv\Scripts\Activate.ps1

# FRディレクトリに移動
cd ..\..\FR

# アプリを実行（app.pyが作成された後）
streamlit run app.py
```

### 方法2: python/streamlitディレクトリから実行

```powershell
# venv環境を有効化
cd python/streamlit
.\venv\Scripts\Activate.ps1

# アプリを実行（app.pyがFRディレクトリに作成された場合）
streamlit run ..\..\FR\app.py
```

## 📁 プロジェクト構造

```
code4biz/
├── FR/
│   ├── Logistic.csv              # 経費管理データ（CSV形式）
│   ├── Logistic.xlsx             # 経費管理データ（Excel形式）
│   ├── dashboard-design.md       # ダッシュボード設計書
│   ├── README.md                 # プロジェクト説明
│   ├── SETUP.md                  # このファイル（環境設定ガイド）
│   └── app.py                    # Streamlitアプリケーション（作成予定）
│
└── python/
    └── streamlit/
        ├── venv/                  # 仮想環境
        ├── requirements.txt      # 依存ライブラリリスト
        └── app.py                # 既存のStreamlitアプリ（参考用）
```

## 🔍 トラブルシューティング

### 問題1: venv環境が有効化できない

**解決方法**:
```powershell
# PowerShellの実行ポリシーを確認
Get-ExecutionPolicy

# 実行ポリシーを変更（必要に応じて）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 問題2: ライブラリがインポートできない

**解決方法**:
```powershell
# venv環境が有効化されているか確認
python --version  # パスがvenv内のpythonを指しているか確認

# ライブラリを再インストール
.\venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
```

### 問題3: Streamlitが起動しない

**解決方法**:
```powershell
# Streamlitのバージョンを確認
streamlit --version

# Streamlitを再インストール
.\venv\Scripts\python.exe -m pip install --upgrade streamlit
```

## ✅ 次のステップ

環境設定が完了したら、以下のステップでダッシュボードを開発します：

1. ✅ 環境確認とvenv設定（完了）
2. ⏭️ CSVデータの読み込みと前処理ロジックの実装
3. ⏭️ ステップ1（ミニマム版）の実装
   - トップページ（概要ダッシュボード）
   - 詳細データ探索ページ
   - 基本的なフィルター機能

詳細は`dashboard-design.md`を参照してください。

