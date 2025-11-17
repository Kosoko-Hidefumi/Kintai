# Streamlit ダッシュボード開発環境

このディレクトリには、データ可視化ダッシュボードを開発するためのStreamlit環境が構築されています。

## 環境のセットアップ

### venv環境のアクティベート

PowerShellの場合:
```powershell
.\venv\Scripts\Activate.ps1
```

コマンドプロンプトの場合:
```cmd
venv\Scripts\activate.bat
```

### ライブラリのインストール

既にインストール済みですが、必要に応じて再インストールできます:

```bash
pip install -r requirements.txt
```

## インストール済みライブラリ

- **streamlit** (>=1.28.0) - ダッシュボード開発フレームワーク
- **pandas** (>=2.0.0) - データ処理
- **numpy** (>=1.24.0) - 数値計算
- **matplotlib** (>=3.7.0) - データ可視化
- **seaborn** (>=0.12.0) - 統計的可視化
- **plotly** (>=5.14.0) - インタラクティブな可視化
- **openpyxl** (>=3.1.0) - Excelファイル読み込み
- **scipy** (>=1.10.0) - 統計分析

## Streamlitアプリの実行

venv環境をアクティベートした後、Streamlitアプリを実行できます:

```bash
streamlit run app.py
```

または、任意のPythonファイルを実行:

```bash
streamlit run your_script.py
```

## データファイル

- `data/sample-data.csv` - サンプルデータファイル

## 開発のヒント

1. Streamlitアプリは自動的にリロードされます（ファイルを保存すると自動更新）
2. ブラウザで `http://localhost:8501` が自動的に開きます
3. デバッグ情報はターミナルに表示されます



