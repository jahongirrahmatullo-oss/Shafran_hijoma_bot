import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


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
# ASOSIY MENYU
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
# XIZMATLAR MENYUSI
# =========================

async def xizmatlar_menu(update: Update):
    keyboard = [
        ["🩸 Hijoma"],
        ["💆 Massaj"],
        ["🪱 Zuluk"],
        ["🔙 Asosiy menyu"],
    ]

    await update.message.reply_text(
        "💰 XIZMATLAR VA NARXLAR\n\n"
        "Kerakli xizmat turini tanlang 👇",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# =========================
# HIJOMA
# =========================

async def hijoma(update: Update):
    text = (
        "🩸 HIJOMA XIZMATLARI\n\n"
        "1️⃣ Hijoma + zaytunli massaj — 300 000 so‘m\n\n"
        "2️⃣ Yuz hijomasi + yengil chiskasi bilan — 450 000 so‘m\n\n"
        "3️⃣ Chertma hijoma — 150 000 so‘m\n\n"
        "4️⃣ Lab uchun hijoma — 100 000 so‘m\n\n"
        "5️⃣ Oyoqdagi shishlar va og‘riqlar uchun hijoma — 200 000 so‘m\n\n"
        "6️⃣ Boshda hijoma — 200 000 so‘m\n\n"
        "7️⃣ Detoks hijoma — 300 000 so‘m\n\n"
        "📌 Batafsil ma’lumotlar keyingi bosqichlarda qo‘shiladi."
    )

    keyboard = [
        ["💆 Massaj"],
        ["🪱 Zuluk"],
        ["💰 Xizmatlar"],
        ["🔙 Asosiy menyu"],
    ]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# =========================
# MASSAJ
# =========================

async def massaj(update: Update):
    text = (
        "💆 MASSAJ XIZMATLARI\n\n"
        "1️⃣ Bitta sohaga massaj — 100 000 so‘m\n\n"
        "2️⃣ Obshiy massaj — 400 000 so‘m\n\n"
        "3️⃣ Koreyksya figura massaj — 300 000 so‘m\n\n"
        "4️⃣ Relax massaj — 300 000 so‘m\n\n"
        "5️⃣ Bo‘yin massaj — 90 000 so‘m\n\n"
        "6️⃣ Oyoq sohasiga massaj — 90 000 so‘m\n\n"
        "7️⃣ Bolalar massaji — 60 000–130 000 so‘m\n\n"
        "8️⃣ Asalli massaj — 150 000 so‘m\n\n"
        "📌 Batafsil ma’lumotlar keyingi bosqichlarda qo‘shiladi."
    )

    keyboard = [
        ["🩸 Hijoma"],
        ["🪱 Zuluk"],
        ["💰 Xizmatlar"],
        ["🔙 Asosiy menyu"],
    ]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# =========================
# ZULUK
# =========================

async def zuluk(update: Update):
    text = (
        "🪱 ZULUK XIZMATLARI\n\n"
        "1️⃣ Zuluk donasi — 50 000 so‘mdan\n\n"
        "2️⃣ Vaginalniy zuluk — 400 000 so‘m\n\n"
        "3️⃣ Zuluklar — Turkiyaniki 🇹🇷\n"
        "   Narxi alohida aniqlanadi.\n\n"
        "📌 Batafsil ma’lumotlar keyingi bosqichlarda qo‘shiladi."
    )

    keyboard = [
        ["🩸 Hijoma"],
        ["💆 Massaj"],
        ["💰 Xizmatlar"],
        ["🔙 Asosiy menyu"],
    ]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# =========================
# QOLGAN MENYULAR
# =========================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 Xizmatlar va narxlar":
        await xizmatlar_menu(update)

    elif text == "🩸 Hijoma":
        await hijoma(update)

    elif text == "💆 Massaj":
        await massaj(update)

    elif text == "🪱 Zuluk":
        await zuluk(update)

    elif text == "💰 Xizmatlar":
        await xizmatlar_menu(update)

    elif text == "🔙 Asosiy menyu":
        await start(update, context)

    elif text == "📅 Qabulga yozilish":
        await update.message.reply_text(
            "📅 Qabulga yozilish\n\n"
            "Online qabulga yozilish tizimini keyingi bosqichda qo‘shamiz."
        )

    elif text == "ℹ️ Hijoma haqida":
        await update.message.reply_text(
            "🩸 HIJOMA HAQIDA\n\n"
            "Hijoma qadimdan qo‘llanib kelgan an’anaviy "
            "muolaja usullaridan biridir.\n\n"
            "🌷 Shafran Hijomada muolajalar tozalik va "
            "ehtiyotkorlikka rioya qilgan holda amalga oshiriladi."
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
