import { createServerComponentClient } from '@/lib/supabase/server'
import { moveInventory } from '@/lib/db'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { productId, moveType, qty, reason, userId } = body

    // バリデーション
    if (!productId || !moveType || !qty) {
      return NextResponse.json(
        { error: '必須項目が不足しています' },
        { status: 400 }
      )
    }

    if (!['in', 'out', 'adjust'].includes(moveType)) {
      return NextResponse.json(
        { error: '無効な移動種別です' },
        { status: 400 }
      )
    }

    if (typeof qty !== 'number' || qty <= 0) {
      return NextResponse.json(
        { error: '数量は1以上の数値を入力してください' },
        { status: 400 }
      )
    }

    // 在庫移動を実行
    await moveInventory(productId, moveType, qty, reason || null, userId || null)

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Error moving inventory:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '在庫移動に失敗しました' },
      { status: 500 }
    )
  }
}

