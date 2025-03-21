# tv_websocket.py

import websocket
import json
import threading
import time
from functools import partial

REALTIME_PRICE = {}

def _create_session_id():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase, k=12))

def connect_tradingview(symbol="OANDA:XAUUSD"):
    session_id = _create_session_id()

    socket = websocket.WebSocketApp(
        "wss://widgetdata.tradingview.com/socket.io/websocket",
        on_message=partial(on_message, session_id=session_id, symbol=symbol),
        on_open=partial(on_open, session_id=session_id, symbol=symbol),
        on_error=lambda ws, err, *args: print("WebSocket Error:", err),
        on_close=lambda ws, *args: print("WebSocket Closed.")
    )

    thread = threading.Thread(target=socket.run_forever)
    thread.start()

    # ✅ Wait for price or timeout after 7 seconds
    timeout = 7
    start_time = time.time()
    while time.time() - start_time < timeout:
        if symbol in REALTIME_PRICE:
            break
        time.sleep(0.3)

    socket.close()
    return REALTIME_PRICE.get(symbol, "Price not found")

def on_open(ws, session_id, symbol):
    print(f"WebSocket connected for {symbol}")
    ws.send(json.dumps({"m": "set_auth_token", "p": ""}))
    ws.send(json.dumps({"m": "chart_create_session", "p": [session_id, ""]}))
    ws.send(json.dumps({"m": "resolve_symbol", "p": [session_id, "s1", symbol]}))
    ws.send(json.dumps({"m": "create_series", "p": [session_id, "s1", "s1", "s1", 1, 300]}))

def on_message(ws, message, session_id, symbol):
    try:
        if "lp" in message:
            data = json.loads(message)
            for item in data.get("p", []):
                if "v" in item and "lp" in item["v"]:
                    price = item["v"]["lp"]
                    REALTIME_PRICE[symbol] = round(price, 2)
                    print(f"🔁 {symbol} Live Price: {REALTIME_PRICE[symbol]}")
    except Exception as e:
        print("Error handling message:", e)
