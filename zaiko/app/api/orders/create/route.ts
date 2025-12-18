import { createServerComponentClient } from '@/lib/supabase/server'
import { createOrder } from '@/lib/db'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { userId, items } = body

    // バリデーション
    if (!items || !Array.isArray(items) || items.length === 0) {
      return NextResponse.json(
        { error: 'カートに商品がありません' },
        { status: 400 }
      )
    }

    for (const item of items) {
      if (!item.productId || !item.quantity || !item.unitPrice) {
        return NextResponse.json(
          { error: '商品情報が不正です' },
          { status: 400 }
        )
      }

      if (typeof item.quantity !== 'number' || item.quantity <= 0) {
        return NextResponse.json(
          { error: '数量は1以上の数値を入力してください' },
          { status: 400 }
        )
      }

      if (typeof item.unitPrice !== 'number' || item.unitPrice < 0) {
        return NextResponse.json(
          { error: '単価が不正です' },
          { status: 400 }
        )
      }
    }

    // 注文を作成
    const orderId = await createOrder(userId || null, items)

    return NextResponse.json({ success: true, orderId })
  } catch (error) {
    console.error('Error creating order:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '注文の作成に失敗しました' },
      { status: 500 }
    )
  }
}

