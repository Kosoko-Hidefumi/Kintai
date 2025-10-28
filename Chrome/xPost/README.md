# X Post to Slack/Notion Chrome Extension

X(Twitter)の有益なポストを簡単に Slack と Notion に転送する Google Chrome 拡張機能

## 機能概要

- X投稿の自動取得（テキスト、URL、投稿者情報、投稿日時）
- ワンクリックでSlackチャンネルに送信
- ワンクリックでNotionデータベースに追加
- 両方のサービスに同時送信可能

## セットアップ

### 1. 拡張機能のインストール

1. Chrome で `chrome://extensions/` を開く
2. 右上の「デベロッパーモード」を有効化
3. 「パッケージ化されていない拡張機能を読み込む」をクリック
4. このフォルダ（`Chrome/xPost`）を選択

### 2. Slack の設定

#### Botの作成とトークンの取得

1. [Slack API](https://api.slack.com/apps) にアクセス
2. 「Create New App」をクリック
3. 「From scratch」を選択
4. App名とWorkspaceを設定して「Create App」をクリック
5. 左メニューから「OAuth & Permissions」を選択
6. 「Scopes」セクションの「Bot Token Scopes」に以下を追加：
   - `chat:write` - メッセージ送信
   - `chat:write.public` - パブリックチャンネルへの書き込み
7. ページ上部の「Install to Workspace」をクリック
8. 「xoxb-」で始まる「Bot User OAuth Token」をコピー

#### チャンネルIDの取得

1. Slackで対象チャンネルを開く
2. チャンネル名をクリック → 「その他」→「リンクの追加」→「チャンネル固有のリンクをコピー」
3. URLから最後の部分（例：`C1234567890`）がChannel ID

### 3. Notion の設定

#### Integrationの作成とトークンの取得

1. [Notion Integrations](https://www.notion.so/my-integrations) にアクセス
2. 「+ New integration」をクリック
3. 名前を設定して「Submit」をクリック
4. 「Internal Integration Token」をコピー（「secret_」で始まる）

#### データベースの準備とIDの取得

1. Notionで新規データベースを作成（または既存のデータベースを使用）
2. データベースのプロパティを設定：
   - **投稿テキスト**（Title または Rich Text）
   - **投稿URL**（URL）
   - **投稿者**（Text）
   - **投稿日時**（Date）
3. データベースの設定で「接続を追加」→ 作成した Integration を選択
4. データベースのURLから32桁のIDをコピー
   - 例：`https://www.notion.so/[ワークスペース]/32桁のUUID?v=...`

### 4. 拡張機能の設定

1. Chrome のツールバーで拡張機能のアイコンをクリック
2. 設定画面で以下を入力：
   - **Slack Token**: Bot User OAuth Token
   - **Slack Channel ID**: チャンネルID
   - **Notion Token**: Internal Integration Token
   - **Notion Database ID**: データベースID
3. 各サービスの「テスト」ボタンで接続確認
4. 「設定を保存」をクリック

## 使用方法

### 基本的な使い方

1. [x.com](https://x.com) にアクセス
2. 各投稿のブックマークアイコンの左に表示される転送アイコンをクリック
3. 投稿が自動的に Slack と Notion に送信される

### 送信先の選択

- **Slack のみ**: Slack設定のみが完了している場合
- **Notion のみ**: Notion設定のみが完了している場合
- **両方**: 両方の設定が完了している場合、両方に送信

## 送信されるデータ

- **投稿テキスト**: X投稿の本文
- **投稿URL**: 元の投稿へのリンク
- **投稿者**: 投稿者の情報
- **投稿日時**: 投稿の作成日時

## トラブルシューティング

### アイコンが表示されない

#### ステップ1: 拡張機能のリロード
1. `chrome://extensions/` を開く
2. X Post to Slack/Notion の拡張機能を探す
3. 🔄（リロード）ボタンをクリック

#### ステップ2: ページのリロード
1. X (x.com) でページをリロード（F5）

#### ステップ3: デバッグコンソールで確認
1. X (x.com) でF12キーを押してデベロッパーツールを開く
2. 「Console」タブを開く
3. 以下のメッセージが表示されているか確認：
   ```
   [XPost] Content script loaded
   [XPost] Starting initial scan...
   [XPost] 投稿数: 10
   ```
4. メッセージが表示されない場合：
   - 拡張機能の「background.js」にエラーがないか確認（chrome://extensions/ → エラーの詳細）
   - content.jsファイルが存在するか確認

#### ステップ4: 要素の確認
コンソールで以下を実行して投稿要素を確認：
```javascript
document.querySelectorAll('[data-testid="tweet"]').length
// または
document.querySelectorAll('article').length
```

#### ステップ5: 手動でアイコンを追加（テスト用）
コンソールで以下を実行：
```javascript
const icon = document.createElement('div');
icon.style.cssText = 'width: 36px; height: 36px; background: #1d9bf0; cursor: pointer; border-radius: 50%;';
document.body.appendChild(icon);
```

### 送信が失敗する

- 設定画面で正しく設定されているか確認
- 「テスト」ボタンで接続確認
- ブラウザのコンソール（F12）でエラーメッセージを確認

### Notionにデータが表示されない

- Notion Integration がデータベースに接続されているか確認
- データベースのプロパティ名が正しいか確認（「投稿テキスト」「投稿URL」「投稿者」「投稿日時」）

## ファイル構成

```
xPost/
├── manifest.json       # 拡張機能の設定
├── background.js       # バックグラウンド処理（API通信）
├── content.js          # Xサイトへの注入スクリプト
├── popup.html          # 設定画面のHTML
├── popup.css           # 設定画面のスタイル
├── popup.js            # 設定画面のJavaScript
├── icons/              # アイコンファイル
└── README.md           # このファイル
```

## 開発者向け情報

### 技術スタック

- **Manifest V3**: Chrome 拡張機能の最新仕様
- **Content Scripts**: Xサイトへのスクリプト注入
- **Service Worker**: バックグラウンド処理
- **Slack Web API**: メッセージ送信
- **Notion API**: データベースへの追加

### カスタマイズ

- Content Script を編集して取得データを変更
- Background Service Worker を編集して送信フォーマットを変更
- Popup UI を編集して設定項目を追加

## ライセンス

このプロジェクトは個人利用・商用利用を問わず自由に使用できます。

## 更新履歴

### Version 1.0.0 (2025)
- 初回リリース
- X投稿のSlack/Notionへの転送機能


