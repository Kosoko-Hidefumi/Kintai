'use client'

import { useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { createClientComponentClient } from '@/lib/supabase/client'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

export default function InventoryMovePage() {
  const [searchType, setSearchType] = useState<'product' | 'jan'>('product')
  const [productId, setProductId] = useState('')
  const [janCode, setJanCode] = useState('')
  const [moveType, setMoveType] = useState<'in' | 'out' | 'adjust'>('in')
  const [quantity, setQuantity] = useState('')
  const [reason, setReason] = useState('')
  const [productName, setProductName] = useState<string | null>(null)
  const [currentQuantity, setCurrentQuantity] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()
  const router = useRouter()
  const supabase = createClientComponentClient()

  const handleSearchProduct = async () => {
    try {
      setError(null)
      setProductName(null)
      setCurrentQuantity(null)

      if (searchType === 'product' && !productId.trim()) {
        setError('商品IDを入力してください')
        return
      }

      if (searchType === 'jan' && !janCode.trim()) {
        setError('JANコードを入力してください')
        return
      }

      let targetProductId = productId

      // JANコードで検索する場合
      if (searchType === 'jan') {
        const { data: product, error: productError } = await supabase
          .from('products')
          .select('id, name')
          .eq('jan', janCode.trim())
          .single()

        if (productError || !product) {
          setError('商品が見つかりませんでした')
          return
        }

        targetProductId = product.id
        setProductId(product.id)
        setProductName(product.name)
      } else {
        // 商品IDで検索する場合
        const { data: product, error: productError } = await supabase
          .from('products')
          .select('id, name')
          .eq('id', productId.trim())
          .single()

        if (productError || !product) {
          setError('商品が見つかりませんでした')
          return
        }

        setProductName(product.name)
      }

      // 現在の在庫を取得
      const { data: inventory, error: inventoryError } = await supabase
        .from('inventory')
        .select('quantity')
        .eq('product_id', targetProductId)
        .single()

      if (inventoryError && inventoryError.code !== 'PGRST116') {
        setError('在庫情報の取得に失敗しました')
        return
      }

      setCurrentQuantity(inventory?.quantity || 0)
    } catch (err) {
      console.error('Error searching product:', err)
      setError('商品の検索に失敗しました')
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    if (!productId) {
      setError('商品を検索してください')
      return
    }

    const qty = parseInt(quantity, 10)
    if (isNaN(qty) || qty <= 0) {
      setError('数量は1以上の数値を入力してください')
      return
    }

    startTransition(async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const userId = session?.user?.id || null

        // Server Actionの代わりに直接APIを呼び出す
        const response = await fetch('/api/inventory/move', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            productId,
            moveType,
            qty,
            reason: reason.trim() || null,
            userId,
          }),
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || '在庫移動に失敗しました')
        }

        // 成功したら在庫一覧にリダイレクト
        router.push('/inventory')
        router.refresh()
      } catch (err) {
        console.error('Error moving inventory:', err)
        setError(err instanceof Error ? err.message : '在庫移動に失敗しました')
      }
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link
            href="/inventory"
            className="text-blue-600 hover:text-blue-900 text-sm font-medium"
          >
            ← 在庫一覧に戻る
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">在庫移動</h1>
          <p className="mt-2 text-gray-600">
            商品の入庫・出庫・調整を行います
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 商品検索 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                検索方法
              </label>
              <div className="flex gap-4 mb-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="product"
                    checked={searchType === 'product'}
                    onChange={(e) => {
                      setSearchType(e.target.value as 'product')
                      setProductId('')
                      setProductName(null)
                      setCurrentQuantity(null)
                    }}
                    className="mr-2"
                  />
                  商品ID
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="jan"
                    checked={searchType === 'jan'}
                    onChange={(e) => {
                      setSearchType(e.target.value as 'jan')
                      setJanCode('')
                      setProductName(null)
                      setCurrentQuantity(null)
                    }}
                    className="mr-2"
                  />
                  JANコード
                </label>
              </div>

              <div className="flex gap-2">
                {searchType === 'product' ? (
                  <input
                    type="text"
                    value={productId}
                    onChange={(e) => setProductId(e.target.value)}
                    placeholder="商品IDを入力"
                    className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  />
                ) : (
                  <input
                    type="text"
                    value={janCode}
                    onChange={(e) => setJanCode(e.target.value)}
                    placeholder="JANコードを入力"
                    className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  />
                )}
                <button
                  type="button"
                  onClick={handleSearchProduct}
                  className="rounded-lg bg-gray-600 px-6 py-2 text-white font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
                >
                  検索
                </button>
              </div>

              {productName && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm font-medium text-blue-900">
                    商品名: {productName}
                  </p>
                  {currentQuantity !== null && (
                    <p className="text-sm text-blue-700 mt-1">
                      現在の在庫: {currentQuantity.toLocaleString()}
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* 移動種別 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                移動種別
              </label>
              <select
                value={moveType}
                onChange={(e) => setMoveType(e.target.value as 'in' | 'out' | 'adjust')}
                className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <option value="in">入庫</option>
                <option value="out">出庫</option>
                <option value="adjust">調整</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">
                {moveType === 'in' && '在庫を増やします'}
                {moveType === 'out' && '在庫を減らします'}
                {moveType === 'adjust' && '在庫を指定した数量に設定します'}
              </p>
            </div>

            {/* 数量 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                数量
              </label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="数量を入力"
                min="1"
                required
                className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              />
            </div>

            {/* 理由 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                理由（任意）
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="移動理由を入力（例: 入荷、出荷、棚卸など）"
                rows={3}
                className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              />
            </div>

            {/* エラーメッセージ */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* 送信ボタン */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={isPending || !productId}
                className="flex-1 rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isPending ? '処理中...' : '確定'}
              </button>
              <Link
                href="/inventory"
                className="rounded-lg bg-gray-200 px-6 py-3 text-gray-700 font-medium hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
              >
                キャンセル
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

