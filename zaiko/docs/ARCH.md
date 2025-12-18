# アーキテクチャ（MVP）

## 技術選定
- Next.js (App Router) + TypeScript
- TailwindCSS
- Supabase
  - Auth: Google OAuth
  - DB: Postgres
  - Row Level Security: MVPは最小限（まずは全ログインユーザーOKでも可）
- Barcode scan: zxing-js/browser（推奨）
- Charts: recharts（軽くてラク）

## ディレクトリ構成（案）
app/
  (auth)/login/page.tsx
  dashboard/page.tsx
  products/page.tsx
  products/[id]/page.tsx
  scan/page.tsx
  inventory/page.tsx
  inventory/move/page.tsx
  orders/new/page.tsx
  orders/page.tsx
  orders/[id]/page.tsx
  reports/sales/page.tsx
lib/
  supabaseClient.ts
  auth.ts
  db.ts
  barcode.ts
  validators.ts
  format.ts
types/
  db.ts

## 権限（MVP）
- users.role: 'admin' | 'user'
- MVPは「ログイン済みは基本操作可」→ 後でadminだけ商品登録などに拡張
