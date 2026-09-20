import os
import sqlite3
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


# =========================
# SOZLAMALAR
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

DB_FILE = "bookings.db"


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
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            created_at TEXT NOT NULL,
            reminded INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def is_time_booked(booking_date, booking_time):
    conn = get_db()

    row = conn.execute("""
        SELECT id
        FROM bookings
        WHERE booking_date = ?
        AND booking_time = ?
    """, (booking_date, booking_time)).fetchone()

    conn.close()

    return row is not None


def save_booking(
    user_id,
    name,
    phone,
    service,
    booking_date,
    booking_time
):
    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO bookings
        (
            user_id,
            name,
            phone,
            service,
            booking_date,
            booking_time,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        name,
        phone,
        service,
        booking_date,
        booking_time,
        datetime.now(TASHKENT_TZ).isoformat()
    ))

    booking_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return booking_id


# =========================
# ADMIN PANEL
# =========================

def is_admin(user_id):
    return ADMIN_CHAT_ID and str(user_id) == str(ADMIN_CHAT_ID)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text(
            "❌ Bu bo‘lim faqat operator uchun."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "📋 Bugungi bronlar",
                callback_data="admin_today"
            )
        ],
        [
            InlineKeyboardButton(
                "📅 Barcha bronlar",
                callback_data="admin_all"
            )
        ],
    ]

    await update.message.reply_text(
        "👩‍💼 ADMIN PANEL\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_admin_today(query):
    conn = get_db()

    today = datetime.now(
        TASHKENT_TZ
    ).date().isoformat()

    rows = conn.execute("""
        SELECT *
        FROM bookings
        WHERE booking_date = ?
        ORDER BY booking_time
    """, (today,)).fetchall()

    conn.close()

    if not rows:
        await query.edit_message_text(
            "📋 BUGUNGI BRONLAR\n\n"
            "Bugun bronlar yo‘q."
        )
        return

    text = "📋 BUGUNGI BRONLAR\n\n"

    for row in rows:
        text += (
            f"🆔 #{row['id']}\n"
            f"🕐 {row['booking_time']}\n"
            f"👤 {row['name']}\n"
            f"📞 {row['phone']}\n"
            f"🩸 {row['service']}\n\n"
        )

    await query.edit_message_text(text)


async def show_admin_all(query):
    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM bookings
        ORDER BY booking_date, booking_time
        LIMIT 50
    """).fetchall()

    conn.close()

    if not rows:
        await query.edit_message_text(
            "📋 BRONLAR\n\n"
            "Hozircha bronlar yo‘q."
        )
        return

    text = "📋 OXIRGI 50 TA BRON\n\n"

    for row in rows:
        text += (
            f"🆔 #{row['id']}\n"
            f"📅 {row['booking_date']}\n"
            f"🕐 {row['booking_time']}\n"
            f"👤 {row['name']}\n"
            f"📞 {row['phone']}\n"
            f"🩸 {row['service']}\n\n"
        )

    await query.edit_message_text(text)


# =========================
# XIZMATLAR
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

    await update.message.reply_text(
        "🌷 Assalomu alaykum!\n\n"
        "🩸 Shafran Hijoma botiga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
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
    await update.message.reply_text(
        "🩸 HIJOMA XIZMATLARI\n\n"
        "1️⃣ Hijoma + zaytunli massaj — 300 000 so‘m\n\n"
        "2️⃣ Yuz hijomasi + yengil chiskasi bilan — 450 000 so‘m\n\n"
        "3️⃣ Chertma hijoma — 150 000 so‘m\n\n"
        "4️⃣ Lab uchun hijoma — 100 000 so‘m\n\n"
        "5️⃣ Oyoqdagi shishlar va og‘riqlar uchun hijoma — 200 000 so‘m\n\n"
        "6️⃣ Boshda hijoma — 200 000 so‘m\n\n"
        "7️⃣ Detoks hijoma — 300 000 so‘m"
    )


# =========================
# MASSAJ
# =========================

async def massaj(update: Update):
    await update.message.reply_text(
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


# =========================
# ZULUK
# =========================

async def zuluk(update: Update):
    await update.message.reply_text(
        "🪱 ZULUK XIZMATLARI\n\n"
        "1️⃣ Zuluk donasi — 50 000 so‘mdan\n\n"
        "2️⃣ Vaginalniy zuluk — 400 000 so‘m\n\n"
        "3️⃣ Zuluklar — Turkiyaniki 🇹🇷\n"
        "Narxi alohida aniqlanadi."
    )


# =========================
# QABUL BOSHLASH
# =========================

async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🩸 Hijoma",
                callback_data="cat_h"
            )
        ],
        [
            InlineKeyboardButton(
                "💆 Massaj",
                callback_data="cat_m"
            )
        ],
        [
            InlineKeyboardButton(
                "🪱 Zuluk",
                callback_data="cat_z"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Bekor qilish",
                callback_data="cancel_booking"
            )
        ],
    ]

    await update.message.reply_text(
        "📅 QABULGA YOZILISH\n\n"
        "Xizmat turini tanlang 👇",
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
# SANA
# =========================

def day_name(date):
    names = [
        "Dushanba",
        "Seshanba",
        "Chorshanba",
        "Payshanba",
        "Juma",
        "Shanba",
        "Yakshanba"
    ]

    return names[date.weekday()]


def get_dates():
    result = []

    today = datetime.now(
        TASHKENT_TZ
    ).date()

    for i in range(14):
        date = today + timedelta(days=i)

        if date.weekday() == 6:
            continue

        result.append(date)

    return result


async def show_dates(query):
    keyboard = []

    for date in get_dates():
        keyboard.append([
            InlineKeyboardButton(
                f"📅 {day_name(date)} — "
                f"{date.strftime('%d.%m')}",
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
        "📅 SANANI TANLANG\n\n"
        "🚫 Yakshanba kuni qabul yo‘q.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# VAQTLAR
# =========================

def get_time_slots():
    result = []

    current = 9 * 60
    end = 17 * 60

    while current + 40 <= end:
        hour = current // 60
        minute = current % 60

        result.append(
            f"{hour:02d}:{minute:02d}"
        )

        current += 40

    return result


async def show_times(query, selected_date):
    date_obj = datetime.strptime(
        selected_date,
        "%Y-%m-%d"
    ).date()

    now = datetime.now(TASHKENT_TZ)

    available = []

    for time_text in get_time_slots():
        hour, minute = map(
            int,
            time_text.split(":")
        )

        slot = datetime(
            date_obj.year,
            date_obj.month,
            date_obj.day,
            hour,
            minute,
            tzinfo=TASHKENT_TZ
        )

        if date_obj == now.date() and slot <= now:
            continue

        if not is_time_booked(
            selected_date,
            time_text
        ):
            available.append(time_text)

    if not available:
        await query.edit_message_text(
            "😔 Bu kun uchun bo‘sh vaqt qolmagan.\n\n"
            "Boshqa kunni tanlang."
        )
        return

    keyboard = []
    row = []

    for time_text in available:
        row.append(
            InlineKeyboardButton(
                f"🕐 {time_text}",
                callback_data=(
                    f"time_{selected_date}_{time_text}"
                )
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
        f"📅 {day_name(date_obj)} — "
        f"{date_obj.strftime('%d.%m.%Y')}\n\n"
        "🕐 BO‘SH VAQTNI TANLANG\n\n"
        "⏱ Har bir qabul: 40 daqiqa",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# CALLBACK
# =========================

async def booking_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    data = query.data

    # =====================
    # ADMIN
    # =====================

    if data == "admin_today":
        if not is_admin(query.from_user.id):
            await query.edit_message_text(
                "❌ Ruxsat yo‘q."
            )
            return

        await show_admin_today(query)
        return

    if data == "admin_all":
        if not is_admin(query.from_user.id):
            await query.edit_message_text(
                "❌ Ruxsat yo‘q."
            )
            return

        await show_admin_all(query)
        return

    # =====================
    # BOOKING
    # =====================

    if data == "booking_start":
        keyboard = [
            [
                InlineKeyboardButton(
                    "🩸 Hijoma",
                    callback_data="cat_h"
                )
            ],
            [
                InlineKeyboardButton(
                    "💆 Massaj",
                    callback_data="cat_m"
                )
            ],
            [
                InlineKeyboardButton(
                    "🪱 Zuluk",
                    callback_data="cat_z"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Bekor qilish",
                    callback_data="cancel_booking"
                )
            ],
        ]

        await query.edit_message_text(
            "📅 QABULGA YOZILISH\n\n"
            "Xizmat turini tanlang 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("cat_"):
        category = data.replace(
            "cat_",
            ""
        )

        await show_services(
            query,
            category
        )

    elif data.startswith("service_"):
        service_id = data.replace(
            "service_",
            ""
        )

        if service_id not in SERVICES:
            await query.edit_message_text(
                "❌ Xizmat topilmadi."
            )
            return

        context.user_data[
            "service_id"
        ] = service_id

        await show_dates(query)

    elif data.startswith("date_"):
        selected_date = data.replace(
            "date_",
            ""
        )

        context.user_data[
            "booking_date"
        ] = selected_date

        await show_times(
            query,
            selected_date
        )

    elif data == "booking_dates":
        await show_dates(query)

    elif data.startswith("time_"):
        parts = data.split("_")

        selected_date = parts[1]
        selected_time = parts[2]

        service_id = context.user_data.get(
            "service_id"
        )

        if not service_id:
            await query.edit_message_text(
                "❌ Xizmat topilmadi."
            )
            return

        if is_time_booked(
            selected_date,
            selected_time
        ):
            await query.edit_message_text(
                "😔 Bu vaqt hozirgina band qilindi.\n\n"
                "Iltimos, boshqa vaqtni tanlang."
            )
            return

        context.user_data[
            "booking_time"
        ] = selected_time

        service_name = SERVICES[service_id]

        date_obj = datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        ).date()

        await query.edit_message_text(
            "✅ VAQT TANLANDI\n\n"
            f"🩸 Xizmat:\n{service_name}\n\n"
            f"📅 Sana: {day_name(date_obj)} — "
            f"{date_obj.strftime('%d.%m.%Y')}\n"
            f"🕐 Vaqt: {selected_time}\n"
            "⏱ Davomiyligi: 40 daqiqa\n\n"
            "Endi ismingizni yozing 👇"
        )

        context.user_data[
            "booking_step"
        ] = "name"

    elif data == "cancel_booking":
        context.user_data.clear()

        await query.edit_message_text(
            "❌ Qabulga yozilish bekor qilindi."
        )

    elif data == "confirm_booking":
        await finish_booking(
            query,
            context
        )

    elif data == "edit_booking":
        context.user_data[
            "booking_step"
        ] = "name"

        await query.edit_message_text(
            "✏️ Ismingizni qaytadan yozing:"
        )


# =========================
# ISM
# =========================

async def handle_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if context.user_data.get(
        "booking_step"
    ) != "name":
        return

    name = update.message.text.strip()

    if len(name) < 2:
        await update.message.reply_text(
            "Iltimos, ismingizni to‘liqroq yozing 🙂"
        )
        return

    context.user_data["name"] = name
    context.user_data[
        "booking_step"
    ] = "phone"

    keyboard = [
        [
            KeyboardButton(
                "📞 Telefon raqamni yuborish",
                request_contact=True
            )
        ],
        [
            KeyboardButton(
                "❌ Bekor qilish"
            )
        ]
    ]

    await update.message.reply_text(
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


# =========================
# TELEFON
# =========================

async def handle_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if context.user_data.get(
        "booking_step"
    ) != "phone":
        return

    phone = None

    if update.message.contact:
        phone = update.message.contact.phone_number

    elif update.message.text:
        phone = update.message.text.strip()

    if not phone:
        await update.message.reply_text(
            "📞 Telefon raqamingizni yuboring."
        )
        return

    context.user_data["phone"] = phone
    context.user_data[
        "booking_step"
    ] = "confirm"

    service_id = context.user_data.get(
        "service_id"
    )

    booking_date = context.user_data.get(
        "booking_date"
    )

    booking_time = context.user_data.get(
        "booking_time"
    )

    name = context.user_data.get(
        "name"
    )

    service_name = SERVICES.get(
        service_id,
        "Noma'lum xizmat"
    )

    date_obj = datetime.strptime(
        booking_date,
        "%Y-%m-%d"
    ).date()

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Tasdiqlash",
                callback_data="confirm_booking"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ O‘zgartirish",
                callback_data="edit_booking"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Bekor qilish",
                callback_data="cancel_booking"
            )
        ],
    ]

    await update.message.reply_text(
        "📋 QABUL MA'LUMOTLARI\n\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}\n"
        f"🩸 Xizmat: {service_name}\n"
        f"📅 Sana: {day_name(date_obj)} — "
        f"{date_obj.strftime('%d.%m.%Y')}\n"
        f"🕐 Vaqt: {booking_time}\n"
        "⏱ Davomiyligi: 40 daqiqa\n\n"
        "Ma'lumotlar to‘g‘rimi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# BRONNI YAKUNLASH
# =========================

async def finish_booking(
    query,
    context
):
    user = query.from_user

    service_id = context.user_data.get(
        "service_id"
    )

    booking_date = context.user_data.get(
        "booking_date"
    )

    booking_time = context.user_data.get(
        "booking_time"
    )

    name = context.user_data.get(
        "name"
    )

    phone = context.user_data.get(
        "phone"
    )

    if not all([
        service_id,
        booking_date,
        booking_time,
        name,
        phone
    ]):
        await query.edit_message_text(
            "❌ Ma'lumotlar to‘liq emas.\n\n"
            "Qabulga qaytadan yoziling."
        )

        context.user_data.clear()
        return

    if is_time_booked(
        booking_date,
        booking_time
    ):
        await query.edit_message_text(
            "😔 Kechirasiz, bu vaqt boshqa mijoz "
            "tomonidan band qilindi.\n\n"
            "Iltimos, boshqa vaqtni tanlang."
        )

        context.user_data.clear()
        return

    service_name = SERVICES[
        service_id
    ]

    booking_id = save_booking(
        user.id,
        name,
        phone,
        service_name,
        booking_date,
        booking_time
    )

    date_obj = datetime.strptime(
        booking_date,
        "%Y-%m-%d"
    ).date()

    # =====================
    # MIJOZGA
    # =====================

    await query.edit_message_text(
        "🎉 QABUL MUVAFFAQIYATLI BAND QILINDI!\n\n"
        f"🆔 Bron raqami: #{booking_id}\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}\n"
        f"🩸 Xizmat: {service_name}\n"
        f"📅 Sana: {day_name(date_obj)} — "
        f"{date_obj.strftime('%d.%m.%Y')}\n"
        f"🕐 Vaqt: {booking_time}\n\n"
        "🌷 Sizni kutamiz!\n"
        "📍 General Uzoqov 32-uy"
    )

    # =====================
    # OPERATORGA
    # =====================

    if ADMIN_CHAT_ID:
        try:
            await query.get_bot().send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    "🔔 YANGI QABUL!\n\n"
                    f"🆔 Bron: #{booking_id}\n"
                    f"👤 Ism: {name}\n"
                    f"📞 Telefon: {phone}\n"
                    f"🩸 Xizmat: {service_name}\n"
                    f"📅 Sana: "
                    f"{date_obj.strftime('%d.%m.%Y')}\n"
                    f"🕐 Vaqt: {booking_time}\n"
                    f"👤 Telegram ID: {user.id}"
                )
            )
        except Exception:
            pass

    context.user_data.clear()


# =========================
# Eslatma
# =========================

async def reminder_job(
    context: ContextTypes.DEFAULT_TYPE
):
    now = datetime.now(TASHKENT_TZ)

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM bookings
        WHERE reminded = 0
    """).fetchall()

    for row in rows:
        try:
            booking_datetime = datetime.strptime(
                f"{row['booking_date']} "
                f"{row['booking_time']}",
                "%Y-%m-%d %H:%M"
            ).replace(
                tzinfo=TASHKENT_TZ
            )

            difference = (
                booking_datetime - now
            )

            if (
                timedelta(minutes=0)
                < difference
                <= timedelta(minutes=60)
            ):
                await context.bot.send_message(
                    chat_id=row["user_id"],
                    text=(
                        "⏰ QABULINGIZGA 1 SOAT QOLDI!\n\n"
                        f"🩸 {row['service']}\n"
                        f"📅 {row['booking_date']}\n"
                        f"🕐 {row['booking_time']}\n\n"
                        "🌷 Sizni Shafran Hijomada kutamiz!"
                    )
                )

                conn.execute("""
                    UPDATE bookings
                    SET reminded = 1
                    WHERE id = ?
                """, (row["id"],))

        except Exception:
            pass

    conn.commit()
    conn.close()


