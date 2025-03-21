import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import requests
from io import BytesIO
from PIL import Image

app = FastAPI()

CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY")

# Your TradingView Shared Layout ID (Make sure it's correct)
LAYOUT_ID = "815anN0d"  # ✅ Your TradingView Layout

# Path to your logo
LOGO_PATH = "White-Logo-And-Font.png"

class ChartRequest(BaseModel):
    symbol: str

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
        "symbol": request.symbol,  # ✅ Keep your requested symbol
        "width": 1920,  # ✅ HD Wide Format
        "height": 1080, # ✅ Not square, cinematic
        "format": "png"
    }

    try:
        response = requests.post(
            f"https://api.chart-img.com/v2/tradingview/layout-chart/{LAYOUT_ID}",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            chart_image = Image.open(BytesIO(response.content))
            final_image = add_logo_to_chart(chart_image)
            img_io = BytesIO()
            final_image.save(img_io, format="PNG")
            img_io.seek(0)
            return StreamingResponse(img_io, media_type="image/png")
        else:
            return {"error": f"API Error {response.status_code}", "details": response.text}

    except Exception as e:
        return {"error": "Request failed", "details": str(e)}

def add_logo_to_chart(chart_image):
    """ Adds the VessaPro watermark to the bottom-center of the chart """
    if not os.path.exists(LOGO_PATH):
        return chart_image  # If logo is missing, return original chart

    logo = Image.open(LOGO_PATH).convert("RGBA")

    # Resize logo to fit well (adjust as needed)
    logo_width = chart_image.width // 5
    logo_height = int((logo_width / logo.width) * logo.height)
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    # Position: Bottom-center
    x_position = (chart_image.width - logo_width) // 2
    y_position = chart_image.height - logo_height - 20  # 20px padding from bottom

    # Paste logo onto chart
    chart_image.paste(logo, (x_position, y_position), logo)

    return chart_image
