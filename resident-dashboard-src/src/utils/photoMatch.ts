/**
 * 研修医名から写真URLを取得するための正規化・検索ロジック
 * build-photos.js の名前抽出ロジックと一致させること
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

/**
 * 研修医名から写真のdata URLを取得。該当なしなら undefined
 */
export function getResidentPhotoUrl(name: string): string | undefined {
  const candidates = normalizeForPhotoMatch(name);
  for (const key of candidates) {
    const url = (residentPhotos as Record<string, string>)[key];
    if (url) return url;
  }
  return undefined;
}
