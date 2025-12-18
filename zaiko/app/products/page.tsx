import { requireAuth } from '@/lib/auth'
import { getProducts } from '@/lib/db'
import { Product } from '@/types/db'
import ProductsList from '@/components/ProductsList'
import { Suspense } from 'react'

export const dynamic = 'force-dynamic'

interface ProductsPageProps {
  searchParams: Promise<{ search?: string }>
}

export default async function ProductsPage({ searchParams }: ProductsPageProps) {
  await requireAuth()
  
  const params = await searchParams
  const search = params.search || ''
  const products = await getProducts(search)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">商品一覧</h1>
          <p className="mt-2 text-gray-600">
            商品の検索と一覧表示
          </p>
        </div>

        <Suspense fallback={<div>読み込み中...</div>}>
          <ProductsList initialProducts={products} initialSearch={search} />
        </Suspense>
      </div>
    </div>
  )
}

