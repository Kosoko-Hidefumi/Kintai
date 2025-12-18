import { createServerComponentClient } from '@/lib/supabase/server'
import { getDailySales } from '@/lib/db'
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

    const data = await getDailySales(days)
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching daily sales:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'データの取得に失敗しました' },
      { status: 500 }
    )
  }
}

