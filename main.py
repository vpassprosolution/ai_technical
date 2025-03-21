import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import requests
from io import BytesIO

app = FastAPI()

CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY")
SESSION_ID = os.getenv("SESSION_ID")
SESSION_SIGN = os.getenv("SESSION_SIGN")

class ChartRequest(BaseModel):
    symbol: str
    interval: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Technical Analysis API"}

@app.post("/get_chart_image")
def get_chart_image(request: ChartRequest):
    headers = {
        "Authorization": f"Bearer {CHART_IMG_API_KEY}",
        "Content-Type": "application/json"
    }

    params = {
    "symbol": request.symbol,
    "interval": request.interval,
    "studies": [
        "PPS:Traditional,Auto,15",  # ✅ Pivot Points Standard (Support & Resistance Levels)
        "BB:20,close,2",            # ✅ Bollinger Bands (Dynamic Price Zones)
        "VSTOP:20,close,2"          # ✅ Volatility Stop (Dynamic Zones Like SNR)
    ],
    "theme": "dark",
    "style": "candle",
    "width": 1920,
    "height": 1600,
    "timezone": "Etc/UTC",
    "format": "png",
    "logo": "false"  # Remove logo for a cleaner look
}


    try:
        response = requests.get(
            "https://api.chart-img.com/v1/tradingview/advanced-chart",
            headers=headers,
            params=params
        )

        print("Status:", response.status_code)
        if response.status_code == 200:
            return StreamingResponse(BytesIO(response.content), media_type="image/png")
        else:
            print("Error:", response.text)
            return {"error": f"API Error {response.status_code}", "details": response.text}

    except Exception as e:
        return {"error": "Request failed", "details": str(e)}
