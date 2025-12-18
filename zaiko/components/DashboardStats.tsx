'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface DashboardStatsData {
  salesTotal: number
  orderCount: number
  topProducts: Array<{
    product_id: string
    product_name: string
    total_sales: number
    total_quantity: number
  }>
  lowStock: Array<{
    product_id: string
    product_name: string
    quantity: number
  }>
}

export default function DashboardStats() {
  const [period, setPeriod] = useState<7 | 30 | 90>(30)
  const [stats, setStats] = useState<DashboardStatsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true)
      try {
        const response = await fetch(`/api/reports/dashboard-stats?days=${period}`)
        if (response.ok) {
          const data = await response.json()
          setStats(data)
        }
      } catch (error) {
        console.error('Error fetching dashboard stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [period])

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
    }).format(price)
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-24 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-32"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">データの読み込みに失敗しました</p>
      </div>
    )
  }

  return (
    <>
      {/* 期間選択 */}
      <div className="mb-6 flex justify-end">
        <div className="flex gap-2">
          <button
            onClick={() => setPeriod(7)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              period === 7
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            7日
          </button>
          <button
            onClick={() => setPeriod(30)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              period === 30
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            30日
          </button>
          <button
            onClick={() => setPeriod(90)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              period === 90
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            90日
          </button>
        </div>
      </div>

      {/* KPIカード */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-sm font-medium text-gray-500">売上合計</h2>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {formatPrice(stats.salesTotal)}
          </p>
          <p className="mt-1 text-sm text-gray-500">過去{period}日間</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-sm font-medium text-gray-500">注文件数</h2>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {stats.orderCount.toLocaleString()}
          </p>
          <p className="mt-1 text-sm text-gray-500">過去{period}日間</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-sm font-medium text-gray-500 mb-3">売れ筋TOP3</h2>
          {stats.topProducts.length === 0 ? (
            <p className="text-sm text-gray-500">データなし</p>
          ) : (
            <div className="space-y-2">
              {stats.topProducts.map((product, index) => (
                <div key={product.product_id} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {index + 1}. {product.product_name}
                  </span>
                  <span className="text-sm font-semibold text-gray-900">
                    {formatPrice(product.total_sales)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-sm font-medium text-gray-500 mb-3">在庫少TOP3</h2>
          {stats.lowStock.length === 0 ? (
            <p className="text-sm text-gray-500">データなし</p>
          ) : (
            <div className="space-y-2">
              {stats.lowStock.map((product, index) => (
                <Link
                  key={product.product_id}
                  href={`/products/${product.product_id}`}
                  className="flex items-center justify-between hover:text-blue-600"
                >
                  <span className="text-sm text-gray-600">
                    {index + 1}. {product.product_name}
                  </span>
                  <span className={`text-sm font-semibold ${
                    product.quantity === 0 ? 'text-red-600' : 'text-yellow-600'
                  }`}>
                    {product.quantity}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* レポートへのリンク */}
      <div className="mb-6">
        <Link
          href="/reports/sales"
          className="inline-flex items-center text-blue-600 hover:text-blue-900 font-medium"
        >
          詳細なレポートを見る →
        </Link>
      </div>
    </>
  )
}

