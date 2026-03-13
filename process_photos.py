"""
研修医写真の読み込み・変換（build-photos.js と同じロジック）
pictures フォルダから画像を読み込み、名前→data URL のマッピングを返す
"""
import os
import re
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict


IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")
MAX_SIZE_PX = 200
JPEG_QUALITY = 75


def fullwidth_to_halfwidth(s: str) -> str:
    """全角数字を半角に変換"""
    return re.sub(r"[０-９]", lambda m: chr(ord(m.group(0)) - 0xFEE0), s)


def remove_parentheses(s: str) -> str:
    """括弧とその中身を削除"""
    return re.sub(r"[（(（\[【][^）)）\]】]*[）)）\]】]", "", s).strip()


def extract_name_keys(filename: str) -> list[str]:
    """
    ファイル名から名前部分を抽出し、マッチング用キーの配列を生成
    例: "p01稲村　直紀.jpg" → ["稲村直紀", "直紀稲村", "稲村　直紀", "直紀　稲村"]
    """
    base = Path(filename).stem
    base = re.sub(r"^[pP]?\d+\s*", "", base)  # 接頭辞除去
    base = fullwidth_to_halfwidth(base)
    base = remove_parentheses(base)
    base = re.sub(r"[\s　]+", " ", base).strip()

    keys = set()
    no_space = base.replace(" ", "").replace("　", "")
    if no_space:
        keys.add(no_space)

    parts = [p for p in base.replace("　", " ").split() if p]
    if len(parts) >= 2:
        a, b = parts[0], parts[1]
        keys.add(a + b)
        keys.add(b + a)
        keys.add(f"{a}　{b}")
        keys.add(f"{b}　{a}")

    return [k for k in keys if k]


def collect_image_files(dir_path: str) -> list[str]:
    """ディレクトリを再帰的に走査して画像ファイルを収集"""
    files = []
    if not os.path.isdir(dir_path):
        return files
    for entry in os.scandir(dir_path):
        full = os.path.join(dir_path, entry.name)
        if entry.is_dir():
            files.extend(collect_image_files(full))
        elif entry.name.lower().endswith(IMAGE_EXT):
            files.append(full)
    return files


def load_resident_photos(pictures_dir: str) -> Dict[str, str]:
    """
    pictures フォルダから写真を読み込み、名前キー→data URL の辞書を返す
    build-photos.js と同様のロジック
    """
    result = {}
    try:
        from PIL import Image
    except ImportError:
        return result

    image_files = collect_image_files(pictures_dir)
    for filepath in image_files:
        try:
            with Image.open(filepath) as img:
                img = img.convert("RGB")
                w, h = img.size
                max_dim = max(w, h)
                if max_dim > MAX_SIZE_PX:
                    scale = MAX_SIZE_PX / max_dim
                    new_w = round(w * scale)
                    new_h = round(h * scale)
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                buf = BytesIO()
                img.save(buf, format="JPEG", quality=JPEG_QUALITY)
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                data_url = f"data:image/jpeg;base64,{b64}"

                for key in extract_name_keys(os.path.basename(filepath)):
                    result[key] = data_url
        except Exception:
            pass
    return result
