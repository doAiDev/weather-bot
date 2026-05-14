import os
import json
import requests
from datetime import datetime

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_IDS = os.environ['TELEGRAM_CHAT_IDS'].split(',')

LOCATIONS = [
    {"name": "경기도 부천", "lat": 37.4989, "lon": 126.7831},
    {"name": "서울 용산",   "lat": 37.5326, "lon": 126.9907},
    {"name": "서울 금천구", "lat": 37.4563, "lon": 126.8956},
    {"name": "경기도 용인", "lat": 37.2411, "lon": 127.1776},
]

STATE_FILE = "state.json"

def get_precipitation_probability(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["precipitation_probability"],
        "timezone": "Asia/Seoul",
        "forecast_days": 1,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    now_hour = datetime.now().hour
    return data["hourly"]["precipitation_probability"][now_hour]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def send_telegram(message, chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id.strip(),
        "text": message,
        "parse_mode": "HTML",
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()

def main():
    state = load_state()
    changes = []

    for loc in LOCATIONS:
        current_prob = get_precipitation_probability(loc["lat"], loc["lon"])
        prev_prob = state.get(loc["name"])

        if prev_prob is not None and current_prob != prev_prob:
            if current_prob > prev_prob:
                direction = f"올랐어요 ⬆️ ({prev_prob}% → {current_prob}%)"
            else:
                direction = f"내렸어요 ⬇️ ({prev_prob}% → {current_prob}%)"
            changes.append(f"📍 <b>{loc['name']}</b> 강수확률이 {direction}")

        state[loc["name"]] = current_prob

    save_state(state)

    if changes:
        message = "🌂 <b>강수확률 변동 알림</b>\n\n"
        message += "\n\n".join(changes)
        for chat_id in CHAT_IDS:
            send_telegram(message, chat_id)
            print(f"Sent to {chat_id}")
    else:
        print("변동 없음")

if __name__ == "__main__":
    main()
