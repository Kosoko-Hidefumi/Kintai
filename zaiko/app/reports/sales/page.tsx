'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface DailySalesData {
  date: string
  amount: number
}

interface TopProductData {
  product_id: string
  product_name: string
  total_sales: number
  total_quantity: number
}

export default function SalesReportPage() {
  const [period, setPeriod] = useState<7 | 30 | 90>(30)
  const [dailySales, setDailySales] = useState<DailySalesData[]>([])
  const [topProducts, setTopProducts] = useState<TopProductData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [dailyResponse, topResponse] = await Promise.all([
          fetch(`/api/reports/daily-sales?days=${period}`),
          fetch(`/api/reports/top-products?days=${period}`),
        ])

        if (dailyResponse.ok) {
          const dailyData = await dailyResponse.json()
          setDailySales(dailyData)
        }

        if (topResponse.ok) {
          const topData = await topResponse.json()
          setTopProducts(topData)
        }
      } catch (error) {
        console.error('Error fetching report data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [period])

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
    }).format(price)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link
            href="/dashboard"
            className="text-blue-600 hover:text-blue-900 text-sm font-medium"
          >
            ← ダッシュボードに戻る
          </Link>
        </div>

        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">売上レポート</h1>
            <p className="mt-2 text-gray-600">
              期間別の売上推移と商品別売上を確認できます
            </p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setPeriod(7)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                period === 7
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              7日
            </button>
            <button
              onClick={() => setPeriod(30)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                period === 30
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              30日
            </button>
            <button
              onClick={() => setPeriod(90)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                period === 90
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              90日
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">読み込み中...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* 日別売上推移 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                日別売上推移
              </h2>
              {dailySales.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  データがありません
                </p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dailySales}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={formatDate}
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis
                      tickFormatter={(value) => `¥${(value / 1000).toFixed(0)}k`}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                      formatter={(value: number | undefined) => value ? formatPrice(value) : ''}
                      labelFormatter={(label) => `日付: ${label}`}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="amount"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      name="売上"
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* 商品別売上TOP */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                商品別売上TOP
              </h2>
              {topProducts.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  データがありません
                </p>
              ) : (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topProducts}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="product_name"
                      angle={-45}
                      textAnchor="end"
                      height={100}
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis
                      tickFormatter={(value) => `¥${(value / 1000).toFixed(0)}k`}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                      formatter={(value: number | undefined) => value ? formatPrice(value) : ''}
                    />
                    <Legend />
                    <Bar dataKey="total_sales" fill="#3b82f6" name="売上" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* 商品別売上TOP テーブル */}
            {topProducts.length > 0 && (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        順位
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        商品名
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        売上金額
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        数量
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {topProducts.map((product, index) => (
                      <tr key={product.product_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {index + 1}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {product.product_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="text-sm font-semibold text-gray-900">
                            {formatPrice(product.total_sales)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="text-sm text-gray-900">
                            {product.total_quantity}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

