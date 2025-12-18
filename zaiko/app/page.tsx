import { requireAuth } from '@/lib/auth'
import { redirect } from 'next/navigation'

export const dynamic = 'force-dynamic'

export default async function Home() {
  const { session } = await requireAuth()
  
  // 認証済みの場合はダッシュボードにリダイレクト
  if (session) {
    redirect('/dashboard')
  }
  
  // 未認証の場合はログインページにリダイレクト
  redirect('/login')
}
