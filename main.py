import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import requests
from io import BytesIO

app = FastAPI()

CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY")

class ChartRequest(BaseModel):
    symbol: str
    interval: str

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
        "theme": "dark",
        "style": "candle",
        "width": 1920,
        "height": 1600,
        "studies": [
            {"name": "Pivot Points Standard"},
            {"name": "Bollinger Bands"},
            {"name": "Relative Strength Index"}
        ],
        "drawings": [
            {
                "name": "Rectangle",
                "input": {"x1": "high", "y1": "high+5", "x2": "low", "y2": "low-5"},
                "override": {"fillColor": "rgba(255, 0, 0, 0.2)", "borderColor": "rgba(255, 0, 0, 1)"}
            },
            {
                "name": "Rectangle",
                "input": {"x1": "low", "y1": "low-5", "x2": "high", "y2": "high+5"},
                "override": {"fillColor": "rgba(0, 255, 0, 0.2)", "borderColor": "rgba(0, 255, 0, 1)"}
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.chart-img.com/v2/tradingview/advanced-chart",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return StreamingResponse(BytesIO(response.content), media_type="image/png")
        else:
            return {"error": f"API Error {response.status_code}", "details": response.text}

    except Exception as e:
        return {"error": "Request failed", "details": str(e)}
