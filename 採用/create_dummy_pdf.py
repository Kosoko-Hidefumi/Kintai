from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_pdf():
    output_path = os.path.join(os.path.dirname(__file__), 'input', 'sample.pdf')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    c = canvas.Canvas(output_path)
    
    # Register a Japanese font (MS Gothic is standard on Windows)
    try:
        pdfmetrics.registerFont(TTFont('Gothic', 'C:\\Windows\\Fonts\\msgothic.ttc'))
        c.setFont('Gothic', 12)
    except:
        print("Japanese font not found, using default (text might be garbled)")
        # Fallback (OCR might fail to read Japanese if not displayed correctly)
    
    c.drawString(100, 750, '氏名: テスト 太郎')
    c.drawString(100, 730, '郵便番号: 123-4567')
    c.drawString(100, 710, '住所: 東京都千代田区1-1-1')
    c.drawString(100, 690, '電話番号: 090-1234-5678')
    
    c.save()
    print(f"Created {output_path}")

if __name__ == '__main__':
    create_pdf()
