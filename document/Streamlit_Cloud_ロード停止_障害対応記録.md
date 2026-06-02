# Streamlit Cloud ロード停止・ローカル SSL 問題 — 障害対応記録

**記録日:** 2026-06-02  
**対象アプリ:** ハワイ大学システム（Kintai-clone）  
**Cloud URL:** `https://kintai-unfus92zx5nbevkpwvz6df.streamlit.app`  
**リポジトリ:** `https://github.com/Kosoko-Hidefumi/Kintai.git`  
**結果:** Streamlit Cloud 正常復旧（ユーザー確認済み）

---

## 1. 現象

| 環境 | 症状 |
|------|------|
| **ローカル（Windows）** | Google Sheets 接続失敗（`PermissionError(13)` / SSL 証明書エラー）。`streamlit run app.py` 単体起動で再現 |
| **Streamlit Cloud** | デプロイ済み URL を開くとロード画面のスピナーが終わらない（20 分以上）。別ブラウザでも同様 |
| **共有データ** | `events` シート読み込みで `'DataFrame' object has no attribute 'dtype'`（ローカル・Cloud 双方で発生しうる） |

---

## 2. 根本原因（複数が重なっていた）

### 2.1 ローカル専用の SSL 対策が Cloud にも入っていた（最終的な Cloud 停止の主因）

ローカル Windows 向けに追加した **`pip-system-certs`** と **`truststore`** を `requirements.txt` に含めていた。

- `pip-system-certs` は `.pth` 経由で **Python 起動のたびに** `truststore.inject_into_ssl()` を自動実行する
- `ssl_bootstrap.py` でも同様の注入を行っていた
- **Streamlit Cloud（Linux）** では OS 証明書がもともと正常なのに、SSL パッチが **二重注入** され、スクリプトが完了せず **無限ロード** になった

### 2.2 `importlib.reload(database)`（Cloud 停止の一因）

ローカル開発で古いモジュールキャッシュを避けるため `app.py` に追加した **`importlib.reload(database)`** が、Cloud 上では Streamlit の再実行のたびに `database` を reload し、内部状態が壊れて **起動が終わらない** 状態を招いた。

### 2.3 `events` シートの重複列名

スプレッドシートの `events` シートに `end_date |` と `end_date` など **正規化後に同名になる列** が共存していた。

- 旧 `read_events` は列名正規化後に `df[col].dtype` を参照
- 重複列では `df[col]` が Series ではなく DataFrame になり **AttributeError**
- ローカル作業中にシート構造が変わったため、**Cloud のコードを触っていなくても** 同じスプレッドシートを参照する Cloud 側でもエラーが表面化した

### 2.4 ローカル起動方法の問題（SSL と別件）

`streamlit run app.py` を **venv 外の Python** で実行すると、SSL 対策パッケージが効かず Google API 接続が失敗する。Cloud では発生しない。

---

## 3. 実施した修正

| コミット | 内容 |
|----------|------|
| `0e9d39c` | `ssl_bootstrap.py` 追加、`read_events` 重複列対応、`start-local.ps1` 追加、ドキュメント更新 |
| `2c6f5be` | **`importlib.reload(database)` を削除**（Cloud 無限ロード対策） |
| `c0df68e` | **`pip-system-certs` / `truststore` を `requirements.txt` から除外**。`ssl_bootstrap.py` を **Windows のみ** 実行。`start-local.ps1` でローカル専用インストール。`main()` を Streamlit 標準の直呼びに変更 |

### 修正後の役割分担

| 項目 | ローカル（Windows） | Streamlit Cloud（Linux） |
|------|---------------------|--------------------------|
| SSL 対策 | `start-local.ps1` が `pip-system-certs` / `truststore` を追加インストール。`ssl_bootstrap.py` が Windows 時のみ実行 | **何もしない**（`requirements.txt` に SSL パッケージなし） |
| 起動 | `.\start-local.ps1` 必須 | GitHub push → 自動デプロイ |
| 認証情報 | `.streamlit/secrets.toml` | Streamlit Cloud **Secrets** |

---

## 4. 復旧手順（再発時）

### Streamlit Cloud がスピナーのまま止まる場合

1. [share.streamlit.io](https://share.streamlit.io) にログイン
2. 対象アプリ（`kintai · master · app.py`）の **「︙」→ Reboot**
3. 2〜3 分待って URL を **強制リロード**（`Ctrl + Shift + R`）
4. ログ確認: **アプリ URL 右下「Manage app」→ Logs**（ダッシュボードの「︙」メニューに Logs はない）

### ローカルで Sheets 接続が失敗する場合

1. `Ctrl + C` で Streamlit 停止
2. `.\start-local.ps1` で再起動
3. ブラウザを `Ctrl + Shift + R` で強制リロード

---

## 5. 教訓・再発防止

1. **Windows 専用の依存関係は `requirements.txt` に入れない**  
   Cloud とローカルで OS が異なるため、ローカル専用パッケージは `start-local.ps1` や `requirements-local.txt` 等で分離する。

2. **`importlib.reload` を Streamlit アプリに入れない**  
   Streamlit は操作のたびにスクリプト全体を再実行する。reload は Cloud でハングの原因になる。

3. **ローカルと Cloud は同じスプレッドシートを共有する**  
   ローカルテストでシート列を増やすと、Cloud の古いコードでもエラーが出る。シート変更時は Cloud への push もセットで行う。

4. **ローカル起動は `.\start-local.ps1` に統一する**  
   `streamlit run app.py` 単体は venv / SSL の取り違えで失敗しやすい。

5. **デプロイ対象アプリを確認する**  
   ワークスペースに `kintai · master · app.py` と `kintai · master · kintai/app.py` など複数ある場合、URL とエントリポイントが一致しているか確認する。

---

## 6. 関連ファイル

| ファイル | 役割 |
|----------|------|
| `ssl_bootstrap.py` | Windows ローカル向け SSL 初期化（Cloud では no-op） |
| `start-local.ps1` | venv 起動 + ローカル専用 SSL パッケージインストール |
| `requirements.txt` | Cloud 共通依存（SSL パッケージは含めない） |
| `database.py` | `read_events` の重複列正規化（`_read_version: int = 2`） |
| `app.py` | 末尾で `main()` を直呼び |
| `起動方法.md` | ローカル起動手順・トラブルシューティング |

---

## 7. 参考: events シートで観測された列（調査時）

```
event_id, start_date, end_date |, title, description, color, start_time, end_time, end_date, event_type
```

`end_date |` と `end_date` の共存が旧コードの `.dtype` エラーを引き起こした。必要に応じてスプレッドシート側で `end_date |` 列を手動整理してもよい（コード側は重複列に耐えるよう修正済み）。
