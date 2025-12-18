'use client'

import { useEffect, useRef, useState } from 'react'
import { BrowserMultiFormatReader } from '@zxing/library'
import { useRouter } from 'next/navigation'
import { createClientComponentClient } from '@/lib/supabase/client'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

export default function ScanPage() {
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const readerRef = useRef<BrowserMultiFormatReader | null>(null)
  const lastScannedCodeRef = useRef<string | null>(null)
  const lastScannedTimeRef = useRef<number>(0)
  const router = useRouter()
  const supabase = createClientComponentClient()

  const stopScanning = () => {
    if (readerRef.current) {
      readerRef.current.reset()
      readerRef.current = null
    }
    setIsScanning(false)
    setError(null)
    setMessage(null)
  }

  const startScanning = async () => {
    try {
      setError(null)
      setMessage(null)
      
      if (!videoRef.current) {
        setError('ビデオ要素が見つかりません')
        return
      }

      const reader = new BrowserMultiFormatReader()
      readerRef.current = reader

      // カメラデバイスを取得
      const devices = await reader.listVideoInputDevices()
      const videoInputDevices = devices.filter(device => device.kind === 'videoinput')
      
      if (videoInputDevices.length === 0) {
        setError('カメラが見つかりません')
        return
      }

      // 最初のカメラを使用
      const selectedDeviceId = videoInputDevices[0].deviceId

      setIsScanning(true)

      // デコードコールバック
      reader.decodeFromVideoDevice(
        selectedDeviceId,
        videoRef.current,
        (result, err) => {
          if (result) {
            const code = result.getText()
            const now = Date.now()

            // 連続読取を防ぐ（同じコードは1秒間無視）
            if (
              code === lastScannedCodeRef.current &&
              now - lastScannedTimeRef.current < 1000
            ) {
              return
            }

            lastScannedCodeRef.current = code
            lastScannedTimeRef.current = now

            // 商品を検索
            handleBarcodeScanned(code)
          }

          if (err) {
            // デコードエラーは無視（継続的にスキャンするため）
            if (err.name !== 'NotFoundException') {
              console.error('Decode error:', err)
            }
          }
        }
      )
    } catch (err) {
      console.error('Error starting scan:', err)
      setError('カメラの起動に失敗しました: ' + (err instanceof Error ? err.message : '不明なエラー'))
      setIsScanning(false)
    }
  }

  const handleBarcodeScanned = async (jan: string) => {
    try {
      setMessage('商品を検索中...')

      // JANコードで商品を検索
      const { data, error: searchError } = await supabase
        .from('products')
        .select('id')
        .eq('jan', jan)
        .single()

      if (searchError || !data) {
        // 商品が見つからない場合
        setMessage(null)
        showToast('商品が見つかりませんでした: ' + jan)
        return
      }

      // 商品が見つかった場合、詳細ページへ遷移
      stopScanning()
      router.push(`/products/${data.id}`)
    } catch (err) {
      console.error('Error searching product:', err)
      setMessage(null)
      showToast('商品の検索に失敗しました')
    }
  }

  const showToast = (text: string) => {
    setMessage(text)
    setTimeout(() => {
      setMessage(null)
    }, 3000)
  }

  useEffect(() => {
    return () => {
      stopScanning()
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link
            href="/dashboard"
            className="text-blue-600 hover:text-blue-900 text-sm font-medium"
          >
            ← ダッシュボードに戻る
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">バーコードスキャン</h1>
          <p className="mt-2 text-gray-600">
            EAN-13バーコードをスキャンして商品を検索します
          </p>
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* トーストメッセージ */}
        {message && (
          <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800">{message}</p>
          </div>
        )}

        {/* ビデオ要素 */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-4">
          <div className="relative aspect-video bg-black">
            <video
              ref={videoRef}
              className="w-full h-full object-cover"
              playsInline
            />
            {!isScanning && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75">
                <p className="text-white text-lg">カメラを起動してください</p>
              </div>
            )}
          </div>
        </div>

        {/* コントロールボタン */}
        <div className="flex gap-4">
          {!isScanning ? (
            <button
              onClick={startScanning}
              className="flex-1 rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              スキャン開始
            </button>
          ) : (
            <button
              onClick={stopScanning}
              className="flex-1 rounded-lg bg-red-600 px-6 py-3 text-white font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
            >
              スキャン停止
            </button>
          )}
        </div>

        {/* 使用方法 */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">使用方法</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-600">
            <li>「スキャン開始」ボタンをクリックしてカメラを起動します</li>
            <li>カメラのアクセス許可を求められたら「許可」を選択します</li>
            <li>バーコードをカメラの前にかざします</li>
            <li>読み取りが成功すると自動的に商品詳細ページに遷移します</li>
            <li>商品が見つからない場合は、通知が表示されます</li>
          </ol>
        </div>
      </div>
    </div>
  )
}

