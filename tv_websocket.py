# tv_websocket.py

import websocket
import json
import threading
import time

REALTIME_PRICE = {}

def _create_session_id():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase, k=12))

def connect_tradingview(symbol="OANDA:XAUUSD"):
    session_id = _create_session_id()
    socket = websocket.WebSocketApp(
        "wss://widgetdata.tradingview.com/socket.io/websocket",
        on_message=lambda ws, msg: on_message(ws, msg, session_id, symbol),
        on_open=lambda ws: on_open(ws, session_id, symbol),
        on_error=lambda ws, err: print("WebSocket Error:", err),
        on_close=lambda ws: print("WebSocket Closed.")
    )

    thread = threading.Thread(target=socket.run_forever)
    thread.start()

    # Wait a few seconds to gather price
    time.sleep(3)

    # Close connection after getting price
    socket.close()

    return REALTIME_PRICE.get(symbol, "Price not found")

def on_open(ws, session_id, symbol):
    print(f"WebSocket connected for {symbol}")
    ws.send(json.dumps({"m": "set_auth_token", "p": ""}))
    ws.send(json.dumps({"m": "chart_create_session", "p": [session_id, ""]}))
    ws.send(json.dumps({
        "m": "resolve_symbol",
        "p": [session_id, "s1", symbol]
    }))
    ws.send(json.dumps({
        "m": "create_series",
        "p": [session_id, "s1", "s1", "s1", 1, 300]
    }))

def on_message(ws, message, session_id, symbol):
    try:
        data = json.loads(message)
        if "s1" in message and "price" in message:
            for update in data.get("p", [{}]):
                price = update.get("v", {}).get("lp")  # last price
                if price:
                    REALTIME_PRICE[symbol] = round(price, 2)
                    print(f"🔁 {symbol} Live Price: {REALTIME_PRICE[symbol]}")
    except Exception as e:
        print("Error handling message:", e)
