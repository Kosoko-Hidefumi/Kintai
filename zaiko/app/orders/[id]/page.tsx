import { requireAuth } from '@/lib/auth'
import { getOrder } from '@/lib/db'
import { notFound } from 'next/navigation'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface OrderDetailPageProps {
  params: Promise<{ id: string }>
}

export default async function OrderDetailPage({ params }: OrderDetailPageProps) {
  await requireAuth()
  
  const { id } = await params
  const order = await getOrder(id)

  if (!order) {
    notFound()
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
    }).format(price)
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'confirmed':
        return { label: '確定', color: 'bg-green-100 text-green-800' }
      case 'draft':
        return { label: '下書き', color: 'bg-gray-100 text-gray-800' }
      case 'cancelled':
        return { label: 'キャンセル', color: 'bg-red-100 text-red-800' }
      default:
        return { label: status, color: 'bg-gray-100 text-gray-800' }
    }
  }

  const statusInfo = getStatusLabel(order.status)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link
            href="/orders"
            className="text-blue-600 hover:text-blue-900 text-sm font-medium"
          >
            ← 注文一覧に戻る
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow p-8">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">注文詳細</h1>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${statusInfo.color}`}>
              {statusInfo.label}
            </span>
          </div>

          <dl className="grid grid-cols-1 gap-6 mb-8">
            <div>
              <dt className="text-sm font-medium text-gray-500">注文ID</dt>
              <dd className="mt-1 text-sm text-gray-900">{order.id}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">注文日時</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(order.ordered_at).toLocaleString('ja-JP')}
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">合計金額</dt>
              <dd className="mt-1 text-2xl font-bold text-gray-900">
                {formatPrice(order.total_amount)}
              </dd>
            </div>
          </dl>

          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">注文内容</h2>
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      商品名
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      単価
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      数量
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      小計
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {order.items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {item.product.name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {item.product.sku && `SKU: ${item.product.sku}`}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm text-gray-900">
                          {formatPrice(item.unit_price_in)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm text-gray-900">
                          {item.quantity}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          {formatPrice(item.line_total)}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

