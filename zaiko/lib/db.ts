import { createServerComponentClient } from './supabase/server'
import { Product, Inventory, InventoryMovement, Order, OrderItem } from '@/types/db'

/**
 * 商品一覧を取得（検索対応）
 */
export async function getProducts(search?: string): Promise<Product[]> {
  const supabase = await createServerComponentClient()
  
  let query = supabase
    .from('products')
    .select('*')
    .order('created_at', { ascending: false })

  if (search && search.trim()) {
    const searchTerm = search.trim()
    query = query.or(`name.ilike.%${searchTerm}%,sku.ilike.%${searchTerm}%,jan.ilike.%${searchTerm}%`)
  }

  const { data, error } = await query

  if (error) {
    console.error('Error fetching products:', error)
    throw error
  }

  return data || []
}

/**
 * 商品詳細を取得
 */
export async function getProduct(id: string): Promise<Product | null> {
  const supabase = await createServerComponentClient()
  
  const { data, error } = await supabase
    .from('products')
    .select('*')
    .eq('id', id)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      // レコードが見つからない
      return null
    }
    console.error('Error fetching product:', error)
    throw error
  }

  return data
}

/**
 * JANコードで商品を検索
 */
export async function getProductByJan(jan: string): Promise<Product | null> {
  const supabase = await createServerComponentClient()
  
  const { data, error } = await supabase
    .from('products')
    .select('*')
    .eq('jan', jan)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      // レコードが見つからない
      return null
    }
    console.error('Error fetching product by JAN:', error)
    throw error
  }

  return data
}

/**
 * 在庫一覧を取得（商品情報と結合）
 */
export async function getInventory(): Promise<Array<Inventory & { product: Product }>> {
  const supabase = await createServerComponentClient()
  
  const { data, error } = await supabase
    .from('inventory')
    .select(`
      *,
      product:products(*)
    `)
    .order('updated_at', { ascending: false })

  if (error) {
    console.error('Error fetching inventory:', error)
    throw error
  }

  return (data || []).map((item: any) => ({
    ...item,
    product: item.product,
  }))
}

/**
 * 在庫を取得（商品ID指定）
 */
export async function getInventoryByProductId(productId: string): Promise<Inventory | null> {
  const supabase = await createServerComponentClient()
  
  const { data, error } = await supabase
    .from('inventory')
    .select('*')
    .eq('product_id', productId)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      // レコードが見つからない
      return null
    }
    console.error('Error fetching inventory:', error)
    throw error
  }

  return data
}

/**
 * 在庫移動を実行
 */
export async function moveInventory(
  productId: string,
  moveType: 'in' | 'out' | 'adjust',
  qty: number,
  reason: string | null,
  userId: string | null
): Promise<void> {
  const supabase = await createServerComponentClient()
  
  // トランザクション的に処理（SupabaseではRPC関数を使うか、複数クエリで処理）
  // まず現在の在庫を取得
  const currentInventory = await getInventoryByProductId(productId)
  const currentQty = currentInventory?.quantity || 0

  // 新しい数量を計算
  let newQty: number
  if (moveType === 'in') {
    newQty = currentQty + qty
  } else if (moveType === 'out') {
    newQty = currentQty - qty
  } else {
    // adjust: 調整（指定した数量に設定）
    newQty = qty
  }

  // 在庫が負の値にならないようにチェック（出庫時）
  if (moveType === 'out' && newQty < 0) {
    throw new Error('在庫が不足しています')
  }

  // 在庫を更新または作成
  const { error: inventoryError } = await supabase
    .from('inventory')
    .upsert({
      product_id: productId,
      quantity: newQty,
      updated_at: new Date().toISOString(),
    }, {
      onConflict: 'product_id',
    })

  if (inventoryError) {
    console.error('Error updating inventory:', inventoryError)
    throw inventoryError
  }

  // 在庫移動履歴を記録
  const { error: movementError } = await supabase
    .from('inventory_movements')
    .insert({
      product_id: productId,
      move_type: moveType,
      qty: moveType === 'adjust' ? qty : qty, // adjustの場合は調整後の数量
      reason: reason,
      user_id: userId,
    })

  if (movementError) {
    console.error('Error recording movement:', movementError)
    throw movementError
  }
}

/**
 * 在庫移動履歴を取得
 */
export async function getInventoryMovements(productId?: string): Promise<InventoryMovement[]> {
  const supabase = await createServerComponentClient()
  
  let query = supabase
    .from('inventory_movements')
    .select('*')
    .order('created_at', { ascending: false })

  if (productId) {
    query = query.eq('product_id', productId)
  }

  const { data, error } = await query

  if (error) {
    console.error('Error fetching movements:', error)
    throw error
  }

  return data || []
}

/**
 * 注文一覧を取得
 */
export async function getOrders(): Promise<Order[]> {
  const supabase = await createServerComponentClient()
  
  const { data, error } = await supabase
    .from('orders')
    .select('*')
    .order('ordered_at', { ascending: false })

  if (error) {
    console.error('Error fetching orders:', error)
    throw error
  }

  return data || []
}

/**
 * 注文詳細を取得（注文アイテム含む）
 */
