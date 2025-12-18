import { requireAuth } from '@/lib/auth'
import LogoutButton from '@/components/LogoutButton'
import DashboardStats from '@/components/DashboardStats'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  const { session } = await requireAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">ダッシュボード</h1>
            <p className="mt-2 text-gray-600">
              ようこそ、{session.user.email} さん
            </p>
          </div>
          <LogoutButton />
        </div>

        {/* ナビゲーション */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            href="/scan"
            className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow border-2 border-blue-500"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-2">バーコードスキャン</h2>
            <p className="text-sm text-gray-600">カメラでバーコードを読み取り</p>
          </Link>
          <Link
            href="/products"
            className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-2">商品管理</h2>
            <p className="text-sm text-gray-600">商品の一覧・検索・詳細</p>
          </Link>
          <Link
            href="/inventory"
            className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-2">在庫管理</h2>
            <p className="text-sm text-gray-600">在庫一覧・入庫・出庫</p>
          </Link>
          <Link
            href="/orders"
            className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-2">注文管理</h2>
            <p className="text-sm text-gray-600">注文の作成・一覧・詳細</p>
          </Link>
        </div>

        {/* KPIと統計 */}
        <DashboardStats />
      </div>
    </div>
  )
}

