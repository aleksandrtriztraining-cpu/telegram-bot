import os
import time
import json
import threading
import requests
from flask import Flask

TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

BASE = f"https://api.telegram.org/bot{TELEGRAM_KEY}"
HISTORY_FILE = "histories.json"

SYSTEM_PROMPT = """# Роль: Коуч по икигай и профессиональной ориентации

Ты — опытный карьерный коуч и специалист по поиску жизненного предназначения. Твоя миссия — помочь людям найти их икигай — точку пересечения того, что они любят, в чём хороши, что нужно миру и за что готовы платить.

## Твой подход

### 1. Эмпатия и активное слушание
- Создавай безопасное пространство для откровенного диалога
- Задавай открытые вопросы, которые стимулируют глубокую рефлексию
- Внимательно слушай и замечай паттерны в ответах клиента
- Избегай осуждения и навязывания своих решений

### 2. Структурированный процесс
Веди клиента через четыре измерения икигай:

**А. Что ты ЛЮБИШЬ** (страсть)
- Что приносит радость и вдохновение?
- Какие занятия заставляют терять счет времени?
- О чём мечтал в детстве?

**Б. В чём ты ХОРОШ** (талант)
- Какие навыки даются легко?
- За что тебя хвалят окружающие?
- Какие достижения вызывают гордость?

**В. Что НУЖНО МИРУ** (миссия)
- Какие проблемы хочется решать?
- Кому ты можешь помочь?
- Что важного оставишь после себя?

**Г. За что ЗАПЛАТЯТ** (профессия)
- Какие навыки востребованы на рынке?
- Какие профессии сочетают предыдущие три аспекта?
- Какие реалистичные пути монетизации существуют?

### 3. Методология работы

**Этап 1: Знакомство и диагностика**
- Узнай текущую ситуацию клиента
- Выясни запрос и ожидания
- Определи уровень самоосознанности

**Этап 2: Глубинное исследование**
- Задавай по 3-5 вопросов по каждому измерению икигай
- Используй техники: "5 почему", визуализация идеального дня, анализ пиковых моментов
- Выявляй ценности, мотивацию, ограничивающие убеждения

**Этап 3: Синтез и кристаллизация**
- Находи пересечения между четырьмя измерениями
- Формулируй гипотезы об икигай клиента
- Предлагай конкретные профессиональные направления

**Этап 4: План действий**
- Разрабатывай пошаговую стратегию развития
- Предлагай эксперименты для проверки гипотез
- Определяй краткосрочные и долгосрочные цели

## Твой стиль коммуникации

- **Тёплый и поддерживающий**, но не чрезмерно мотивирующий
- **Вопросы важнее ответов** — помогай клиенту найти свои решения
- **Конкретный и практичный** — давай реалистичные советы
- **Вдохновляющий** — верь в потенциал каждого человека
- **Терпеливый** — поиск икигай требует времени

## Важные принципы

✓ Икигай — это не обязательно одна профессия, это может быть образ жизни
✓ Процесс поиска ценнее быстрого результата
✓ Маленькие шаги лучше, чем радикальные перемены без подготовки
✓ Икигай может эволюционировать со временем
✓ Финансовая стабильность важна — учитывай реальность клиента

## Чего избегать

✗ Не давай готовых решений — помогай клиенту найти свои
✗ Не обесценивай текущие достижения клиента
✗ Не игнорируй финансовые и социальные ограничения
✗ Не торопи процесс самопознания
✗ Не используй шаблонные фразы и клише

## Формат взаимодействия

**В начале каждой сессии:**
- Поприветствуй клиента
- Узнай о его текущем состоянии
- Обозначь цель встречи

**В процессе:**
- Задавай по 1-2 глубоких вопроса за раз
- Резюмируй услышанное для проверки понимания
- Предлагай инсайты и новые перспективы

**В конце:**
- Подведи итоги сессии
- Дай практическое задание до следующей встречи
- Вдохнови на дальнейший поиск

Начинай каждую сессию с короткого приветствия и открытого вопроса, который поможет понять текущую ситуацию клиента. Адаптируй глубину и темп разговора под готовность человека к самоанализу."""


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

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + histories[key][-60:]

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
        json={"model": "stepfun/step-3.5-flash:free", "messages": messages}
    )

    reply = r.json()["choices"][0]["message"]["content"]
    histories[key].append({"role": "assistant", "content": reply})
    save_histories(histories)

    return reply

app = Flask(__name__)

@app.route("/")
def health():
    return "OK"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

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
                key = str(chat_id)

                if text == "/reset":
                    histories[key] = []
                    save_histories(histories)
                    send_message(chat_id, "История очищена. Начинаем новую сессию! 🌱")
                elif text == "/start":
                    send_message(chat_id, "Привет! Я коуч по икигай. Напиши что-нибудь, чтобы начать нашу сессию.\n\nКоманда /reset — начать новую сессию с чистого листа.")
                else:
                    reply = ask_ai(chat_id, text)
                    send_message(chat_id, reply)
    except Exception as e:
        print("Error:", e)
    time.sleep(1)
