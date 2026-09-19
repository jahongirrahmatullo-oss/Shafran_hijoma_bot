import os
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


BOT_TOKEN = os.getenv("BOT_TOKEN")

# Toshkent vaqti
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")


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
        "7️⃣ Detoks hijoma — 300 000 so‘m"
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
        "8️⃣ Asalli massaj — 150 000 so‘m"
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
        "   Narxi alohida aniqlanadi."
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
# QABULGA YOZILISH
# =========================

SERVICES = {
    "h1": "Hijoma + zaytunli massaj",
    "h2": "Yuz hijomasi + yengil chiskasi bilan",
    "h3": "Chertma hijoma",
    "h4": "Lab uchun hijoma",
    "h5": "Oyoqdagi shishlar va og‘riqlar uchun hijoma",
    "h6": "Boshda hijoma",
    "h7": "Detoks hijoma",

    "m1": "Bitta sohaga massaj",
    "m2": "Obshiy massaj",
    "m3": "Koreyksya figura massaj",
    "m4": "Relax massaj",
    "m5": "Bo‘yin massaj",
    "m6": "Oyoq sohasiga massaj",
    "m7": "Bolalar massaji",
    "m8": "Asalli massaj",

    "z1": "Zuluk donasi",
    "z2": "Vaginalniy zuluk",
    "z3": "Zuluklar — Turkiyaniki 🇹🇷",
}


