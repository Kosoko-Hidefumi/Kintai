# FR 経費管理データ ダッシュボード

## プロジェクト概要

FR/Logistic.csvの経費管理データを可視化するStreamlitダッシュボードです。

## 環境設定

### venv環境の有効化

既存の`python/streamlit`ディレクトリのvenv環境を使用します。

#### Windows PowerShellの場合:
```powershell
cd python/streamlit
.\venv\Scripts\Activate.ps1
```

#### Windows CMDの場合:
```cmd
cd python\streamlit
venv\Scripts\activate.bat
```

### 必要なライブラリ

以下のライブラリが既にインストールされています：
- streamlit (1.51.0)
- pandas (2.3.3)
- numpy (2.3.4)
- plotly (6.4.0)
- matplotlib (3.10.7)
- seaborn (0.13.2)
- openpyxl (3.1.5)
- scipy (1.16.3)
- scikit-learn (1.7.2)

### アプリの実行

venv環境を有効化した後、以下のコマンドでアプリを実行します：

```powershell
# FRディレクトリから実行する場合
cd FR
streamlit run app.py

# または、python/streamlitディレクトリから実行する場合
cd python/streamlit
streamlit run FR/app.py
```

## プロジェクト構造

```
FR/
├── Logistic.csv              # 経費管理データ（CSV形式）
├── Logistic.xlsx             # 経費管理データ（Excel形式）
├── dashboard-design.md       # ダッシュボード設計書
├── README.md                 # このファイル
└── app.py                    # Streamlitアプリケーション（作成予定）
```

## データ構造

CSVファイルには以下のカラムが含まれています：
- Date: 日付
- Vendor: ベンダー/支払先
- Description: 説明
- EXP: 支出金額
- E&E Date: 支払期限日
- Faculty: 教員関連
- Official: 公式関連
- カテゴリ列: Travel, Per Diem, Bks/Jrnls/AV, EQUIP, Other, Commun., Supplies/Misc, Short-term consultants

## 実装計画

詳細は`dashboard-design.md`を参照してください。

### ステップ1: ミニマム版（50%機能）
- トップページ（概要ダッシュボード）
- 詳細データ探索ページ
- 基本的なフィルター機能

### ステップ2: 機能追加版（80%機能）
- 時系列分析ページ
- カテゴリ分析ページ
- ベンダー分析ページ

### ステップ3: 完全版（100%機能）
- 支出分析ページ
- 月別比較分析ページ
- カテゴリ×ベンダー分析ページ
- 高度な可視化機能

