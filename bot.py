import os
import asyncio
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
        model="google/gemma-3-27b-it:free",
        messages=[{"role": "user", "content": user_text}]
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_KEY).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()
