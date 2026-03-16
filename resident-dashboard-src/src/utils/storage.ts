/**
 * アップロードした研修医データのローカル永続化
 * localStorage を使用（同ブラウザ・同デバイスで保持）
 */

import { ResidentRecord } from "../types";

const STORAGE_KEY = "resident-dashboard-data";
const STORAGE_VERSION = 1;

interface StoredData {
  version: number;
  data: ResidentRecord[];
  fileName: string;
  savedAt: string;
}

export function saveResidentData(
  data: ResidentRecord[],
  fileName: string
): boolean {
  try {
    const payload: StoredData = {
      version: STORAGE_VERSION,
      data,
      fileName,
      savedAt: new Date().toISOString(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    return true;
  } catch (e) {
    if (e instanceof DOMException && e.name === "QuotaExceededError") {
      console.warn("ストレージ容量超過: 古いデータを削除して再試行してください");
    }
    return false;
  }
}

export function loadResidentData(): StoredData | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw) as StoredData;
    if (parsed.version !== STORAGE_VERSION || !Array.isArray(parsed.data)) {
      return null;
    }

    return parsed;
  } catch {
    return null;
  }
}

export function clearResidentData(): void {
  localStorage.removeItem(STORAGE_KEY);
}
