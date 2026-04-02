from fastapi import FastAPI, Request
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

app = FastAPI()

# --- Configurations ---
DISCORD_VIP_WEBHOOK = "https://discord.com/api/webhooks/1489262275872161952/HGSWn3RkQuw0gmxL9ujqcstv2XuHA9kcqlRK02hwzAduFGHccR6fBmrMGKKOyttreu6U"
TELEGRAM_BOT_TOKEN = "8633861460:AAFNzDkJmULM6B9AgR3EDO9CQKjAdYVAHzg"
TELEGRAM_VIP_CHAT_ID = "-1003829300597"

# --- Google Sheets Setup ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open("Trade Journal").sheet1

# --- TradingView Webhook Endpoint ---
@app.post("/webhook")
async def receive_signal(request: Request):
    data = await request.json()
    
    # Extract data from TradingView
    pair = data.get("pair")
    action = data.get("action") # BUY or SELL
    entry = data.get("entry")
    sl = data.get("sl")
    tp = data.get("tp")
    risk = data.get("risk", "1%")
    
    # 1. Send to Discord/Telegram
    send_discord_alert(pair, action, entry, sl, tp, risk)
    send_telegram_alert(pair, action, entry, sl, tp, risk)
    
    # 2. Log to Google Sheets
    log_to_sheets(pair, action, entry, sl, tp)
    
    return {"status": "success"}