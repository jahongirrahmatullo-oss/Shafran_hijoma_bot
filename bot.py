import os
import sqlite3
import threading
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


# =========================================================
# SOZLAMALAR
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_FILE = "bot.db"

PHONE = "+998 94 504 09 18"

ADDRESS = (
    "Toshkent shahri, Shayxontohur tumani, "
    "General Uzoqov 32-uy"
)

GOOGLE_MAPS = (
    "https://www.google.com/maps/search/"
    "?api=1&query=General+Uzoqov+32%2C+Tashkent%2C+Uzbekistan"
)

YANDEX_MAPS = (
    "https://yandex.com/maps/org/"
    "shafran_women_s_center/148946361051/"
)

CHANNEL = "https://t.me/Shafran_hijoma"


# =========================================================
# XIZMATLAR
# =========================================================

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


# =========================================================
# DATABASE
# =========================================================

def init_db():

    conn = sqlite3.connect(DB_FILE)

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
            created_at TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# ASOSIY MENYU
# =========================================================

def main_menu():

    keyboard = [
        ["💰 Xizmatlar va narxlar"],
        ["📅 Qabulga yozilish"],
        ["ℹ️ Hijoma haqida"],
        ["📍 Manzil", "📞 Operator"],
        ["📢 Telegram kanal"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "🌷 Assalomu alaykum!\n\n"
        "🩸 Shafran Hijoma markaziga xush kelibsiz!\n\n"
        "Quyidagi menyudan kerakli bo‘limni tanlang:",
        reply_markup=main_menu()
    )


# =========================================================
# XIZMATLAR
# =========================================================

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):

    buttons = []

    for category in SERVICES:

        buttons.append([
            InlineKeyboardButton(
                category,
                callback_data="category|" + category
            )
        ])

    await update.message.reply_text(
        "💰 Xizmatlar va narxlar:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    category = query.data.split("|", 1)[1]

    buttons = []

    for index, (name, price) in enumerate(SERVICES[category]):

        if price > 0:
            price_text = f"{price:,}".replace(",", " ")
            title = f"{name} — {price_text} so‘m"
        else:
            title = name

        buttons.append([
            InlineKeyboardButton(
                title,
                callback_data=f"service|{category}|{index}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "⬅️ Orqaga",
            callback_data="categories"
        )
    ])

    await query.edit_message_text(
        f"{category}\n\nXizmatni tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def show_service(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    parts = query.data.split("|")

    category = parts[1]
    index = int(parts[2])

    name, price = SERVICES[category][index]

    if price > 0:
        price_text = f"{price:,}".replace(",", " ") + " so‘m"
    else:
        price_text = "Narxi alohida aniqlanadi"

    text = (
        f"🌷 {name}\n\n"
        f"💰 Narxi: {price_text}\n\n"
        "📅 Qabulga yozilish uchun tugmani bosing."
    )

    buttons = [
        [
            InlineKeyboardButton(
                "📅 Qabulga yozilish",
                callback_data=f"book|{category}|{index}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data=f"category|{category}"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def back_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    buttons = []

    for category in SERVICES:

        buttons.append([
            InlineKeyboardButton(
                category,
                callback_data="category|" + category
            )
        ])

    await query.edit_message_text(
        "💰 Xizmatlar:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================================================
# HIJOMA HAQIDA
# =========================================================

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


# =========================================================
# MANZIL
# =========================================================

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):

    buttons = [

        [
            InlineKeyboardButton(
                "🗺️ Google Maps",
                url=GOOGLE_MAPS
            )
        ],

        [
            InlineKeyboardButton(
                "🟡 Yandex Maps",
                url=YANDEX_MAPS
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
        "📍 MANZIL\n\n"
        f"{ADDRESS}\n\n"
        "🕐 Har kuni: 09:00–17:00\n"
        f"📞 {PHONE}\n\n"
        "Xaritadan kerakli xizmatni tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================================================
# OPERATOR
# =========================================================

async def operator(update: Update, context: ContextTypes.DEFAULT_TYPE):

    buttons = [
        [
            InlineKeyboardButton(
                "📞 Qo‘ng‘iroq qilish",
                url="tel:+998945040918"
            )
        ]
    ]

    await update.message.reply_text(
        "📞 Operator bilan bog‘lanish:\n\n"
        f"{PHONE}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================================================
# TELEGRAM KANAL
# =========================================================

async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    buttons = [
        [
            InlineKeyboardButton(
                "📢 Kanalga kirish",
                url=CHANNEL
            )
        ]
    ]

    await update.message.reply_text(
        "🌷 Shafran Hijoma Telegram kanali:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================================================
# QABULGA YOZILISH
# =========================================================

async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    buttons = []

    for category in SERVICES:

        buttons.append([
            InlineKeyboardButton(
                category,
                callback_data="bookcategory|" + category
            )
        ])

    await update.message.reply_text(
        "📅 QABULGA YOZILISH\n\n"
        "Xizmat turini tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def booking_category(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    category = query.data.split("|", 1)[1]

    buttons = []

    for index, (name, price) in enumerate(SERVICES[category]):

        buttons.append([
            InlineKeyboardButton(
                name,
                callback_data=f"bookservice|{category}|{index}"
            )
        ])

    await query.edit_message_text(
        "Xizmatni tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def booking_service(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    parts = query.data.split("|")

    category = parts[1]
    index = int(parts[2])

    name, price = SERVICES[category][index]

    context.user_data["service"] = name
    context.user_data["price"] = price
    context.user_data["booking_step"] = "date"

    await query.message.reply_text(
        "📅 Qaysi sana uchun yozilmoqchisiz?\n\n"
        "Masalan:\n"
        "25.09.2026"
    )


async def booking_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    step = context.user_data.get("booking_step")

    if not step:
        return

    text = update.message.text.strip()

    # SANA
    if step == "date":

        context.user_data["date"] = text
        context.user_data["booking_step"] = "time"

        await update.message.reply_text(
            "🕐 Qaysi vaqtga yozilmoqchisiz?\n\n"
            "Masalan:\n"
            "14:00"
        )

        return

    # VAQT
    if step == "time":

        context.user_data["time"] = text
        context.user_data["booking_step"] = "name"

        await update.message.reply_text(
            "👤 Ismingizni yozing:"
        )

        return

    # ISM
    if step == "name":

        context.user_data["name"] = text
        context.user_data["booking_step"] = "phone"

        await update.message.reply_text(
            "📞 Telefon raqamingizni yozing:"
        )

        return

    # TELEFON
    if step == "phone":

        service = context.user_data["service"]
        price = context.user_data["price"]
        date = context.user_data["date"]
        time = context.user_data["time"]
        name = context.user_data["name"]
        phone = text

        conn = sqlite3.connect(DB_FILE)

        conn.execute(
            """
            INSERT INTO bookings
            (
                user_id,
                name,
                phone,
                service,
                price,
                date,
                time,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                update.effective_user.id,
                name,
                phone,
                service,
                price,
                date,
                time
            )
        )

        conn.commit()
        conn.close()

        if price > 0:
            price_text = f"{price:,}".replace(",", " ") + " so‘m"
        else:
            price_text = "Narxi aniqlanadi"

        await update.message.reply_text(
            "✅ QABULGA YOZILISH QABUL QILINDI!\n\n"
            f"🌷 Xizmat: {service}\n"
            f"💰 Narx: {price_text}\n"
            f"📅 Sana: {date}\n"
            f"🕐 Vaqt: {time}\n"
            f"👤 Ism: {name}\n"
            f"📞 Telefon: {phone}\n\n"
            "Operator siz bilan bog‘lanadi.",
            reply_markup=main_menu()
        )

        context.user_data.clear()


# =========================================================
# CANCEL
# =========================================================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Qabulga yozilish bekor qilindi.",
        reply_markup=main_menu()
    )


# =========================================================
# RENDER HEALTH SERVER
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

        self.wfile.write(
            b"Shafran Hijoma bot ishlayapti"
        )

    def log_message(self, format, *args):
        return


def start_web_server():

    port = int(
        os.environ.get("PORT", "10000")
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    server.serve_forever()


# =========================================================
# BOTNI ISHGA TUSHIRISH
# =========================================================

def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN Render Environment Variables ichida topilmadi."
        )

    init_db()

    # Render server
    web_thread = threading.Thread(
        target=start_web_server,
        daemon=True
    )

    web_thread.start()

    # Telegram bot
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # COMMANDS
    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("cancel", cancel)
    )

    # ASOSIY MENYU
    application.add_handler(
        MessageHandler(
            filters.Regex("^💰 Xizmatlar va narxlar$"),
            show_services
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^📅 Qabulga yozilish$"),
            start_booking
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^ℹ️ Hijoma haqida$"),
            hijoma_info
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^📍 Manzil$"),
            address
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^📞 Operator$"),
            operator
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^📢 Telegram kanal$"),
            channel
        )
    )

    # XIZMATLAR CALLBACK
    application.add_handler(
        CallbackQueryHandler(
            show_category,
            pattern=r"^category\|"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            back_categories,
            pattern=r"^categories$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            show_service,
            pattern=r"^service\|"
        )
    )

    # BOOKING CALLBACK
    application.add_handler(
        CallbackQueryHandler(
            booking_category,
            pattern=r"^bookcategory\|"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            booking_service,
            pattern=r"^bookservice\|"
        )
    )

    # BOOKING TEXT
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            booking_text
        )
    )

    print("================================")
    print("SHAFRAN HIJOMA BOT ISHLAYAPTI")
    print("================================")

    application.run_polling()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()
