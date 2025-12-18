'use client'

import { useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { createClientComponentClient } from '@/lib/supabase/client'
import { Product } from '@/types/db'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface CartItem {
  product: Product
  quantity: number
}

export default function NewOrderPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<Product[]>([])
  const [cart, setCart] = useState<CartItem[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()
  const router = useRouter()
  const supabase = createClientComponentClient()

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([])
      return
    }

    setIsSearching(true)
    setError(null)

    try {
      const { data, error: searchError } = await supabase
        .from('products')
        .select('*')
        .or(`name.ilike.%${searchQuery.trim()}%,sku.ilike.%${searchQuery.trim()}%,jan.ilike.%${searchQuery.trim()}%`)
        .limit(10)

      if (searchError) {
        throw searchError
      }

      setSearchResults(data || [])
    } catch (err) {
      console.error('Error searching products:', err)
      setError('商品の検索に失敗しました')
    } finally {
      setIsSearching(false)
    }
  }

  const addToCart = (product: Product) => {
    const existingItem = cart.find(item => item.product.id === product.id)
    
    if (existingItem) {
      setCart(cart.map(item =>
        item.product.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ))
    } else {
      setCart([...cart, { product, quantity: 1 }])
    }

    setSearchQuery('')
    setSearchResults([])
  }

  const updateQuantity = (productId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId)
      return
    }

    setCart(cart.map(item =>
      item.product.id === productId
        ? { ...item, quantity }
        : item
    ))
  }

  const removeFromCart = (productId: string) => {
    setCart(cart.filter(item => item.product.id !== productId))
  }

  const calculateTotal = () => {
    return cart.reduce((sum, item) => {
      return sum + (item.product.price_in * item.quantity)
    }, 0)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (cart.length === 0) {
      setError('カートに商品がありません')
      return
    }

    startTransition(async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const userId = session?.user?.id || null

        const items = cart.map(item => ({
          productId: item.product.id,
          quantity: item.quantity,
          unitPrice: item.product.price_in,
        }))

        const response = await fetch('/api/orders/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId,
            items,
          }),
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || '注文の作成に失敗しました')
        }

        const { orderId } = await response.json()

        // 成功したら注文詳細ページにリダイレクト
        router.push(`/orders/${orderId}`)
        router.refresh()
      } catch (err) {
        console.error('Error creating order:', err)
        setError(err instanceof Error ? err.message : '注文の作成に失敗しました')
      }
    })
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
    }).format(price)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link
            href="/dashboard"
            className="text-blue-600 hover:text-blue-900 text-sm font-medium"
          >
            ← ダッシュボードに戻る
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">新規注文</h1>
          <p className="mt-2 text-gray-600">
            商品を検索してカートに追加してください
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左側: 商品検索 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 検索フォーム */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">商品検索</h2>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleSearch()
                    }
                  }}
                  placeholder="商品名、SKU、JANコードで検索..."
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                />
                <button
                  type="button"
                  onClick={handleSearch}
                  disabled={isSearching}
                  className="rounded-lg bg-blue-600 px-6 py-2 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isSearching ? '検索中...' : '検索'}
                </button>
              </div>

              {/* 検索結果 */}
              {searchResults.length > 0 && (
                <div className="mt-4 space-y-2">
                  {searchResults.map((product) => (
                    <div
                      key={product.id}
                      className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{product.name}</p>
                        <p className="text-xs text-gray-500">
                          {product.sku && `SKU: ${product.sku} `}
                          {product.jan && `JAN: ${product.jan}`}
                        </p>
                        <p className="text-sm text-gray-700 mt-1">{formatPrice(product.price_in)}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => addToCart(product)}
                        className="ml-4 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white font-medium hover:bg-blue-700 transition-colors"
                      >
                        追加
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {error && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* 右側: カート */}
          <div className="lg:col-span-1">
            <form onSubmit={handleSubmit}>
              <div className="bg-white rounded-lg shadow p-6 sticky top-4">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">カート</h2>

                {cart.length === 0 ? (
                  <p className="text-gray-500 text-sm">カートに商品がありません</p>
                ) : (
                  <div>
                    <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
                      {cart.map((item) => (
                        <div key={item.product.id} className="border-b border-gray-200 pb-3">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-900">{item.product.name}</p>
                              <p className="text-xs text-gray-500">{formatPrice(item.product.price_in)}</p>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeFromCart(item.product.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              削除
                            </button>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                              className="w-8 h-8 rounded border border-gray-300 text-gray-700 hover:bg-gray-50"
                            >
                              -
                            </button>
                            <input
                              type="number"
                              value={item.quantity}
                              onChange={(e) => updateQuantity(item.product.id, parseInt(e.target.value, 10) || 0)}
                              min="1"
                              className="w-16 text-center rounded border border-gray-300 px-2 py-1 text-sm"
                            />
                            <button
                              type="button"
                              onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                              className="w-8 h-8 rounded border border-gray-300 text-gray-700 hover:bg-gray-50"
                            >
                              +
                            </button>
                            <span className="ml-auto text-sm font-medium text-gray-900">
                              {formatPrice(item.product.price_in * item.quantity)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="border-t border-gray-200 pt-4">
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-lg font-semibold text-gray-900">合計</span>
                        <span className="text-2xl font-bold text-gray-900">
                          {formatPrice(calculateTotal())}
                        </span>
                      </div>

                      <button
                        type="submit"
                        disabled={isPending}
                        className="w-full rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {isPending ? '処理中...' : '注文を確定'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

