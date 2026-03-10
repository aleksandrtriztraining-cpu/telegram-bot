import os
import time
import requests

TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

BASE = f"https://api.telegram.org/bot{TELEGRAM_KEY}"

def get_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    r = requests.get(f"{BASE}/getUpdates", params=params)
    return r.json().get("result", [])

def send_message(chat_id, text):
    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": text})

def ask_ai(text):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
        json={"model": "google/gemma-3-27b-it:free", "messages": [{"role": "user", "content": text}]}
    )
    return r.json()["choices"][0]["message"]["content"]

offset = None
while True:
    updates = get_updates(offset)
    for update in updates:
        offset = update["update_id"] + 1
        msg = update.get("message", {})
        text = msg.get("text")
        chat_id = msg.get("chat", {}).get("id")
        if text and chat_id:
            reply = ask_ai(text)
            send_message(chat_id, reply)
    time.sleep(1)