async def qabulga_yozilish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🩸 Hijoma",
                callback_data="category_h"
            )
        ],
        [
            InlineKeyboardButton(
                "💆 Massaj",
                callback_data="category_m"
            )
        ],
        [
            InlineKeyboardButton(
                "🪱 Zuluk",
                callback_data="category_z"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Bekor qilish",
                callback_data="booking_cancel"
            )
        ],
    ]

    await update.message.reply_text(
        "📅 QABULGA YOZILISH\n\n"
        "Avval xizmat turini tanlang 👇\n\n"
        "⏱ Har bir qabul uchun 40 daqiqa ajratiladi.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# XIZMAT TANLASH
# =========================

async def show_services(query, category):
    if category == "h":
        items = [
            ("h1", "1️⃣ Hijoma + zaytunli massaj"),
            ("h2", "2️⃣ Yuz hijomasi"),
            ("h3", "3️⃣ Chertma hijoma"),
            ("h4", "4️⃣ Lab uchun hijoma"),
            ("h5", "5️⃣ Oyoqdagi shishlar uchun hijoma"),
            ("h6", "6️⃣ Boshda hijoma"),
            ("h7", "7️⃣ Detoks hijoma"),
        ]
    elif category == "m":
        items = [
            ("m1", "1️⃣ Bitta sohaga massaj"),
            ("m2", "2️⃣ Obshiy massaj"),
            ("m3", "3️⃣ Koreyksya figura massaj"),
            ("m4", "4️⃣ Relax massaj"),
            ("m5", "5️⃣ Bo‘yin massaj"),
            ("m6", "6️⃣ Oyoq sohasiga massaj"),
            ("m7", "7️⃣ Bolalar massaji"),
            ("m8", "8️⃣ Asalli massaj"),
        ]
    else:
        items = [
            ("z1", "1️⃣ Zuluk donasi"),
            ("z2", "2️⃣ Vaginalniy zuluk"),
            ("z3", "3️⃣ Zuluklar — Turkiyaniki 🇹🇷"),
        ]

    keyboard = []

    for service_id, name in items:
        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=f"service_{service_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="booking_start"
        )
    ])

    await query.edit_message_text(
        "📋 Xizmatni tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# SANA TANLASH
# =========================

def get_available_dates():
    dates = []
    today = datetime.now(TASHKENT_TZ).date()

    for i in range(8):
        date = today + timedelta(days=i)

        # Yakshanba = 6
        if date.weekday() == 6:
            continue

        dates.append(date)

    return dates


def format_date(date):
    days = {
        0: "Dushanba",
        1: "Seshanba",
        2: "Chorshanba",
        3: "Payshanba",
        4: "Juma",
        5: "Shanba",
        6: "Yakshanba",
    }

    return f"{days[date.weekday()]} — {date.strftime('%d.%m')}"


async def show_dates(query):
    keyboard = []

    for date in get_available_dates():
        date_text = format_date(date)

        keyboard.append([
            InlineKeyboardButton(
                f"📅 {date_text}",
                callback_data=f"date_{date.isoformat()}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Xizmatni o‘zgartirish",
            callback_data="booking_start"
        )
    ])

    await query.edit_message_text(
        "📅 SANA TANLANG\n\n"
        "Yakshanba kuni qabul yo‘q.\n\n"
        "Kerakli kunni tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# VAQT TANLASH
# =========================

def get_time_slots():
    slots = []

    start_minutes = 9 * 60
    end_minutes = 17 * 60

    current = start_minutes

    while current + 40 <= end_minutes:
        hour = current // 60
        minute = current % 60

        slots.append(f"{hour:02d}:{minute:02d}")

        current += 40

    return slots


async def show_times(query, selected_date):
    date_obj = datetime.strptime(
        selected_date,
        "%Y-%m-%d"
    ).date()

    # Bugungi kun uchun o'tib ketgan vaqtlarni chiqarib tashlaymiz
    now = datetime.now(TASHKENT_TZ)

    slots = []

    for time_text in get_time_slots():
        hour, minute = map(int, time_text.split(":"))

        slot_datetime = datetime(
            date_obj.year,
            date_obj.month,
            date_obj.day,
            hour,
            minute,
            tzinfo=TASHKENT_TZ
        )

        if date_obj == now.date() and slot_datetime <= now:
            continue

        slots.append(time_text)

    if not slots:
        await query.edit_message_text(
            "😔 Bu kun uchun bo‘sh vaqt qolmagan.\n\n"
            "Boshqa kunni tanlang."
        )
        return

    keyboard = []

    row = []

    for time_text in slots:
        row.append(
            InlineKeyboardButton(
                f"🕐 {time_text}",
                callback_data=f"time_{selected_date}_{time_text}"
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Sanani o‘zgartirish",
            callback_data="booking_dates"
        )
    ])

    await query.edit_message_text(
        f"📅 {format_date(date_obj)}\n\n"
        "🕐 BO‘SH VAQTNI TANLANG\n\n"
        "Har bir qabul 40 daqiqa.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# CALLBACKLAR
# =========================

async def booking_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # Booking boshlash
    if data == "booking_start":
        keyboard = [
            [
                InlineKeyboardButton(
                    "🩸 Hijoma",
                    callback_data="category_h"
                )
            ],
            [
                InlineKeyboardButton(
                    "💆 Massaj",
                    callback_data="category_m"
                )
            ],
            [
                InlineKeyboardButton(
                    "🪱 Zuluk",
                    callback_data="category_z"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Bekor qilish",
                    callback_data="booking_cancel"
                )
            ],
        ]

        await query.edit_message_text(
            "📅 QABULGA YOZILISH\n\n"
            "Avval xizmat turini tanlang 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Kategoriya
    elif data.startswith("category_"):
        category = data.split("_")[1]
        await show_services(query, category)

    # Xizmat
    elif data.startswith("service_"):
        service_id = data.replace("service_", "")

        if service_id not in SERVICES:
            await query.edit_message_text(
                "❌ Xizmat topilmadi."
            )
            return

        context.user_data["booking_service"] = service_id

        await show_dates(query)

    # Sana
    elif data.startswith("date_"):
        selected_date = data.replace("date_", "")

        context.user_data["booking_date"] = selected_date

        await show_times(query, selected_date)

    # Sana menyusiga qaytish
    elif data == "booking_dates":
        await show_dates(query)

    # Vaqt
    elif data.startswith("time_"):
        parts = data.split("_")

        selected_date = parts[1]
        selected_time = parts[2]

        service_id = context.user_data.get("booking_service")

        if not service_id:
            await query.edit_message_text(
                "❌ Xizmat tanlanmagan."
            )
            return

        service_name = SERVICES.get(
            service_id,
            "Noma'lum xizmat"
        )

        context.user_data["booking_date"] = selected_date
        context.user_data["booking_time"] = selected_time

        date_obj = datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        ).date()

        await query.edit_message_text(
            "✅ VAQT TANLANDI\n\n"
            f"🩸 Xizmat: {service_name}\n"
            f"📅 Sana: {format_date(date_obj)}\n"
            f"🕐 Vaqt: {selected_time}\n\n"
            "⏱ Davomiyligi: 40 daqiqa\n\n"
            "Keyingi bosqichda ism va telefon raqamini "
            "olib, qabulni tasdiqlaymiz."
        )

    # Bekor qilish
    elif data == "booking_cancel":
        await query.edit_message_text(
            "❌ Qabulga yozilish bekor qilindi.\n\n"
            "Asosiy menyudan boshqa bo‘limni tanlashingiz mumkin."
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
        await qabulga_yozilish(update, context)

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
            "🕐 Dushanba–Shanba: 09:00–17:00\n"
            "🚫 Yakshanba: dam olish kuni"
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

    # Render health server
    threading.Thread(
        target=start_server,
        daemon=True
    ).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    # Inline tugmalar
    app.add_handler(
        CallbackQueryHandler(
            booking_callback,
            pattern="^(booking_|category_|service_|date_|time_)"
        )
    )

    # Oddiy menyu tugmalari
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