export async function getOrder(id: string): Promise<(Order & { items: Array<OrderItem & { product: Product }> }) | null> {
  const supabase = await createServerComponentClient()
  
  const { data: order, error: orderError } = await supabase
    .from('orders')
    .select('*')
    .eq('id', id)
    .single()

  if (orderError) {
    if (orderError.code === 'PGRST116') {
      return null
    }
    console.error('Error fetching order:', orderError)
    throw orderError
  }

  const { data: items, error: itemsError } = await supabase
    .from('order_items')
    .select(`
      *,
      product:products(*)
    `)
    .eq('order_id', id)

  if (itemsError) {
    console.error('Error fetching order items:', itemsError)
    throw itemsError
  }

  return {
    ...order,
    items: (items || []).map((item: any) => ({
      ...item,
      product: item.product,
    })),
  }
}

/**
 * 注文を作成
 */
export async function createOrder(
  userId: string | null,
  items: Array<{ productId: string; quantity: number; unitPrice: number }>
): Promise<string> {
  const supabase = await createServerComponentClient()
  
  // 合計金額を計算
  const totalAmount = items.reduce((sum, item) => {
    return sum + (item.unitPrice * item.quantity)
  }, 0)

  // 注文を作成
  const { data: order, error: orderError } = await supabase
    .from('orders')
    .insert({
      user_id: userId,
      status: 'confirmed',
      total_amount: totalAmount,
    })
    .select('id')
    .single()

  if (orderError) {
    console.error('Error creating order:', orderError)
    throw orderError
  }

  // 注文アイテムを作成
  const orderItems = items.map(item => ({
    order_id: order.id,
    product_id: item.productId,
    quantity: item.quantity,
    unit_price_in: item.unitPrice,
    line_total: item.unitPrice * item.quantity,
  }))

  const { error: itemsError } = await supabase
    .from('order_items')
    .insert(orderItems)

  if (itemsError) {
    console.error('Error creating order items:', itemsError)
    throw itemsError
  }

  return order.id
}

/**
 * 期間内の売上合計を取得
 */
export async function getSalesTotal(days: number): Promise<number> {
  const supabase = await createServerComponentClient()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - days)
  
  const { data, error } = await supabase
    .from('orders')
    .select('total_amount')
    .eq('status', 'confirmed')
    .gte('ordered_at', startDate.toISOString())

  if (error) {
    console.error('Error fetching sales total:', error)
    throw error
  }

  return (data || []).reduce((sum, order) => sum + order.total_amount, 0)
}

/**
 * 期間内の注文件数を取得
 */
export async function getOrderCount(days: number): Promise<number> {
  const supabase = await createServerComponentClient()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - days)
  
  const { count, error } = await supabase
    .from('orders')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'confirmed')
    .gte('ordered_at', startDate.toISOString())

  if (error) {
    console.error('Error fetching order count:', error)
    throw error
  }

  return count || 0
}

/**
 * 日別売上推移を取得
 */
export async function getDailySales(days: number): Promise<Array<{ date: string; amount: number }>> {
  const supabase = await createServerComponentClient()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - days)
  
  const { data, error } = await supabase
    .from('orders')
    .select('ordered_at, total_amount')
    .eq('status', 'confirmed')
    .gte('ordered_at', startDate.toISOString())
    .order('ordered_at', { ascending: true })

  if (error) {
    console.error('Error fetching daily sales:', error)
    throw error
  }

  // 日別に集計
  const dailyMap = new Map<string, number>()
  
  ;(data || []).forEach(order => {
    const date = new Date(order.ordered_at).toISOString().split('T')[0]
    dailyMap.set(date, (dailyMap.get(date) || 0) + order.total_amount)
  })

  // 日付順にソートして返す
  return Array.from(dailyMap.entries())
    .map(([date, amount]) => ({ date, amount }))
    .sort((a, b) => a.date.localeCompare(b.date))
}

/**
 * 商品別売上TOPを取得
 */
export async function getTopProductsBySales(days: number, limit: number = 10): Promise<Array<{ product_id: string; product_name: string; total_sales: number; total_quantity: number }>> {
  const supabase = await createServerComponentClient()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - days)
  
  const { data, error } = await supabase
    .from('order_items')
    .select(`
      product_id,
      quantity,
      line_total,
      order:orders!inner(ordered_at, status),
      product:products(name)
    `)
    .eq('order.status', 'confirmed')
    .gte('order.ordered_at', startDate.toISOString())

  if (error) {
    console.error('Error fetching top products:', error)
    throw error
  }

  // 商品別に集計
  const productMap = new Map<string, { name: string; sales: number; quantity: number }>()
  
  ;(data || []).forEach((item: any) => {
    const productId = item.product_id
    const existing = productMap.get(productId) || { name: item.product?.name || '不明', sales: 0, quantity: 0 }
    productMap.set(productId, {
      name: existing.name,
      sales: existing.sales + item.line_total,
      quantity: existing.quantity + item.quantity,
    })
  })

  // 売上順にソートしてTOPを返す
  return Array.from(productMap.entries())
    .map(([product_id, data]) => ({
      product_id,
      product_name: data.name,
      total_sales: data.sales,
      total_quantity: data.quantity,
    }))
    .sort((a, b) => b.total_sales - a.total_sales)
    .slice(0, limit)
}

/**
 * 在庫少TOPを取得
 */
export async function getLowStockProducts(limit: number = 10): Promise<Array<{ product_id: string; product_name: string; quantity: number }>> {
  const supabase = await createServerComponentClient()
  
  const { data, error } = await supabase
    .from('inventory')
    .select(`
      product_id,
      quantity,
      product:products(name)
    `)
    .order('quantity', { ascending: true })
    .limit(limit)

  if (error) {
    console.error('Error fetching low stock products:', error)
    throw error
  }

  return (data || []).map((item: any) => ({
    product_id: item.product_id,
    product_name: item.product?.name || '不明',
    quantity: item.quantity,
  }))
}

