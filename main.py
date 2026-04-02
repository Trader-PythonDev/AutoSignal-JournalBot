from fastapi import FastAPI, Request
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json

app = FastAPI()

# --- Configurations ---
DISCORD_VIP_WEBHOOK = os.environ.get("DISCORD_VIP_WEBHOOK")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_VIP_CHAT_ID = os.environ.get("TELEGRAM_VIP_CHAT_ID")

# --- Google Sheets Setup ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
google_creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if google_creds_json:
    creds = Credentials.from_service_account_info(json.loads(google_creds_json), scopes=scopes)
else:
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