import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_IDS = os.environ['TELEGRAM_CHAT_IDS'].split(',')

LOCATIONS = [
    {"name": "경기도 부천", "lat": 37.4989, "lon": 126.7831},
    {"name": "서울 용산", "lat": 37.5326, "lon": 126.9907},
    {"name": "서울 금천구", "lat": 37.4563, "lon": 126.8956},
    {"name": "경기도 용인", "lat": 37.2411, "lon": 127.1776},
]

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "weathercode",
        ],
        "timezone": "Asia/Seoul",
        "forecast_days": 1,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def weather_code_to_text(code):
    if code == 0:
        return "☀️ 맑음"
    elif code == 1:
        return "🌤️ 대체로 맑음"
    elif code == 2:
        return "⛅ 구름 많음"
    elif code == 3:
        return "☁️ 흐림"
    elif code in [45, 48]:
        return "🌫️ 안개"
    elif code in [51, 53, 55]:
        return "🌦️ 이슬비"
    elif code in [61, 63, 65]:
        return "🌧️ 비"
    elif code in [71, 73, 75]:
        return "❄️ 눈"
    elif code in [80, 81, 82]:
        return "🌧️ 소나기"
    elif code in [95, 96, 99]:
        return "⛈️ 뇌우"
    else:
        return "🌡️ 알 수 없음"

def send_telegram(message, chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id.strip(),
        "text": message,
        "parse_mode": "HTML",
    }
    response = requests.post(url, json=payload, timeout=10)
    print(f"Telegram response: {response.status_code} {response.text}")
    response.raise_for_status()

def main():
    today = datetime.now(KST).strftime("%Y년 %m월 %d일 (%a)")
    # 요일 한글 변환
    weekday_map = {"Mon": "월", "Tue": "화", "Wed": "수", "Thu": "목",
                   "Fri": "금", "Sat": "토", "Sun": "일"}
    for en, ko in weekday_map.items():
        today = today.replace(en, ko)

    message = f"🌤️ <b>{today} 날씨 안내</b>\n"
    message += "─" * 20 + "\n\n"

    for loc in LOCATIONS:
        data = get_weather(loc["lat"], loc["lon"])
        daily = data["daily"]

        temp_max = daily["temperature_2m_max"][0]
        temp_min = daily["temperature_2m_min"][0]
        precipitation = daily["precipitation_sum"][0]
        rain_prob = daily["precipitation_probability_max"][0]
        code = daily["weathercode"][0]

        message += f"📍 <b>{loc['name']}</b>\n"
        message += f"   {weather_code_to_text(code)}\n"
        message += f"   🌡️ 최고 {temp_max}°C / 최저 {temp_min}°C\n"
        message += f"   🌂 강수확률 {rain_prob}% / 강수량 {precipitation}mm\n\n"

    message += "좋은 하루 보내세요! 😊"

    for chat_id in CHAT_IDS:
        send_telegram(message, chat_id)
        print(f"Sent to {chat_id}")

if __name__ == "__main__":
    main()
