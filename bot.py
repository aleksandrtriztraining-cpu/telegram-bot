import os
import time
import requests

TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

BASE = f"https://api.telegram.org/bot{TELEGRAM_KEY}"

r = requests.get(f"{BASE}/deleteWebhook")
print("deleteWebhook:", r.text)

r = requests.get(f"{BASE}/getMe")
print("getMe:", r.text)

def get_updates(offset=None):
    params = {"timeout": 10}
    if offset:
        params["offset"] = offset
    r = requests.get(f"{BASE}/getUpdates", params=params, timeout=15)
    print("getUpdates status:", r.status_code, r.text[:300])
    return r.json().get("result", [])

def send_message(chat_id, text):
    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": text})

def ask_ai(text):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
        json={"model": "stepfun/step-3.5-flash:free", "messages": [{"role": "user", "content": text}]}
    )
    print("OpenRouter:", r.status_code, r.text[:200])
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
                print(f"Message: {text}")
                reply = ask_ai(text)
                send_message(chat_id, reply)
    except Exception as e:
        print("Error:", e)
    time.sleep(1)
