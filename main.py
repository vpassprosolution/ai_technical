import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import requests
from io import BytesIO

app = FastAPI()

CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY")

# Shared layout ID from TradingView
LAYOUT_ID = "815anN0d"

class ChartRequest(BaseModel):
    symbol: str
    interval: str

@app.get("/")
def read_root():
    return {"message": "AI Technical Chart Generator with Shared TradingView Layout"}


@app.post("/get_chart_image")
def get_chart_image(request: ChartRequest):
    headers = {
        "x-api-key": CHART_IMG_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "symbol": request.symbol,           # e.g. BINANCE:BTCUSDT
        "interval": request.interval,       # e.g. 1h, 4h, 1D
        "width": 1920,
        "height": 1080,
        "format": "png"
    }

    try:
        response = requests.post(
            f"https://api.chart-img.com/v2/tradingview/layout-chart/{LAYOUT_ID}",
            headers=headers,
            json=payload,
            timeout=60  # recommended by Chart-IMG
        )

        print("Response Code:", response.status_code)
        if response.status_code == 200:
            return StreamingResponse(BytesIO(response.content), media_type="image/png")
        else:
            return {"error": f"API Error {response.status_code}", "details": response.text}

    except Exception as e:
        return {"error": "Request failed", "details": str(e)}
