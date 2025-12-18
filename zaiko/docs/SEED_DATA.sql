-- テストデータ投入用SQL
-- SupabaseのSQL Editorで実行してください

-- 商品データ（12件）
INSERT INTO public.products (name, sku, jan, price_in) VALUES
('コーラ 500ml', 'SKU-001', '4901234567890', 150),
('お茶 500ml', 'SKU-002', '4901234567891', 120),
('コーヒー 250ml', 'SKU-003', '4901234567892', 180),
('パン 食パン', 'SKU-004', '4901234567893', 250),
('牛乳 1L', 'SKU-005', '4901234567894', 200),
('卵 10個入り', 'SKU-006', '4901234567895', 300),
('りんご 1袋', 'SKU-007', '4901234567896', 450),
('バナナ 1房', 'SKU-008', '4901234567897', 200),
('チョコレート', 'SKU-009', '4901234567898', 100),
('クッキー', 'SKU-010', '4901234567899', 150),
('ヨーグルト', 'SKU-011', '4901234567900', 120),
('サンドイッチ', 'SKU-012', '4901234567901', 350)
ON CONFLICT (jan) DO NOTHING;

-- 在庫データ（商品IDを取得して設定）
-- まず商品IDを取得して在庫を設定
INSERT INTO public.inventory (product_id, quantity)
SELECT id, 
  CASE 
    WHEN random() < 0.2 THEN 0  -- 20%の確率で在庫0
    WHEN random() < 0.4 THEN floor(random() * 10)::integer  -- 20%の確率で1-9個
    ELSE floor(random() * 50)::integer + 10  -- 60%の確率で10-59個
  END
FROM public.products
ON CONFLICT (product_id) DO NOTHING;

-- 注文データ（売上データ）の作成
-- 注意: このSQLを実行する前に、Googleログインでユーザーを作成しておく必要があります
-- 詳細は docs/SEED_DATA_ORDERS.sql を参照してください

