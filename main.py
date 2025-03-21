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
        "height": 1080,
        "range": {
            "from": "2023-01-20T00:00:00.000Z",
            "to": "2023-02-12T00:00:00.000Z"
        },
        "studies": [
            {"name": "Pivot Points Standard"},
            {"name": "Bollinger Bands"}
        ],
        "drawings": [
            {
                "name": "Rectangle",
                "input": {
                    "startDatetime": "2023-02-09T00:00:00.000Z",
                    "entryPrice": 22400,
                    "targetPrice": 24000,
                    "stopPrice": 22100
                }
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
