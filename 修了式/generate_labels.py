
import os
import csv
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration for KOKUYO KPC-E121-20
# 21 labels (3 columns x 7 rows)
# Sheet size: A4 (210 x 297 mm)
# Label size: 63.5 x 38.1 mm
MARGIN_TOP = 10.7 * mm
MARGIN_LEFT = 7 * mm # Estimated based on standard layout (210 - 63.5*3) / 2 ~= 9.75? Adjusting to standard 7mm usually.
# Actually (210 - 63.5*3)/2 = 9.75mm. Let's start with proper calculation or standard specs.
# KPC-E121-20 specs often: Left margin 10mm, Top 10.7mm.
# Let's try: Left 10mm.
MARGIN_LEFT = 9.75 * mm
COL_PITCH = 63.5 * mm
ROW_PITCH = 38.1 * mm
COLS = 3
ROWS = 7

FONT_PATH = "C:\\Windows\\Fonts\\msgothic.ttc"
FONT_NAME = "MSGothic"

def register_font():
    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
        return True
    except Exception as e:
        print(f"Font registration warning: {e}")
        # Fallback handling could be added here
        return False

def format_address_with_openai(client, record):
    """
    Format address using OpenAI API.
    Record expected dict: {'名前': ..., '住所': ..., '郵便番号': ..., '肩書き': ...}
    """
    if not client:
        # Fallback if no API key
        return f"〒{record.get('郵便番号', '')}\n{record.get('住所', '')}\n{record.get('肩書き', '')}\n{record.get('名前', '')}"

    prompt = f"""
以下の宛先情報を日本の郵便ラベル（横63mm x 縦38mm）用に整形・改行してください。
- 住所が長い場合は適切に改行してください。
- 郵便番号、住所、肩書き（あれば）、名前の順に並べてください。
- 敬称（様、殿など）が名前に含まれていない場合は追加してください。既に含まれている場合は重複させないでください。
- 郵便番号の前に「〒」記号を付けてください（例: 〒900-0000）。
- 行ごとに区切って出力してください。
- 出力は整形されたテキストのみにしてください。

情報:
郵便番号: {record.get('郵便番号')}
住所: {record.get('住所')}
肩書き: {record.get('肩書き')}
名前: {record.get('名前')}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # or gpt-3.5-turbo, using a cheaper model for simple formatting
            messages=[
                {"role": "system", "content": "You are a helpful assistant that formats addresses for mailing labels."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return f"〒{record.get('郵便番号', '')}\n{record.get('住所', '')}\n{record.get('肩書き', '')}\n{record.get('名前', '')}"

def generate_pdf(output_file="labels.pdf"):
    # Read Data
    data_file = "list.xlsx"
    if not os.path.exists(data_file):
        data_file = "施設リスト.csv"
        print(f"list.xlsx not found, using {data_file}")
    
    try:
        if data_file.endswith('.xlsx'):
            df = pd.read_excel(data_file)
        else:
            df = pd.read_csv(data_file)
            
        print(f"Columns found: {df.columns.tolist()}")
        
        # Standardize columns matching
        # Expected: 名前, 住所, 郵便番号, 肩書き
        # If headers differ, we might need mapping.
        # Let's clean headers (strip whitespace)
        df.columns = [c.strip() for c in df.columns]
        
        required_cols = ['名前', '住所']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
             print(f"Error: Missing required columns in {data_file}. Missing: {missing}")
             # Attempt fuzzy matching or index based if needed?
             # For now, just return to let user know.
             return
    except Exception as e:
        print(f"Error reading data file: {e}")
        return

    # Initialize OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None
    if not client:
        print("Warning: OPENAI_API_KEY not found. Using raw data formatting.")

    # Setup PDF
    c = canvas.Canvas(output_file, pagesize=A4)
    if register_font():
        c.setFont(FONT_NAME, 10)
    else:
        print("Warning: using default font (no Japanese support).")

    records = df.to_dict('records')
    
    col = 0
    row = 0 # 0 is top row? No, usually coordinate system starts bottom-left for PDF, but we can calculate from top.
    
    # Coordinate system: (0,0) is bottom-left.
    # Top-Left Label position:
    # X = MARGIN_LEFT + col * COL_PITCH
    # Y = HEIGHT - MARGIN_TOP - (row + 1) * ROW_PITCH
    
    page_width, page_height = A4
    
    count = 0
    
    for i, record in enumerate(records):
        print(f"Processing {i+1}/{len(records)}: {record.get('名前')}")
        
        # Get formatted text
        formatted_text = format_address_with_openai(client, record)
        
        # Position
        x = MARGIN_LEFT + col * COL_PITCH + 5 * mm # padding inside label
        y_top = page_height - MARGIN_TOP - row * ROW_PITCH - 5 * mm # padding inside label
        
        # Draw text
        text_object = c.beginText(x, y_top)
        if register_font():
             text_object.setFont(FONT_NAME, 10)
        else:
             text_object.setFont("Helvetica", 10)
             
        # Split by lines and draw
        lines = formatted_text.split('\n')
        for line in lines:
            text_object.textLine(line)
        
        c.drawText(text_object)
        
        # Draw outline for debugging (optional - remove for production)
        # rect_x = MARGIN_LEFT + col * COL_PITCH
        # rect_y = page_height - MARGIN_TOP - (row + 1) * ROW_PITCH
        # c.rect(rect_x, rect_y, 63.5*mm, 38.1*mm)

        count += 1
        col += 1
        if col >= COLS:
            col = 0
            row += 1
            if row >= ROWS:
                c.showPage() # New page
                if register_font():
                    c.setFont(FONT_NAME, 10)
                row = 0
                col = 0

    c.save()
    print(f"PDF Generated: {output_file}")

if __name__ == "__main__":
    generate_pdf()
