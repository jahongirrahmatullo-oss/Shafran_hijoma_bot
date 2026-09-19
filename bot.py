import os
import asyncio
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


TOKEN = os.environ["BOT_TOKEN"]


# Render portini ochiq ushlab turish uchun
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Shafran bot ishlayapti!")

    def log_message(self, format, *args):
        pass


def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


keyboard = [
    ["📅 Qabulga yozilish"],
    ["💰 Xizmatlar va narxlar"],
    ["ℹ️ Hijoma haqida"],
    ["📍 Manzil"],
    ["📞 Operator bilan bog‘lanish"]
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! 🌷\n"
        "Shafran Hijoma markaziga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 Xizmatlar va narxlar":
        await update.message.reply_text(
            "💰 XIZMATLAR VA NARXLAR\n\n"
            "🩸 Hijoma — 300 000 so'm\n"
            "🪱 Vaginalniy zuluk — 400 000 so'm\n"
            "✨ Yuz kosmetologik hijoma — 450 000 so'm\n"
            "🌿 Ruqiyali hijoma — 400 000 so'm\n"
            "🪱 Turkiya zulugi — 50 000 so'm / dona\n"
            "⚡ Chertma Fast hijoma — 150 000 so'm\n"
            "💆 Obshiy massaj — 400 000 so'm\n"
            "💃 Koreksiya figura massaj — 300 000 so'm\n"
            "😌 Relax massaj — 250 000 so'm"
        )

    elif text == "📍 Manzil":
        await update.message.reply_text(
            "📍 MANZIL\n\n"
            "Toshkent shahri, Shayxontohur tumani,\n"
            "General Uzoqov 32-uy.\n\n"
            "🕐 Har kuni: 09:00–17:00\n"
            "📞 +998 94 504 09 18"
        )

    elif text == "📞 Operator bilan bog‘lanish":
        await update.message.reply_text(
            "📞 OPERATOR BILAN BOG‘LANISH\n\n"
            "📞 +998 94 504 09 18\n"
            "🕐 Har kuni 09:00–17:00"
        )

    elif text == "ℹ️ Hijoma haqida":
        await update.message.reply_text(
            "ℹ️ HIJOMA HAQIDA\n\n"
            "Hijoma — an’anaviy muolaja usullaridan biri.\n\n"
            "Batafsil ma’lumot uchun operator bilan bog‘lanishingiz mumkin:\n"
            "📞 +998 94 504 09 18"
        )

    elif text == "📅 Qabulga yozilish":
        await update.message.reply_text(
            "📅 QABULGA YOZILISH\n\n"
            "Qabulga yozilish uchun operator bilan bog‘laning:\n\n"
            "📞 +998 94 504 09 18\n"
            "🕐 Har kuni 09:00–17:00"
        )


async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    Thread(target=keep_alive, daemon=True).start()
    asyncio.run(main())
