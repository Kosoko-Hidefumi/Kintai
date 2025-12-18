export type Product = {
  id: string
  name: string
  sku: string | null
  jan: string | null
  price_in: number
  created_at: string
  updated_at: string
}

export type Inventory = {
  product_id: string
  quantity: number
  updated_at: string
}

export type InventoryMovement = {
  id: string
  product_id: string
  move_type: 'in' | 'out' | 'adjust'
  qty: number
  reason: string | null
  user_id: string | null
  created_at: string
}

export type OrderStatus = 'draft' | 'confirmed' | 'cancelled'

export type Order = {
  id: string
  user_id: string | null
  status: OrderStatus
  ordered_at: string
  total_amount: number
}

export type OrderItem = {
  id: string
  order_id: string
  product_id: string
  quantity: number
  unit_price_in: number
  line_total: number
}

export type AppUser = {
  id: string
  role: string
  created_at: string
}

