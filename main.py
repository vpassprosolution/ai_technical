import os
import base64
import random
import httpx
from io import BytesIO
from PIL import Image
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis 
import time


# ✅ REDIS CONNECTION
redis_client = redis.StrictRedis.from_url(
    "redis://default:SVvGFFWHscRbAxcSPswMmyhzXLfhIDyk@yamanote.proxy.rlwy.net:12288",
    decode_responses=True
)


app = FastAPI()


CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY", "your_test_api_key_here")
LAYOUT_ID = "815anN0d"
LOGO_PATH = "White-Logo-And-Font.png"

class ChartRequest(BaseModel):
    symbol: str
    interval: str

def generate_dramatic_zone_analysis(symbol: str, interval: str):
    trend = random.choice(["Bullish", "Bearish"])
    emoji = "📉" if trend == "Bearish" else "💹"

    zone_lines = [
        "A major liquidity zone is forming, hinting at an upcoming shift in market momentum. Watch closely.",
        "Strong historical reaction area detected. Traders are watching this zone for breakout or reversal.",
        "The market has this level. A key decision point is near.",
        "A powerful price zone is developing where buyers and sellers are in active battle.",
        "Zone is heating up with compressed candles — a volatility explosion may be near.",
        "Vessa AI has detected overlapping supply/demand layers. Expect rapid reaction.",
        "An imbalance is forming at this zone, price could react aggressively soon.",
        "Price is consolidating in a tight range near this zone — potential accumulation or distribution.",
        "Multiple timeframe alignment found at this level. Critcal reaction expected.",
        "Wicks are stacking near this zone, suggesting a powerful rejection zone is forming.",
        # add more unique variations below (40+ total)
    ]

    guidance_lines = [
        "Let the chart guide your timing. Read the zones, control your entry. 🎯",
        "Focus on market structure, not just price. The zones don’t lie.",
        "It’s not about prediction — it’s about preparation. Trust the levels.",
        "The moment is near. Respect the zone. React with precision. ⚔️",
        "Stay patient. The best trades come from the clearest zones. 🧘‍♂️",
        "This zone holds the key to market bias. Observe price reaction closely.",
        "Trade less. Observe more. Let the zone tell you when to strike.",
        "Momentum traders and swing traders are both watching this zone.",
        "Zone aggression is rising — be ready for fakeouts before breakout.",
        "This is where patience becomes a weapon. Wait for confirmation."
        # add more smart variations (total 40-50 lines)
    ]


    body = f"{random.choice(zone_lines)}\n\n{random.choice(guidance_lines)}"

    return (
        f"{symbol} – Timeframe {interval.upper()}\n\n"
        f"{trend} Outlook {emoji}\n\n"
        f"{body}"
    )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Technical Analysis API"}

@app.post("/get_chart_image")
async def get_chart_image(request: ChartRequest):
    headers = {
        "x-api-key": CHART_IMG_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "symbol": request.symbol,
        "interval": request.interval,
        "width": 1920,
        "height": 1080,
        "format": "png",
        "rightOffset": 10
    }

    # ✅ Check Redis Cache
    cache_key = f"chart_cache:{request.symbol}:{request.interval}"
    cached_data = redis_client.hgetall(cache_key)
    
    if cached_data:
        timestamp = float(cached_data.get("timestamp", 0))
        if time.time() - timestamp < 60:
            print("♻️ Returning chart from Redis cache")
            return JSONResponse(content={
                "caption": cached_data.get("caption", ""),
                "image_base64": cached_data.get("image_base64", "")
            })

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"https://api.chart-img.com/v2/tradingview/layout-chart/{LAYOUT_ID}",
                headers=headers,
                json=payload
            )

        if response.status_code != 200 or "image" not in response.headers.get("Content-Type", ""):
            return JSONResponse(status_code=400, content={
                "error": "Chart image failed",
                "details": response.text
            })

        chart_image = Image.open(BytesIO(response.content))
        final_image = add_logo_to_chart(chart_image)

        img_io = BytesIO()
        final_image.save(img_io, format="PNG")
        img_io.seek(0)
        image_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")

        analysis_text = generate_dramatic_zone_analysis(request.symbol, request.interval)

        # ✅ Save result to Redis
        redis_client.hset(cache_key, mapping={
            "timestamp": time.time(),
            "caption": analysis_text,
            "image_base64": image_base64
        })
        redis_client.expire(cache_key, 120)  # Optional TTL

        return JSONResponse(content={
            "caption": analysis_text,
            "image_base64": image_base64
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "error": "Request crashed",
            "details": str(e)
        })


def add_logo_to_chart(chart_image):
    if not os.path.exists(LOGO_PATH):
        return chart_image

    logo = Image.open(LOGO_PATH).convert("RGBA")

    logo_width = chart_image.width // 4
    logo_height = int((logo_width / logo.width) * logo.height)
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    x_position = (chart_image.width - logo_width) // 2
    y_position = chart_image.height - logo_height - 5

    chart_image.paste(logo, (x_position, y_position), logo)
    return chart_image

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
