import { BrowserMultiFormatReader } from '@zxing/library'

/**
 * バーコードリーダーのインスタンスを取得
 */
export function createBarcodeReader(): BrowserMultiFormatReader {
  return new BrowserMultiFormatReader()
}

/**
 * カメラデバイスのリストを取得
 */
export async function getVideoInputDevices(): Promise<MediaDeviceInfo[]> {
  const reader = createBarcodeReader()
  try {
    const devices = await reader.listVideoInputDevices()
    return devices
  } catch (error) {
    console.error('Error getting video input devices:', error)
    throw error
  }
}

