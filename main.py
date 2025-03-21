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
        "tradingview-session-id": SESSION_ID,
        "tradingview-session-id-sign": SESSION_SIGN,
        "Content-Type": "application/json"
    }

    payload = {
        "symbol": request.symbol,
        "interval": request.interval,
        "width": 1920,  # Max resolution
        "height": 1600,
        "layout": "vessa pro",  # Ensure this is exactly your TradingView layout name
        "loadIndicators": True,  # Force Chart-IMG to load indicators from the layout
        "useIndicatorsFromLayout": True,  # Explicitly load indicators from the TradingView layout
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
            return {"error": f"API Error: {response.status_code}", "details": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": "Request failed", "details": str(e)}


# ✅ Required for Railway Deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
