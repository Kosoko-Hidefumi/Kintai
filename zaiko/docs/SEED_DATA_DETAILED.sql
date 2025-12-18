-- 詳細なテストデータ投入用SQL
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

-- 在庫データ（商品ごとにランダムな数量を設定）
INSERT INTO public.inventory (product_id, quantity)
SELECT 
  id,
  CASE 
    WHEN random() < 0.2 THEN 0  -- 20%の確率で在庫0
    WHEN random() < 0.4 THEN floor(random() * 10)::integer  -- 20%の確率で1-9個
    ELSE floor(random() * 50)::integer + 10  -- 60%の確率で10-59個
  END
FROM public.products
ON CONFLICT (product_id) DO UPDATE SET quantity = EXCLUDED.quantity;

-- 注文データの作成（過去30日分）
-- 注意: 実際のユーザーIDが必要なため、ログイン後にアプリケーション経由で作成することを推奨
-- 以下のSQLは、auth.usersに存在するユーザーIDを使用します

-- 注文データ作成用の関数
DO $$
DECLARE
  user_id_val uuid;
  order_id_val uuid;
  product_rec record;
  order_date date;
  item_count integer;
  total_amount_val integer;
BEGIN
  -- 最初のユーザーIDを取得（存在する場合）
  SELECT id INTO user_id_val FROM auth.users LIMIT 1;
  
  -- ユーザーが存在する場合のみ注文データを作成
  IF user_id_val IS NOT NULL THEN
    -- 過去30日分の注文を作成
    FOR i IN 1..30 LOOP
      order_date := CURRENT_DATE - (i - 1);
      
      -- 1日あたり0〜5件の注文
      FOR j IN 1..floor(random() * 5)::integer LOOP
        -- 注文を作成
        INSERT INTO public.orders (user_id, status, ordered_at, total_amount)
        VALUES (user_id_val, 'confirmed', order_date + (random() * interval '1 day'), 0)
        RETURNING id INTO order_id_val;
        
        -- 注文アイテムを作成（1〜5明細）
        item_count := floor(random() * 5)::integer + 1;
        total_amount_val := 0;
        
        FOR k IN 1..item_count LOOP
          -- ランダムな商品を選択
          SELECT * INTO product_rec 
          FROM public.products 
          ORDER BY random() 
          LIMIT 1;
          
          -- 数量（1〜5個）
          INSERT INTO public.order_items (order_id, product_id, quantity, unit_price_in, line_total)
          VALUES (
            order_id_val,
            product_rec.id,
            floor(random() * 5)::integer + 1,
            product_rec.price_in,
            product_rec.price_in * (floor(random() * 5)::integer + 1)
          );
          
          -- 合計金額を計算
          total_amount_val := total_amount_val + (product_rec.price_in * (floor(random() * 5)::integer + 1));
        END LOOP;
        
        -- 注文の合計金額を更新
        UPDATE public.orders SET total_amount = total_amount_val WHERE id = order_id_val;
      END LOOP;
    END LOOP;
  END IF;
END $$;

