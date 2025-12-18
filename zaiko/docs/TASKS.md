# 実装タスク（PR単位）

## PR0: 初期セットアップ
- Next.js(App Router/TS) 作成
- Tailwind導入
- Supabaseプロジェクト作成（URL/ANON KEY）
- env設定
- lib/supabaseClient.ts 追加

受け入れ:
- / にアクセスしてビルドエラーなし

## PR1: 認証（Googleログイン）
- /login 作成
- Supabase Auth UI or 自前ボタンでGoogleログイン
- ログイン後 /dashboard へ
- 未ログインは保護ページから /login にリダイレクト

受け入れ:
- Googleでログイン→dashboard表示

## PR2: DBスキーマ反映 + 最小CRUD
- docs/DB.sql をSupabaseに適用
- products を一覧表示できる（まずは read only）
- products 検索（name/sku/jan）

受け入れ:
- /products で一覧・検索が動く

## PR3: バーコードスキャン
- /scan 追加
- カメラ起動 → EAN-13読取 → janで products 検索
- 見つかれば /products/[id] へ遷移
- 見つからない場合は通知

受け入れ:
- スキャン→商品が開く

## PR4: 在庫管理（入庫/出庫/調整）
- /inventory（一覧：商品名 + quantity）
- /inventory/move（商品選択 or jan入力 → qty → move_type → 確定）
- 確定で inventory.quantity を加減算し movementを記録

受け入れ:
- 入庫/出庫で数量が変わる
- movementsが残る

## PR5: 注文（売上）登録
- /orders/new カート
  - 商品検索/追加、数量変更、確定
- 確定で orders + order_items 作成、total_amount 計算
- /orders 一覧、/orders/[id] 詳細

受け入れ:
- 注文が作れて参照できる

## PR6: レポート + ダッシュボード
- /reports/sales：期間（7/30/90日）で
  - 日別売上推移（折れ線）
  - 商品別売上TOP（棒）
- /dashboard：
  - 売上合計（期間）
  - 注文件数
  - 売れ筋TOP3
  - 在庫少TOP3

受け入れ:
- 指標とグラフが表示される
