# Streamlit Cloud デプロイ問題の原因と解決策

## 🔴 発生した問題

**エラーメッセージ**: 「データがありません」

Streamlit Cloudでアプリをデプロイした際に、データファイル（`sample-data.csv`）が読み込めないエラーが発生しました。

## 🔍 原因の分析

### 問題の根本原因

**相対パスの解決方法の違い**

1. **ローカル環境での動作**
   - ローカルでは `streamlit run python/streamlit/app.py` を実行
   - 作業ディレクトリが `python/streamlit/` になる
   - `data/sample-data.csv` という相対パスが正しく解決される

2. **Streamlit Cloudでの動作**
   - Streamlit Cloudは `python/streamlit/app.py` をメインファイルとして指定
   - しかし、作業ディレクトリがリポジトリのルート（`/`）になる可能性がある
   - `data/sample-data.csv` という相対パスが正しく解決されない
   - 結果として、ファイルが見つからずエラーが発生

### コードの問題箇所

**修正前のコード**:
```python
@st.cache_data
def load_data():
    """CSVファイルを読み込む"""
    try:
        df = pd.read_csv("data/sample-data.csv")  # 相対パス
        # ...
```

**問題点**:
- 相対パス `"data/sample-data.csv"` は、現在の作業ディレクトリ（`os.getcwd()`）からの相対パス
- Streamlit Cloudでは作業ディレクトリが異なる可能性がある
- そのため、ファイルが見つからない

## ✅ 解決策

### 修正内容

**修正後のコード**:
```python
@st.cache_data
def load_data():
    """CSVファイルを読み込む"""
    import os
    # ファイルのパスを取得（app.pyからの相対パス）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "data", "sample-data.csv")
    
    try:
        df = pd.read_csv(data_path)  # 絶対パス
        # ...
```

### 解決のポイント

1. **`__file__`を使用**
   - `__file__`は現在のPythonファイル（`app.py`）のパスを指す
   - `os.path.abspath(__file__)`で絶対パスを取得
   - `os.path.dirname()`でディレクトリ部分を取得

2. **app.pyの場所を基準にパスを構築**
   - `app.py`は `python/streamlit/app.py` にある
   - `app.py`のディレクトリ（`python/streamlit/`）を基準に
   - `data/sample-data.csv` のパスを構築

3. **デバッグ情報の追加**
   - エラー時にパス情報を表示
   - 問題の特定が容易になる

## 📊 比較表

| 項目 | 修正前 | 修正後 |
|------|--------|--------|
| **パスの種類** | 相対パス（作業ディレクトリ基準） | 絶対パス（app.py基準） |
| **ローカル動作** | ✅ 正常 | ✅ 正常 |
| **Streamlit Cloud動作** | ❌ エラー | ✅ 正常 |
| **環境依存性** | あり（作業ディレクトリに依存） | なし（app.pyの場所に依存） |

## 🎯 学んだこと

### ベストプラクティス

1. **ファイルパスの扱い**
   - 相対パスは作業ディレクトリに依存するため、環境によって動作が変わる
   - `__file__`を使用して、スクリプトファイルの場所を基準にパスを構築する
   - これにより、どの環境でも一貫して動作する

2. **デバッグ情報の追加**
   - エラー時にパス情報を表示することで、問題の特定が容易になる
   - 本番環境でのトラブルシューティングに役立つ

3. **環境の違いを考慮**
   - ローカル環境とクラウド環境では動作が異なる可能性がある
   - デプロイ前に環境の違いを考慮した実装を行う

## 🔧 今後の対策

### 推奨される実装パターン

```python
import os
from pathlib import Path

# 方法1: os.pathを使用（今回の実装）
current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "data", "sample-data.csv")

# 方法2: pathlibを使用（よりモダン）
current_dir = Path(__file__).parent
data_path = current_dir / "data" / "sample-data.csv"
```

### チェックリスト

- [x] データファイルのパスを `__file__` 基準に変更
- [x] エラーハンドリングにデバッグ情報を追加
- [x] ローカル環境で動作確認
- [x] Streamlit Cloudで動作確認

## 📝 まとめ

**原因**: 相対パスが作業ディレクトリに依存していたため、Streamlit Cloudで正しく解決されなかった

**解決策**: `__file__`を使用してapp.pyの場所を基準に絶対パスでデータファイルを読み込むように変更

**結果**: ローカル環境とStreamlit Cloudの両方で正常に動作するようになった

## 🔗 関連ファイル

- `python/streamlit/app.py` - 修正されたメインファイル
- `python/streamlit/data/sample-data.csv` - データファイル
- `STREAMLIT_CLOUD_DEPLOY.md` - デプロイガイド

