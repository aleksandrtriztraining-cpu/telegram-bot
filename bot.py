import os
import time
import json
import requests

TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

BASE = f"https://api.telegram.org/bot{TELEGRAM_KEY}"
HISTORY_FILE = "histories.json"

def load_histories():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_histories(histories):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(histories, f, ensure_ascii=False)

histories = load_histories()

requests.get(f"{BASE}/deleteWebhook")

def get_updates(offset=None):
    params = {"timeout": 10}
    if offset:
        params["offset"] = offset
    r = requests.get(f"{BASE}/getUpdates", params=params, timeout=15)
    return r.json().get("result", [])

def send_message(chat_id, text):
    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": text})

def ask_ai(chat_id, text):
    key = str(chat_id)
    if key not in histories:
        histories[key] = []

    histories[key].append({"role": "user", "content": text})

    # Ограничиваем историю последними 20 сообщениями
    messages = histories[key][-20:]

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
        json={"model": "stepfun/step-3.5-flash:free", "messages": messages}
    )

    reply = r.json()["choices"][0]["message"]["content"]
    histories[key].append({"role": "assistant", "content": reply})
    save_histories(histories)

    return reply

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
                reply = ask_ai(chat_id, text)
                send_message(chat_id, reply)
    except Exception as e:
        print("Error:", e)
    time.sleep(1)
