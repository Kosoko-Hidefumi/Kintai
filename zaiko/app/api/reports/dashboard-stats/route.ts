import { createServerComponentClient } from '@/lib/supabase/server'
import { getSalesTotal, getOrderCount, getTopProductsBySales, getLowStockProducts } from '@/lib/db'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const days = parseInt(searchParams.get('days') || '30', 10)

    if (isNaN(days) || days < 1) {
      return NextResponse.json(
        { error: '無効な期間です' },
        { status: 400 }
      )
    }

    const [salesTotal, orderCount, topProducts, lowStock] = await Promise.all([
      getSalesTotal(days),
      getOrderCount(days),
      getTopProductsBySales(days, 3),
      getLowStockProducts(3),
    ])

    return NextResponse.json({
      salesTotal,
      orderCount,
      topProducts,
      lowStock,
    })
  } catch (error) {
    console.error('Error fetching dashboard stats:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'データの取得に失敗しました' },
      { status: 500 }
    )
  }
}

