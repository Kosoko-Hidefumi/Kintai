# 在庫注文管理システム PRD（MVP）

## 目的
- バーコードスキャンで商品を特定し、在庫の増減と注文（売上）登録を簡単にする
- 売上の可視化（期間推移・商品別）をダッシュボードで確認できるようにする

## スコープ（MVP）
### 必須
- Googleログイン（OAuth）
- ロール（admin / user）※MVPは実質 user でもOK、adminは後で拡張
- 商品マスタ（一覧/検索/詳細）
- バーコードスキャン（JAN/EAN-13を読み取って商品特定）
- 在庫管理（入庫/出庫/調整の記録 + 現在庫の表示）
- 注文登録（簡易：カート→確定）
- 売上集計（期間推移、商品別）
- ダッシュボード（主要KPI + グラフ）

### やらない（MVP外）
- 決済（不要）
- 返品・棚卸・複数倉庫
- 複雑な権限（細粒度RBAC）
- オフライン完全対応（PWAは後回し）

## 画面一覧
- /login
- /dashboard
- /products（一覧・検索）
- /products/[id]（詳細）
- /scan（カメラ起動→JAN読取→商品へ）
- /inventory（在庫一覧）
- /inventory/move（入庫/出庫/調整）
- /orders/new（カート）
- /orders（一覧）
- /orders/[id]（詳細）
- /reports/sales（売上）

## 主要フロー
- 出庫（販売）:
  scan → product特定 → 数量入力 → 出庫確定
  → inventory.quantity 減算
  → inventory_movements 記録
  → order + order_items 作成（同時でも、注文画面経由でもOK）

## 受け入れ条件（最小）
- Googleでログインできる
- /scanでJANを読み取れる（開発端末でカメラ許可）
- 読取JANが products.jan に一致したら商品詳細へ遷移
- 在庫を増減でき、在庫一覧に反映される
- 注文登録でき、注文一覧/詳細で参照できる
- ダッシュボードに売上合計/注文件数/売れ筋Topが出る
