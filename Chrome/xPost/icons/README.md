# Icons

このディレクトリには拡張機能のアイコンファイルを配置します。

## 必要なファイル

以下のサイズのアイコンファイルを作成してください：

- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

## アイコンデザイン

`icon.svg` を参考にデザインしてください。

## 作成方法

SVGからPNGへの変換方法：

1. オンラインツールを使用
   - [CloudConvert](https://cloudconvert.com/svg-to-png)
   - [Convertio](https://convertio.co/svg-png/)

2. コマンドラインから（ImageMagickがインストール済みの場合）
   ```bash
   magick icon.svg -resize 16x16 icon16.png
   magick icon.svg -resize 48x48 icon48.png
   magick icon.svg -resize 128x128 icon128.png
   ```

3. プレースホルダーを使用（一時的）
   - このディレクトリに .png ファイルを作成すれば拡張機能は動作します
   - ただし、実際のアイコンは後で置き換えてください