# =========================
# QOLGAN MENYU
# =========================

async def menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text

    if text == "💰 Xizmatlar va narxlar":
        await xizmatlar_menu(update)

    elif text == "🩸 Hijoma":
        await hijoma(update)

    elif text == "💆 Massaj":
        await massaj(update)

    elif text == "🪱 Zuluk":
        await zuluk(update)

    elif text == "🔙 Asosiy menyu":
        await start(update, context)

    elif text == "📅 Qabulga yozilish":
        await start_booking(update, context)

    elif text == "ℹ️ Hijoma haqida":
        await update.message.reply_text(
            "🩸 HIJOMA HAQIDA\n\n"
            "Hijoma qadimdan qo‘llanib kelgan "
            "an’anaviy muolaja usullaridan biridir.\n\n"
            "🌷 Shafran Hijomada muolajalar tozalik "
            "va ehtiyotkorlikka rioya qilgan holda "
            "amalga oshiriladi."
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

    elif text == "❌ Bekor qilish":
        context.user_data.clear()

        await start(update, context)


# =========================
# BOOKING TEXT HANDLER
# =========================

async def handle_booking_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    step = context.user_data.get(
        "booking_step"
    )

    if step == "name":
        await handle_name(
            update,
            context
        )
        return

    if step == "phone":
        await handle_phone(
            update,
            context
        )
        return

    await menu(
        update,
        context
    )


# =========================
# MAIN
# =========================

def main():
    print("BOT STARTING...", flush=True)
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN topilmadi"
        )

    init_db()

    threading.Thread(
        target=start_server,
        daemon=True
    ).start()

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # START
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # ADMIN
    app.add_handler(
        CommandHandler(
            "admin",
            admin_panel
        )
    )

    # CALLBACK
    app.add_handler(
        CallbackQueryHandler(
            booking_callback
        )
    )

    # CONTACT
    app.add_handler(
        MessageHandler(
            filters.CONTACT,
            handle_phone
        )
    )

    # TEXT
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_booking_text
        )
    )

    # REMINDER
    if app.job_queue:
        app.job_queue.run_repeating(
            reminder_job,
            interval=60,
            first=10
        )

    # RUN
    app.run_polling(
        drop_pending_updates=True
    )


# =========================
# START
# =========================

if __name__ == "__main__":
    main()
