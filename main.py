import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import requests
from io import BytesIO
from PIL import Image
from tv_websocket import connect_tradingview

def generate_analysis(symbol: str, interval: str):
    # Step 1: Get real-time price from TradingView WebSocket
    full_symbol = f"OANDA:{symbol}" if "USD" in symbol else f"BINANCE:{symbol}"
    live_price = connect_tradingview(full_symbol)

    if isinstance(live_price, str):
        return "Price not available at the moment."

    # Step 2: Build support/resistance range
    support = round(live_price * 0.997, 2)
    resistance = round(live_price * 1.0015, 2)

    # Step 3: Determine trend
    trend = "Bullish" if support < live_price < resistance else "Bearish"
    emoji = "💹" if trend == "Bullish" else "📉"

    # Step 4: Format analysis text
    message = (
        f"{symbol} – Timeframe {interval.upper()}\n\n"
        f"{trend} Trend {emoji}\n\n"
        f"Vessa sees strong {'buying' if trend == 'Bullish' else 'selling'} opportunities.\n"
        f"A key support level was spotted near ${support}\n"
        f"and a resistance area around ${resistance}.\n"
        f"Check nearby zones for the best entry points to maximize your gains."
    )

    return message

app = FastAPI()

CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY")
LAYOUT_ID = "815anN0d"
LOGO_PATH = "White-Logo-And-Font.png"

# ✅ FIXED HERE
class ChartRequest(BaseModel):
    symbol: str
    interval: str  # ✅ You missed this before – now added

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Technical Analysis API"}

@app.post("/get_chart_image")
def get_chart_image(request: ChartRequest):
    headers = {
        "x-api-key": CHART_IMG_API_KEY,
        "Content-Type": "application/json"
    }

    # Prepare chart payload
    payload = {
        "symbol": request.symbol,
        "interval": request.interval,
        "width": 1920,
        "height": 1080,
        "format": "png"
    }

    try:
        # Step 1: Fetch chart image
        response = requests.post(
            f"https://api.chart-img.com/v2/tradingview/layout-chart/{LAYOUT_ID}",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200 or "image" not in response.headers.get("Content-Type", ""):
            return {"error": "Chart image failed", "details": response.text}

        # Step 2: Add watermark logo
        chart_image = Image.open(BytesIO(response.content))
        final_image = add_logo_to_chart(chart_image)
        img_io = BytesIO()
        final_image.save(img_io, format="PNG")
        img_io.seek(0)

        # Step 3: Generate AI analysis text
        analysis_text = generate_analysis(request.symbol, request.interval)

        # Step 4: Return image + caption text (ready for Telegram)
        return StreamingResponse(
            img_io,
            media_type="image/png",
            headers={"Analysis-Text": analysis_text}
        )

    except Exception as e:
        return {"error": "Request crashed", "details": str(e)}

def add_logo_to_chart(chart_image):
    """ Adds the VessaPro watermark at the center-bottom of the image with a larger size """
    if not os.path.exists(LOGO_PATH):
        return chart_image  

    logo = Image.open(LOGO_PATH).convert("RGBA")

    # Resize logo to be larger
    logo_width = chart_image.width // 4
    logo_height = int((logo_width / logo.width) * logo.height)
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    # Position: Center-bottom
    x_position = (chart_image.width - logo_width) // 2  
    y_position = chart_image.height - logo_height - 20

    # Paste logo onto chart
    chart_image.paste(logo, (x_position, y_position), logo)

    return chart_image

# Optional test mode
if __name__ == "__main__":
    result = generate_analysis("XAUUSD", "M15")
    print(result)
