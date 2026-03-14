import os
import time
import requests

TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

BASE = f"https://api.telegram.org/bot{TELEGRAM_KEY}"

def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    r = requests.get(f"{BASE}/getUpdates", params=params, timeout=35)
    return r.json().get("result", [])

def send_message(chat_id, text):
    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": text})

def ask_ai(text):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
        json={"model": "google/gemma-3-27b-it:free", "messages": [{"role": "user", "content": text}]},
        timeout=30
    )
    return r.json()["choices"][0]["message"]["content"]

print("Bot started!")
offset = None
while True:
    try:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            msg = update.get("message", {})
            text = msg.get("text")
            chat_id = msg.get("chat", {}).get("id")
            if text and chat_id:
                print(f"Got message: {text}")
                reply = ask_ai(text)
                send_message(chat_id, reply)
                print(f"Replied!")
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
