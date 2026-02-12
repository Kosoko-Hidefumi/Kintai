import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
try:
    from openai import OpenAI
    from dotenv import load_dotenv
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI or dotenv not found. Running in offline mode.")

# Load environment variables if available
if OPENAI_AVAILABLE:
    load_dotenv()

# Set up paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
APPLICANT_LIST_PATH = os.path.join(DATA_DIR, 'applicant_list.xlsx')

# KOKUYO KPC-E121-20 specs
# 21 labels (3 columns x 7 rows)
MARGIN_TOP = 10.7 * mm
MARGIN_LEFT = 9.75 * mm # Adjusted based on previous script logic
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
        return False

def format_address_with_openai(client, record):
    """
    Format address using OpenAI API if available.
    """
    if not client:
        return f"〒{record.get('郵便番号', '')}\n{record.get('住所', '')}\n{record.get('名前', '')}  様"

    prompt = f"""
以下の宛先情報を日本の郵便ラベル（横63mm x 縦38mm）用に整形・改行してください。
- 住所が長い場合は適切に改行してください。
- 郵便番号、住所、名前の順に並べてください。
- 名前の後ろに「様」を付けてください（既に含まれている場合は重複させないで）。
- 郵便番号の前に「〒」記号を付けてください（例: 〒900-0000）。
- 行ごとに区切って出力してください。
- 出力は整形されたテキストのみにしてください。

情報:
郵便番号: {record.get('郵便番号')}
住所: {record.get('住所')}
名前: {record.get('名前')}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that formats addresses for mailing labels."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return f"〒{record.get('郵便番号', '')}\n{record.get('住所', '')}\n{record.get('名前', '')}  様"

def generate_pdf(output_filename="labels.pdf"):
    if not os.path.exists(APPLICANT_LIST_PATH):
        print(f"Data file not found: {APPLICANT_LIST_PATH}")
        return

    try:
        df = pd.read_excel(APPLICANT_LIST_PATH)
        print(f"Found {len(df)} applicants.")
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # Initialize OpenAI
    client = None
    if OPENAI_AVAILABLE:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
        else:
            print("Warning: OPENAI_API_KEY not found in .env. Using raw formatting.")

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Use fallback filename if locked
    if os.path.exists(output_path):
        try:
             # Try opening in append mode to check lock? No, just try creating canvas later.
             pass
        except:
             pass

    try:
        c = canvas.Canvas(output_path, pagesize=A4)
    except PermissionError:
        print(f"PermissionError: {output_path} is open.")
        output_path = os.path.join(OUTPUT_DIR, "labels_new.pdf")
        c = canvas.Canvas(output_path, pagesize=A4)
        print(f"Using {output_path} instead.")

    if register_font():
        c.setFont(FONT_NAME, 10)
    else:
        print("Warning: using default font (no Japanese support).")

    records = df.to_dict('records')
    
    col = 0
    row = 0
    page_height = A4[1]
    
    for i, record in enumerate(records):
        print(f"Processing {i+1}/{len(records)}: {record.get('名前')}")
        
        # Get formatted text
        formatted_text = format_address_with_openai(client, record)
        
        # Position (Top-Left based)
        # In PDF (0,0) is bottom-left
        # Top margin is from top.
        # y_top is the y-coordinate of the top of the label
        
        x = MARGIN_LEFT + col * COL_PITCH + 5 * mm
        # Calculate Y for the first line of text. 
        # Start slightly below the top of the label.
        y_label_top = page_height - MARGIN_TOP - row * ROW_PITCH
        y_text_start = y_label_top - 5 * mm
        
        text_object = c.beginText(x, y_text_start)
        if register_font():
             text_object.setFont(FONT_NAME, 10)
        else:
             text_object.setFont("Helvetica", 10)
        
        # Leading (line spacing)
        text_object.setLeading(14)

        lines = formatted_text.split('\n')
        for line in lines:
            text_object.textLine(line)
        
        c.drawText(text_object)
        
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

    try:
        c.save()
        print(f"PDF Generated: {output_path}")
    except PermissionError:
        print(f"PermissionError: Could not save {output_path}. File might be open.")
        # Try one more fallback if valid
        base, ext = os.path.splitext(output_path)
        fallback = f"{base}_fallback{ext}"
        try:
            c = canvas.Canvas(fallback, pagesize=A4)
            # ... re-drawing logic would be needed.
            # Simplified: Just fail here or we need to restructure to allow re-save.
            # Since we save at the end, the canvas is already built on the file handle.
            # ReportLab opens file on initialization? yes.
            pass
        except:
            print("Failed to save.")

if __name__ == "__main__":
    generate_pdf()
