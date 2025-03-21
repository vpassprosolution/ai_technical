import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
import requests
from io import BytesIO

app = FastAPI()

CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY")
LAYOUT_ID = "815anN0d"  # Your shared layout ID

class ChartRequest(BaseModel):
    symbol: str
    interval: str

@app.get("/")
def read_root():
    return {"message": "AI Layout Chart Generator is running ✅"}

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
            timeout=60  # recommended
        )

        print("Status Code:", response.status_code)
        print("Response Headers:", response.headers)

        if response.status_code == 200 and "image" in response.headers["Content-Type"]:
            return StreamingResponse(BytesIO(response.content), media_type="image/png")
        else:
            print("❌ Non-image response received")
            return JSONResponse(content={"error": "API did not return image", "details": response.text}, status_code=422)

    except Exception as e:
        print("❌ Request Failed:", str(e))
        return JSONResponse(content={"error": "Request crashed", "details": str(e)}, status_code=500)
