from fastapi import FastAPI
import requests
from pydantic import BaseModel
from fastapi.responses import FileResponse
import uuid
import os

app = FastAPI()

# CHART-IMG API Key and TradingView session details
CHART_IMG_API_KEY = "EVjv7Hqn7caXhdZylYbFMaoAtBSOJzau5PTpUe0c"
SESSION_ID = "vydn367osb8qn9ar6j337xy9ur6a4sel"
SESSION_SIGN = "v3:l1H/P0mJMDsKrXOIZAgUUPJcS+gRqIY2EWyH6SQawDs="

# Model for input parameters
class ChartRequest(BaseModel):
    symbol: str
    interval: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the VPASS AI Technical Analysis API"}

from fastapi.responses import Response

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
    "width": 800,
    "height": 600
}



    response = requests.post(
        "https://api.chart-img.com/v2/tradingview/advanced-chart",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        image_filename = f"chart_{uuid.uuid4().hex}.png"
        image_path = os.path.join(os.getcwd(), image_filename)

        with open(image_path, "wb") as file:
            file.write(response.content)

        return {"chart_image": image_filename}

    else:
        return {"error": f"API Error: {response.status_code}", "details": response.text}
