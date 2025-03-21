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
        "timezone": "Etc/UTC",
        "range": {  # ✅ Set custom date range
            "from": "2023-01-20T00:00:00.000Z",
            "to": "2023-02-12T00:00:00.000Z"
        },
        "studies": [
            {
                "name": "Pivot Points Standard",  # ✅ Auto support & resistance zones
                "override": {
                    "PP.linewidth": 2,  
                    "PP.color": "rgb(255,215,0)"  # Yellow lines for zones
                }
            },
            {
                "name": "Donchian Channels",  # ✅ Supply & demand zones
                "override": {
                    "DONCH.color": "rgb(0,255,255)",  # Cyan for buy/sell zones
                    "DONCH.linewidth": 2
                }
            },
            {
                "name": "Ichimoku Cloud",  # ✅ Trend & momentum indicator
                "input": {
                    "in_0": 9,
                    "in_1": 26,
                    "in_2": 52,
                    "in_3": 26
                },
                "override": {
                    "ConversionLine.visible": True,
                    "ConversionLine.linewidth": 1,
                    "ConversionLine.plottype": "line",
                    "ConversionLine.color": "rgb(33,150,243)",
                    "BaseLine.visible": True,
                    "BaseLine.linewidth": 1,
                    "BaseLine.plottype": "line",
                    "BaseLine.color": "rgb(128,25,34)",
                    "LaggingSpan.visible": True,
                    "LaggingSpan.linewidth": 1,
                    "LaggingSpan.plottype": "line",
                    "LaggingSpan.color": "rgb(67,160,71)",
                    "LeadingSpanA.visible": True,
                    "LeadingSpanA.linewidth": 1,
                    "LeadingSpanA.plottype": "line",
                    "LeadingSpanA.color": "rgb(165,214,167)",
                    "LeadingSpanB.visible": True,
                    "LeadingSpanB.linewidth": 1,
                    "LeadingSpanB.plottype": "line",
                    "LeadingSpanB.color": "rgb(250,161,164)",
                    "Plots Background.visible": True,
                    "Plots Background.transparency": 90
                }
            }
        ],
        "drawings": [  # ✅ Custom LONG POSITION drawing
            {
                "name": "Long Position",
                "input": {
                    "startDatetime": "2023-02-09T00:00:00.000Z",
                    "entryPrice": 22400,
                    "targetPrice": 24000,
                    "stopPrice": 22100
                }
            }
        ],
        "override": {
            "showStudyLastValue": True,  # ✅ Show last values on chart
            "showLegend": True  # ✅ Show indicator names
        }
    }

    try:
        response = requests.post(
            "https://api.chart-img.com/v2/tradingview/advanced-chart",
            headers=headers,
            json=payload
        )

        print("API Response Code:", response.status_code)
        print("API Response Body:", response.text)

        if response.status_code == 200:
            return StreamingResponse(BytesIO(response.content), media_type="image/png")
        else:
            return {"error": f"API Error {response.status_code}", "details": response.text}

    except Exception as e:
        return {"error": "Request failed", "details": str(e)}
