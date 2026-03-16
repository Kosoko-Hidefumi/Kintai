/**
 * pictures フォルダから写真を読み込み、名前→data URL のマッピングを生成するビルドスクリプト
 * 出力: src/data/residentPhotos.json
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import sharp from "sharp";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// 研修医一覧/pictures を優先、なければ resident-dashboard/pictures
const PICTURES_ROOT = path.resolve(__dirname, "../../pictures");
const PICTURES_LOCAL = path.resolve(__dirname, "../pictures");
const PICTURES_DIR = fs.existsSync(PICTURES_ROOT)
  ? PICTURES_ROOT
  : PICTURES_LOCAL;
const OUTPUT_PATH = path.resolve(__dirname, "../src/data/residentPhotos.json");
const MAX_SIZE_PX = 200;
const JPEG_QUALITY = 75;
const IMAGE_EXT = [".jpg", ".jpeg", ".png", ".webp"];

/**
 * 全角数字を半角に変換
 */
function fullwidthToHalfwidth(str) {
  return str.replace(/[０-９]/g, (c) =>
    String.fromCharCode(c.charCodeAt(0) - 0xfee0)
  );
}

/**
 * 括弧とその中身を削除
 */
function removeParentheses(str) {
  return str.replace(/[（(（\[【][^）)）\]】]*[）)）\]】]/g, "").trim();
}

/**
 * ファイル名から名前部分を抽出し、マッチング用キーの配列を生成
 * 例: "p01稲村　直紀.jpg" → ["稲村直紀", "直紀稲村", "稲村　直紀", "直紀　稲村"]
 */
function extractNameKeys(filename) {
  let base = path.basename(filename, path.extname(filename));
  base = base.replace(/^[pP]?\d+\s*/, ""); // 接頭辞除去
  base = fullwidthToHalfwidth(base);
  base = removeParentheses(base);
  base = base.replace(/[\s　]+/g, " ").trim();

  const keys = new Set();
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
 * ディレクトリを再帰的に走査して画像ファイルを収集
 */
function collectImageFiles(dir, files = []) {
  if (!fs.existsSync(dir)) return files;

  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      collectImageFiles(fullPath, files);
    } else if (
      IMAGE_EXT.some((ext) => entry.name.toLowerCase().endsWith(ext))
    ) {
      files.push(fullPath);
    }
  }
  return files;
}

async function buildPhotos() {
  const photoMap = {};
  const imageFiles = collectImageFiles(PICTURES_DIR);

  if (imageFiles.length === 0) {
    console.log(
      `[build-photos] No images found in ${PICTURES_DIR} (folder may not exist)`
    );
  } else {
    for (const filePath of imageFiles) {
      try {
        let img = sharp(filePath);
        const meta = await img.metadata();
        const { width = 0, height = 0 } = meta;
        const maxDim = Math.max(width, height);

        if (maxDim > MAX_SIZE_PX) {
          const scale = MAX_SIZE_PX / maxDim;
          img = img.resize(
            Math.round(width * scale),
            Math.round(height * scale)
          );
        }

        const buffer = await img
          .jpeg({ quality: JPEG_QUALITY })
          .toBuffer();
        const base64 = buffer.toString("base64");
        const dataUrl = `data:image/jpeg;base64,${base64}`;

        const nameKeys = extractNameKeys(path.basename(filePath));
        for (const key of nameKeys) {
          if (key) photoMap[key] = dataUrl;
        }
      } catch (err) {
        console.warn(`[build-photos] Skip ${filePath}:`, err.message);
      }
    }
    console.log(
      `[build-photos] Processed ${imageFiles.length} images → ${Object.keys(photoMap).length} keys`
    );
  }

  const outDir = path.dirname(OUTPUT_PATH);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(photoMap), "utf-8");
  console.log(`[build-photos] Written to ${OUTPUT_PATH}`);
}

buildPhotos().catch((err) => {
  console.error("[build-photos] Error:", err);
  process.exit(1);
});
