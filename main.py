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
        "x-api-key": CHART_IMG_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "symbol": request.symbol,
        "interval": request.interval,
        "width": 1920,
        "height": 1600,
        "indicators": [
            {
                "id": "rsi",
                "length": 14
            },
            {
                "id": "sma",
                "length": 20
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.chart-img.com/v2/tradingview/advanced-chart",
            headers=headers,
            json=payload
        )

        print("Response Status Code:", response.status_code)
        print("Response Body:", response.text)

        if response.status_code == 200:
            return StreamingResponse(BytesIO(response.content), media_type="image/png")
        else:
            print(f"Error Response: {response.text}")
            return {"error": f"API Error: {response.status_code}", "details": response.text}

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return {"error": "Request failed", "details": str(e)}
