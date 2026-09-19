import os
import sqlite3
import asyncio
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB = "bot.db"
PHONE = "+998 94 504 09 18"
ADDRESS = "Toshkent shahri, Shayxontohur tumani, General Uzoqov 32-uy"
CHANNEL = "https://t.me/Shafran_hijoma"

SERVICES = {
    "🩸 Hijoma": [
        ("Hijoma + zaytunli massaj", 300000),
        ("Yuz hijomasi + yengil chiskasi bilan", 450000),
        ("Chertma hijoma", 150000),
        ("Lab uchun hijoma", 100000),
        ("Oyoqdagi shishlar va og‘riqlar uchun hijoma", 200000),
        ("Boshda hijoma", 200000),
        ("Detoks hijoma", 300000),
    ],
    "💆 Massaj": [
        ("Bitta sohaga massaj", 100000),
        ("Obshiy massaj", 400000),
        ("Koreyksya figura massaj", 300000),
        ("Relax massaj", 300000),
        ("Bo‘yin massaj", 90000),
        ("Oyoq sohasiga massaj", 90000),
        ("Bollar massaj", 60000),
        ("Asalli massaj", 150000),
    ],
    "🪱 Zuluk": [
        ("Zuluk donasi", 50000),
        ("Vaginalniy zuluk", 400000),
        ("Zuluklar — Turkiyaniki 🇹🇷", 0),
    ],
}


def db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            phone TEXT,
            service TEXT,
            price INTEGER,
            date TEXT,
            time TEXT,
            created_at TEXT,
            reminded INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    return conn


def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["💰 Xizmatlar va narxlar"],
            ["📅 Qabulga yozilish"],
            ["ℹ️ Hijoma haqida"],
            ["📍 Manzil", "📞 Operator"],
            ["📢 Telegram kanal"],
        ],
        resize_keyboard=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db().close()

    text = (
        "🌷 Assalomu alaykum!\n\n"
        "🩸 Shafran Hijoma markaziga xush kelibsiz.\n\n"
        "Quyidagi menyudan kerakli bo‘limni tanlang:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for category in SERVICES:
        keyboard.append([
            InlineKeyboardButton(
                category,
                callback_data="cat|" + category
            )
        ])

    await update.message.reply_text(
        "💰 Xizmatlar va narxlar:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_name = query.data.split("|", 1)[1]

    keyboard = []

    for i, (name, price) in enumerate(SERVICES[category_name]):
        if price:
            title = f"{name} — {price:,} so‘m".replace(",", " ")
        else:
            title = name

        keyboard.append([
            InlineKeyboardButton(
                title,
                callback_data=f"service|{category_name}|{i}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Orqaga", callback_data="back_categories")
    ])

    await query.edit_message_text(
        f"{category_name}\n\nXizmatni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def back_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(cat, callback_data="cat|" + cat)]
        for cat in SERVICES
    ]

    await query.edit_message_text(
        "💰 Xizmatlar:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def service_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, category_name, index = query.data.split("|")
    index = int(index)

    name, price = SERVICES[category_name][index]

    if price:
        price_text = f"{price:,} so‘m".replace(",", " ")
    else:
        price_text = "Narxi alohida aniqlanadi"

    text = (
        f"🌷 {name}\n\n"
        f"💰 Narxi: {price_text}\n\n"
        "📅 Qabulga yozilish uchun quyidagi tugmani bosing."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "📅 Qabulga yozilish",
                callback_data=f"book|{category_name}|{index}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data="back_categories"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def hijoma_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🩸 HIJOMA HAQIDA

🌙 HIJOMA — SUNNAT VA AN’ANAVIY MUOLАJA

Hijoma islom tarixida qadimdan ma’lum bo‘lgan muolaja usullaridan biridir. Rasululloh ﷺ o‘zlari ham hijoma qildirganlar.

📖 HADISLARDAN

Rasululloh ﷺ:

«Shifo bo‘ladigan narsalarning ichida hijomada ham shifo bor».

📚 Sahih al-Buxoriy, 5697-hadis. (Сунна)

Yana Anas ibn Molik roziyallohu anhudan rivoyat qilinadi: Rasululloh ﷺ hijoma qildirganlar va hijomani davolanish usullaridan biri sifatida zikr qilganlar.

📚 Sahih al-Buxoriy, 5696-hadis. (Сунна)

Ibn Abbos roziyallohu anhudan rivoyat qilinadi: Rasululloh ﷺ boshlaridagi og‘riq sababli hijoma qildirganlar.

📚 Sahih al-Buxoriy, 5700–5701-hadislar. (Сунна)

Demak, hijomaning musulmonlar uchun ahamiyati faqat an’anaviy muolaja bo‘lgani uchungina emas. Rasululloh ﷺ ning hijoma qildirganlari va uni davolanish vositalaridan biri sifatida zikr qilganlari sababli ham hijoma musulmonlar orasida qadrlanadi.

🌿 HIJOMANING INSON UCHUN FOYDASI

Hijoma qadimdan turli xalqlarda qo‘llanib kelgan. Bugungi kunda ham cupping/hijoma usullari ilmiy tadqiqotlarda o‘rganilmoqda.

Ayrim tadqiqotlarda hijoma og‘riqni kamaytirishga yordam berishi mumkinligi ko‘rsatilgan. Ayniqsa mushak va ayrim og‘riqli holatlarda uning ta’siri o‘rganilgan.

🌷 SHAFRAN HIJOMA

Bizda hijoma muolajalari ehtiyotkorlik, tozalik va mijozning individual holatini hisobga olgan holda amalga oshiriladi.

📅 Qabulga yozilish:
+998 94 504 09 18

📍 Manzil:
Toshkent shahri, Shayxontohur tumani,
General Uzoqov 32-uy.

🕐 Har kuni: 09:00–17:00
"""

    await update.message.reply_text(text)


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🗺️ Xaritada ochish",
                url="https://www.google.com/maps/search/?api=1&query=General+Uzoqov+32%2C+Tashkent%2C+Uzbekistan"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Qo‘ng‘iroq qilish",
                url="tel:+998945040918"
            )
        ]
    ]

    await update.message.reply_text(
        "📍 Toshkent shahri, Shayxontohur tumani,\n"
        "General Uzoqov 32-uy.\n\n"
        "🕐 Har kuni: 09:00–17:00\n"
        "📞 +998 94 504 09 18",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Operator:\n\n"
        "+998 94 504 09 18"
    )


async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "📢 Kanalga kirish",
                url=CHANNEL
            )
        ]
    ]

    await update.message.reply_text(
        "🌷 Shafran Hijoma Telegram kanali:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )async def main():
    db().close()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(
        filters.Regex("^💰 Xizmatlar va narxlar$"),
        services
    ))

    app.add_handler(MessageHandler(
        filters.Regex("^ℹ️ Hijoma haqida$"),
        hijoma_info
    ))

    app.add_handler(MessageHandler(
        filters.Regex("^📍 Manzil$"),
        address
    ))

    app.add_handler(MessageHandler(
        filters.Regex("^📞 Operator$"),
        operator
    ))

    app.add_handler(MessageHandler(
        filters.Regex("^📢 Telegram kanal$"),
        channel
    ))

    app.add_handler(CallbackQueryHandler(
        category,
        pattern=r"^cat\|"
    ))

    app.add_handler(CallbackQueryHandler(
        back_categories,
        pattern=r"^back_categories$"
    ))

    app.add_handler(CallbackQueryHandler(
        service_details,
        pattern=r"^service\|"
    ))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print("BOT ISHLAYAPTI")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
