from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import requests

API_URL = "https://ai-technical.up.railway.app/get_chart_image"

# List of available instruments
INSTRUMENTS = {
    "Forex": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"],
    "Crypto": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "LTCUSDT", "ADAUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT", "DOTUSDT", "AVAXUSDT"],
    "Index": ["DJI", "IXIC", "SPX", "UK100", "DE30", "JP225", "HK50", "FRA40", "AUS200", "RUT"],
    "Metals": ["XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD", "XCUUSD", "WTI"]
}

TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W"]

# Step 1: Show Instrument Categories
def show_categories(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(category, callback_data=f"category_{category}")]
        for category in INSTRUMENTS.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select a category:", reply_markup=reply_markup)

# Step 2: Show Instruments Based on Selected Category
def show_instruments(update: Update, context: CallbackContext):
    query = update.callback_query
    category = query.data.split("_")[1]
    
    keyboard = [
        [InlineKeyboardButton(instrument, callback_data=f"instrument_{instrument}")]
        for instrument in INSTRUMENTS[category]
    ]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_categories")])
    
    query.edit_message_text(f"Select an instrument in {category}:", reply_markup=InlineKeyboardMarkup(keyboard))

# Step 3: Show Timeframes
def show_timeframes(update: Update, context: CallbackContext):
    query = update.callback_query
    instrument = query.data.split("_")[1]

    keyboard = [
        [InlineKeyboardButton(tf, callback_data=f"timeframe_{instrument}_{tf}")]
        for tf in TIMEFRAMES
    ]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_instruments")])

    query.edit_message_text(f"Select a timeframe for {instrument}:", reply_markup=InlineKeyboardMarkup(keyboard))

# Step 4: Fetch TradingView Chart Image & Send to User
def fetch_chart_image(update: Update, context: CallbackContext):
    query = update.callback_query
    _, instrument, timeframe = query.data.split("_")

    payload = {
        "symbol": f"BINANCE:{instrument}" if "USDT" in instrument else f"OANDA:{instrument}",
        "interval": timeframe
    }
    
    response = requests.post(API_URL, json=payload)
    
    if response.status_code == 200:
        chart_image = response.json().get("chart_image")
        query.message.reply_photo(photo=open(chart_image, "rb"), caption=f"{instrument} ({timeframe}) Chart")
    else:
        query.message.reply_text("⚠️ Error fetching chart. Please try again.")

# Back Navigation
def back_to_categories(update: Update, context: CallbackContext):
    show_categories(update, context)

def back_to_instruments(update: Update, context: CallbackContext):
    show_instruments(update, context)
