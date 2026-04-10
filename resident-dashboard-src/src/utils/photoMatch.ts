/**
 * 研修医名から写真URLを取得するための正規化・検索ロジック
 * build-photos.js / process_photos.py の名前抽出と一致させること
 *
 * 参照優先順: window.__RESIDENT_PHOTOS__ (Streamlit が注入) > residentPhotos.json (ビルド時)
 */

import residentPhotos from "../data/residentPhotos.json";

/**
 * 名前を正規化して検索用候補配列を生成
 * 例: "稲村　直紀" → ["稲村直紀", "稲村　直紀", "直紀稲村", "直紀　稲村"]
 */
export function normalizeForPhotoMatch(name: string): string[] {
  if (!name || typeof name !== "string") return [];

  let base = name
    .replace(/[０-９]/g, (c) =>
      String.fromCharCode(c.charCodeAt(0) - 0xfee0)
    )
    .replace(/[（(（\[【][^）)）\]】]*[）)）\]】]/g, "")
    .trim()
    .replace(/[\s　]+/g, " ")
    .trim();

  const keys = new Set<string>();
  const noSpace = base.replace(/\s/g, "");
  keys.add(noSpace);

  const parts = base.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    const [a, b] = parts;
    keys.add(a + b);
    keys.add(b + a);
    keys.add(`${a}　${b}`);
    keys.add(`${b}　${a}`);
  }

  return Array.from(keys);
}

function getPhotoMap(): Record<string, string> {
  if (typeof window !== "undefined") {
    const injected = (
      window as unknown as { __RESIDENT_PHOTOS__?: Record<string, string> }
    ).__RESIDENT_PHOTOS__;
    if (
      injected &&
      typeof injected === "object" &&
      Object.keys(injected).length > 0
    ) {
      return injected;
    }
  }
  return residentPhotos as Record<string, string>;
}

/**
 * 研修医名から写真のdata URLを取得。該当なしなら undefined
 */
export function getResidentPhotoUrl(name: string): string | undefined {
  const photoMap = getPhotoMap();
  const candidates = normalizeForPhotoMatch(name);
  for (const key of candidates) {
    const url = photoMap[key];
    if (url) return url;
  }
  return undefined;
}
