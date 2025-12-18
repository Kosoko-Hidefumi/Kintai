import { requireAuth } from '@/lib/auth'
import { getProduct } from '@/lib/db'
import { notFound } from 'next/navigation'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface ProductDetailPageProps {
  params: Promise<{ id: string }>
}

export default async function ProductDetailPage({ params }: ProductDetailPageProps) {
  await requireAuth()
  
  const { id } = await params
  const product = await getProduct(id)

  if (!product) {
    notFound()
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
    }).format(price)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link
            href="/products"
            className="text-blue-600 hover:text-blue-900 text-sm font-medium"
          >
            ← 商品一覧に戻る
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">{product.name}</h1>

          <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">商品ID</dt>
              <dd className="mt-1 text-sm text-gray-900">{product.id}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">SKU</dt>
              <dd className="mt-1 text-sm text-gray-900">{product.sku || '-'}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">JANコード</dt>
              <dd className="mt-1 text-sm text-gray-900">{product.jan || '-'}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">価格（税込）</dt>
              <dd className="mt-1 text-lg font-semibold text-gray-900">
                {formatPrice(product.price_in)}
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">作成日</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(product.created_at).toLocaleString('ja-JP')}
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">更新日</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(product.updated_at).toLocaleString('ja-JP')}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}

