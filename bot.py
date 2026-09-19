import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


BOT_TOKEN = os.getenv("BOT_TOKEN")


# =========================
# RENDER HEALTH SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def start_server():
    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 Xizmatlar va narxlar"],
        ["📅 Qabulga yozilish"],
        ["ℹ️ Hijoma haqida"],
        ["📍 Manzil", "📞 Operator"],
        ["📢 Telegram kanal"],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🌷 Assalomu alaykum!\n\n"
        "🩸 Shafran Hijoma botiga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=reply_markup
    )


# =========================
# MENU
# =========================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 Xizmatlar va narxlar":
        await update.message.reply_text(
            "💰 Xizmatlar va narxlar bo‘limi\n\n"
            "Bu bo‘limni keyingi qadamda to‘liq qo‘shamiz."
        )

    elif text == "📅 Qabulga yozilish":
        await update.message.reply_text(
            "📅 Qabulga yozilish\n\n"
            "Online qabulga yozilish tizimini keyingi qadamda qo‘shamiz."
        )

    elif text == "ℹ️ Hijoma haqida":
        await update.message.reply_text(
            "🩸 HIJOMA HAQIDA\n\n"
            "Hijoma qadimdan qo‘llanib kelgan an’anaviy muolaja usullaridan biridir.\n\n"
            "🌷 Shafran Hijomada muolajalar tozalik va ehtiyotkorlikka "
            "rioya qilgan holda amalga oshiriladi."
        )

    elif text == "📍 Manzil":
        await update.message.reply_text(
            "📍 Manzil:\n\n"
            "Toshkent shahri, Shayxontohur tumani,\n"
            "General Uzoqov 32-uy\n\n"
            "🕐 Har kuni: 09:00–17:00"
        )

    elif text == "📞 Operator":
        await update.message.reply_text(
            "📞 Operator bilan bog‘lanish:\n\n"
            "+998 94 504 09 18"
        )

    elif text == "📢 Telegram kanal":
        await update.message.reply_text(
            "📢 Telegram kanalimiz:\n\n"
            "https://t.me/Shafran_hijoma"
        )


# =========================
# MAIN
# =========================

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi")

    threading.Thread(
        target=start_server,
        daemon=True
    ).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            menu
        )
    )

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
