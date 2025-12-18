import { createServerComponentClient } from './supabase/server'
import { redirect } from 'next/navigation'

/**
 * サーバーサイドで認証状態を確認
 * 未認証の場合は /login にリダイレクト
 */
export async function requireAuth() {
  const supabase = await createServerComponentClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    redirect('/login')
  }

  return { supabase, session }
}

/**
 * 認証状態を取得（リダイレクトなし）
 */
export async function getSession() {
  const supabase = await createServerComponentClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()
  return { supabase, session }
}

