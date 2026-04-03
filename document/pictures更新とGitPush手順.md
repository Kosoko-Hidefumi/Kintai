# pictures フォルダ更新後の Git push 手順

研修医一覧の写真を `kintai/pictures/` に更新したあと、リモート（GitHub）へ反映するときの手順です。

## 前提

| 項目 | 内容 |
|------|------|
| リポジトリのルート | `kintai/`（本リポジトリのルート） |
| 写真の配置 | `kintai/pictures/` 以下（期別フォルダなど。既存構成に合わせる） |
| 除外されるもの | `.gitignore` により、`.thumbnail/`、`.webaxs_*`、`._*`、`.DS_Store` などはコミットされない |
| サイズ注意 | GitHub はファイル 100MB 超は不可。大量・巨大ファイルは分割や別保管を検討 |

## フォルダの入れ替え（例：56期を削除して60期を追加）

**この手順書で対応できます。** 作業の流れは次のとおりです。

1. エクスプローラなどで `pictures/56期研修医写真簿/`（※実際のフォルダ名に合わせる）を削除する。
2. `pictures/60期研修医写真簿/`（または運用している60期用フォルダ名）を追加し、画像を配置する。
3. リポジトリルートで `git status` を実行すると、**削除（deleted）・新規（untracked/added）** の両方が `pictures/` 配下に出ます。
4. ステージするときは、**削除も追加もまとめて拾う**コマンドが確実です。

```powershell
git add -A pictures/
```

`git add pictures/` だけでも環境によっては削除が拾えることがありますが、**入れ替え（削除＋追加）のときは `git add -A pictures/` を推奨**します。

5. その後は通常どおり `git commit` → `git push` です。

**フォルダ名について**：リポジトリ内の実名（例：`56期研修医写真簿`、`60期研修医写真簿`）に読み替えてください。

## 手順（毎回）

### 1. リポジトリのフォルダへ移動

PowerShell の例（パスは環境に合わせて変更）：

```powershell
cd D:\code4biz\kintai
```

### 2. 差分を確認

```powershell
git status
```

変更・追加された画像が `pictures/` 配下に表示されることを確認します。

### 3. コミットするファイルをステージ

**pictures のみ**をまとめてステージする場合（**追加・変更・削除をすべて含む**）：

```powershell
git add -A pictures/
```

追加・変更のみを対象にしたい場合（削除のステージに不安があるときは上の `-A` を使う）：

```powershell
git add pictures/
```

特定のサブフォルダだけの場合の例：

```powershell
git add pictures/59期研修医写真簿/
```

### 4. コミット

メッセージは分かりやすく英語または日本語で：

```powershell
git commit -m "研修医一覧: pictures を更新（59期など）"
```

### 5. リモートへ push

```powershell
git push origin master
```

ブランチ名が `main` のリポジトリの場合：

```powershell
git push origin main
```

現在のブランチを確認するには：

```powershell
git branch --show-current
```

## プッシュ前に動作確認したい場合（任意）

Streamlit を起動し、研修医一覧で写真が表示されるか確認：

```powershell
cd D:\code4biz\kintai
streamlit run app.py
```

## トラブル時

| 状況 | 対処の例 |
|------|-----------|
| `nothing to commit` | `pictures/` に実ファイルが無い、または既にコミット済み。`git status` で確認 |
| 大容量で push が遅い・失敗 | 画像を圧縮する、LFS の利用を検討、またはリポジトリ方針の見直し |
| 認証エラー | GitHub の Personal Access Token または SSH 鍵の設定を確認 |
| 他人の変更がある | `git pull` で取り込んでから再度 `git push`（競合があれば解消） |

```powershell
git pull origin master
# 競合解消後
git push origin master
```

## コピー用：最小コマンド列（PowerShell）

リポジトリルートで、内容確認 → 追加 → コミット → push まで一気に行う例：

```powershell
cd D:\code4biz\kintai
git status
git add -A pictures/
git commit -m "研修医一覧: pictures を更新（56期削除・60期追加）"
git push origin master
```

※ ブランチやリモート名は環境に合わせて読み替えてください。
