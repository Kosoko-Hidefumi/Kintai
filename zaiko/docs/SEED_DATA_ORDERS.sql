-- 注文データ（売上データ）作成用SQL
-- 注意: このSQLを実行する前に、Googleログインでユーザーを作成しておく必要があります
-- SupabaseのSQL Editorで実行してください

-- 過去30日分の注文データを作成
DO $$
DECLARE
  user_id_val uuid;
  order_id_val uuid;
  product_rec record;
  order_date date;
  item_count integer;
  total_amount_val integer;
  quantity_val integer;
  line_total_val integer;
BEGIN
  -- 最初のユーザーIDを取得（Googleログインで作成されたユーザー）
  SELECT id INTO user_id_val FROM auth.users ORDER BY created_at DESC LIMIT 1;
  
  -- ユーザーが存在しない場合はエラーメッセージを表示
  IF user_id_val IS NULL THEN
    RAISE NOTICE 'ユーザーが見つかりません。まずGoogleログインでユーザーを作成してください。';
    RETURN;
  END IF;
  
  RAISE NOTICE 'ユーザーID: % で注文データを作成します', user_id_val;
  
  -- 過去30日分の注文を作成
  FOR i IN 1..30 LOOP
    order_date := CURRENT_DATE - (i - 1);
    
    -- 1日あたり0〜5件の注文（ランダム）
    FOR j IN 1..floor(random() * 5)::integer LOOP
      -- 注文を作成（合計金額は後で更新）
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
        quantity_val := floor(random() * 5)::integer + 1;
        line_total_val := product_rec.price_in * quantity_val;
        
        -- 注文アイテムを作成
        INSERT INTO public.order_items (order_id, product_id, quantity, unit_price_in, line_total)
        VALUES (
          order_id_val,
          product_rec.id,
          quantity_val,
          product_rec.price_in,
          line_total_val
        );
        
        -- 合計金額を累積
        total_amount_val := total_amount_val + line_total_val;
      END LOOP;
      
      -- 注文の合計金額を更新
      UPDATE public.orders SET total_amount = total_amount_val WHERE id = order_id_val;
      
      -- 在庫を減らす（出庫処理）
      -- 注文アイテムごとに在庫を更新
      FOR product_rec IN 
        SELECT product_id, quantity 
        FROM public.order_items 
        WHERE order_id = order_id_val
      LOOP
        -- 在庫を減らす（負の値にならないように）
        UPDATE public.inventory
        SET quantity = GREATEST(0, quantity - product_rec.quantity),
            updated_at = NOW()
        WHERE product_id = product_rec.product_id;
        
        -- 在庫移動履歴を記録
        INSERT INTO public.inventory_movements (product_id, move_type, qty, reason, user_id)
        VALUES (
          product_rec.product_id,
          'out',
          product_rec.quantity,
          '注文による出庫: ' || order_id_val::text,
          user_id_val
        );
      END LOOP;
    END LOOP;
  END LOOP;
  
  RAISE NOTICE '注文データの作成が完了しました';
END $$;

