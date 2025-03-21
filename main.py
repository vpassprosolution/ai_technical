import os
import base64
import random
import requests
from io import BytesIO
from PIL import Image
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Chart-IMG API Key from environment or fallback for local testing
CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY", "your_test_api_key_here")
LAYOUT_ID = "815anN0d"
LOGO_PATH = "White-Logo-And-Font.png"

class ChartRequest(BaseModel):
    symbol: str
    interval: str

def generate_dramatic_zone_analysis(symbol: str, interval: str):
    trend = random.choice(["Bullish", "Bearish"])
    emoji = "💹" if trend == "Bullish" else "📉"

    zone_lines = [
        "A key zone is lighting up on the chart...",
        "The battle between buyers and sellers is clearly drawn in the zones.",
        "Vessa highlights an area of interest where momentum is shifting.",
        "Watch the zones closely — they’re whispering opportunity.",
        "Price is hovering around a sensitive area. Stay sharp."
    ]

    guidance_lines = [
        "Let the chart guide your timing. Read the zones, control your entry. 🎯",
        "Focus on market structure, not just price. The zones don’t lie.",
        "It’s not about prediction — it’s about preparation. Trust the levels.",
        "The moment is near. Respect the zone. React with precision. ⚔️",
        "Stay patient. The best trades come from the clearest zones. 🧘‍♂️"
    ]

    body = f"{random.choice(zone_lines)}\n\n{random.choice(guidance_lines)}"
    return f"{symbol} – Timeframe {interval.upper()}\n\n{trend} Outlook {emoji}\n\n{body}"

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Technical Analysis API"}

@app.post("/get_chart_image")
def get_chart_image(request: ChartRequest):
    headers = {
        "x-api-key": CHART_IMG_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "symbol": request.symbol,
        "interval": request.interval,
        "width": 1920,
        "height": 1080,
        "format": "png"
    }

    try:
        response = requests.post(
            f"https://api.chart-img.com/v2/tradingview/layout-chart/{LAYOUT_ID}",
            headers=headers,
            json=payload,
            timeout=60
        )

        # Validate response
        if response.status_code != 200 or "image" not in response.headers.get("Content-Type", ""):
            return JSONResponse(status_code=400, content={
                "error": "Chart image failed",
                "details": response.text
            })

        # Process and logo overlay
        chart_image = Image.open(BytesIO(response.content))
        final_image = add_logo_to_chart(chart_image)

        # Convert to base64
        img_io = BytesIO()
        final_image.save(img_io, format="PNG")
        img_io.seek(0)
        image_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")

        # Generate text analysis
        analysis_text = generate_dramatic_zone_analysis(request.symbol, request.interval)

        return JSONResponse(content={
            "caption": analysis_text,
            "image_base64": image_base64
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "error": "Request crashed",
            "details": str(e)
        })

def add_logo_to_chart(chart_image):
    if not os.path.exists(LOGO_PATH):
        return chart_image

    logo = Image.open(LOGO_PATH).convert("RGBA")

    logo_width = chart_image.width // 4
    logo_height = int((logo_width / logo.width) * logo.height)
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    x_position = (chart_image.width - logo_width) // 2
    y_position = chart_image.height - logo_height - 5

    chart_image.paste(logo, (x_position, y_position), logo)
    return chart_image

# Optional test for terminal
if __name__ == "__main__":
    result = generate_dramatic_zone_analysis("XAUUSD", "M15")
    print(result)
