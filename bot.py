# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI

OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")

client = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1"
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = client.chat.completions.create(
        model="arcee-ai/trinity-large-preview:free",
        messages=[{"role": "user", "content": user_text}]
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TELEGRAM_KEY).build()
app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()
