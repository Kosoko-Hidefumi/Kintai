This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## 在庫注文管理システム

在庫管理と注文登録を行うWebアプリケーションです。

## セットアップ

### 環境変数の設定

1. `.env.local` ファイルをプロジェクトルートに作成します
2. 以下の環境変数を設定します：

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Supabaseプロジェクトの設定画面（Settings > API）から取得できます。

### Google OAuthの設定

1. Supabaseダッシュボードでプロジェクトを開く
2. Authentication > Providers に移動
3. Google プロバイダーを有効化
4. Google Cloud ConsoleでOAuth 2.0クライアントIDを作成
5. 作成したクライアントIDとシークレットをSupabaseに設定
6. 認証コールバックURLを設定: `https://your-project-ref.supabase.co/auth/v1/callback`
7. 開発環境の場合、ローカルURLも追加: `http://localhost:3000/auth/callback`

### データベーススキーマの適用

1. Supabaseダッシュボードでプロジェクトを開く
2. SQL Editor に移動
3. `docs/DB.md` の内容をコピーしてSQL Editorに貼り付け
4. Run ボタンをクリックして実行
5. テーブルが正常に作成されたことを確認（Table Editorで確認可能）

**注意**: 初回実行時は全てのテーブルと型が作成されます。既に存在する場合はエラーになることがありますが、`IF NOT EXISTS` 句により安全に実行できます。

### テストデータの投入

動作確認用のテストデータを投入する場合：

1. Supabaseダッシュボードで **SQL Editor** を開く
2. `docs/SEED_DATA.sql` の内容をコピーしてSQL Editorに貼り付け
3. **Run** ボタンをクリックして実行
4. 商品データと在庫データが作成されます

**注意**: 注文データ（売上データ）も作成する場合：

1. まずGoogleログインでユーザーを作成してください（`/login` からログイン）
2. Supabaseダッシュボードで **SQL Editor** を開く
3. `docs/SEED_DATA_ORDERS.sql` の内容をコピーしてSQL Editorに貼り付け
4. **Run** ボタンをクリックして実行
5. 過去30日分の注文データが作成されます

これで、ダッシュボードやレポートページで売上データを確認できるようになります。

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
