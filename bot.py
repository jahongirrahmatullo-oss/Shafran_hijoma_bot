import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
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
TZ = ZoneInfo("Asia/Tashkent")

DB = "shafran_hijoma.db"

PHONE = "+998 94 504 09 18"
ADDRESS = "Toshkent shahri, Shayxontohur tumani, General Uzoqov 32-uy"
CHANNEL = "https://t.me/Shafran_hijoma"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=General+Uzoqov+32%2C+Tashkent%2C+Uzbekistan"


SERVICES = {
    "hijoma": [
        ("Hijoma + zaytunli massaj", "300 000 so‘m"),
        ("Yuz hijomasi + yengil chiskasi bilan", "450 000 so‘m"),
        ("Chertma hijoma", "150 000 so‘m"),
        ("Lab uchun hijoma", "100 000 so‘m"),
        ("Oyoqdagi shishlar va og‘riqlar uchun hijoma", "200 000 so‘m"),
        ("Boshda hijoma", "200 000 so‘m"),
        ("Detoks hijoma", "300 000 so‘m"),
    ],
    "massaj": [
        ("Bitta sohaga massaj", "100 000 so‘m"),
        ("Obshiy massaj", "400 000 so‘m"),
        ("Koreyksya figura massaj", "300 000 so‘m"),
        ("Relax massaj", "300 000 so‘m"),
        ("Bo‘yin massaj", "90 000 so‘m"),
        ("Oyoq sohasiga massaj", "90 000 so‘m"),
        ("Bollar massaj", "60 000 dan 130 000 so‘m gacha"),
        ("Asalli massaj", "150 000 so‘m"),
    ],
    "zuluk": [
        ("Zuluk donasi", "50 000 so‘mdan"),
        ("Vaginalniy zuluk", "400 000 so‘m"),
        ("Zuluklar — Turkiyaniki 🇹🇷", "Narxi aniqlanadi"),
    ],
}


def import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
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
TZ = ZoneInfo("Asia/Tashkent")

DB = "shafran_hijoma.db"

PHONE = "+998 94 504 09 18"
ADDRESS = "Toshkent shahri, Shayxontohur tumani, General Uzoqov 32-uy"
CHANNEL = "https://t.me/Shafran_hijoma"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=General+Uzoqov+32%2C+Tashkent%2C+Uzbekistan"


SERVICES = {
    "hijoma": [
        ("Hijoma + zaytunli massaj", "300 000 so‘m"),
        ("Yuz hijomasi + yengil chiskasi bilan", "450 000 so‘m"),
        ("Chertma hijoma", "150 000 so‘m"),
        ("Lab uchun hijoma", "100 000 so‘m"),
        ("Oyoqdagi shishlar va og‘riqlar uchun hijoma", "200 000 so‘m"),
        ("Boshda hijoma", "200 000 so‘m"),
        ("Detoks hijoma", "300 000 so‘m"),
    ],
    "massaj": [
        ("Bitta sohaga massaj", "100 000 so‘m"),
        ("Obshiy massaj", "400 000 so‘m"),
        ("Koreyksya figura massaj", "300 000 so‘m"),
        ("Relax massaj", "300 000 so‘m"),
        ("Bo‘yin massaj", "90 000 so‘m"),
        ("Oyoq sohasiga massaj", "90 000 so‘m"),
        ("Bollar massaj", "60 000 dan 130 000 so‘m gacha"),
        ("Asalli massaj", "150 000 so‘m"),
    ],
    "zuluk": [
        ("Zuluk donasi", "50 000 so‘mdan"),
        ("Vaginalniy zuluk", "400 000 so‘m"),
        ("Zuluklar — Turkiyaniki 🇹🇷", "Narxi aniqlanadi"),
    ],
}


def db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            service TEXT,
            date TEXT,
            time TEXT,
            name TEXT,
            phone TEXT,
            reminded INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📅 Qabulga yozilish"],
            ["💰 Xizmatlar va narxlar"],
            ["🩸 Hijoma muolajalari", "💆 Massaj muolajalari"],
            ["🪱 Zuluk muolajalari"],
            ["ℹ️ Hijoma haqida"],
            ["📍 Manzil", "📞 Operator bilan bog‘lanish"],
            ["📢 Kanalimiz"],
        ],
        resize_keyboard=True
    )


def category_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🩸 Hijoma", callback_data="bookcat:hijoma")],
        [InlineKeyboardButton("💆 Massaj", callback_data="bookcat:massaj")],
        [InlineKeyboardButton("🪱 Zuluk", callback_data="bookcat:zuluk")],
    ])


def service_keyboard(category):
    buttons = []

    for i, (name, price) in enumerate(SERVICES[category]):
        buttons.append([
            InlineKeyboardButton(
                f"{name} — {price}",
                callback_data=f"service:{category}:{i}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("⬅️ Orqaga", callback_data="back:categories")
    ])

    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    text = (
        "🌷 Shafran Hijoma markaziga xush kelibsiz!\n\n"
        "Quyidagi bo‘limlardan birini tanlang:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard()
    )


async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 XIZMATLAR VA NARXLAR\n\n"
        "🩸 HIJOMA\n"
        "• Hijoma + zaytunli massaj — 300 000 so‘m\n"
        "• Yuz hijomasi + yengil chiskasi bilan — 450 000 so‘m\n"
        "• Chertma hijoma — 150 000 so‘m\n"
        "• Lab uchun hijoma — 100 000 so‘m\n"
        "• Oyoqdagi shishlar va og‘riqlar uchun hijoma — 200 000 so‘m\n"
        "• Boshda hijoma — 200 000 so‘m\n"
        "• Detoks hijoma — 300 000 so‘m\n\n"
        "💆 MASSAJ\n"
        "• Bitta sohaga massaj — 100 000 so‘m\n"
        "• Obshiy massaj — 400 000 so‘m\n"
        "• Koreyksya figura massaj — 300 000 so‘m\n"
        "• Relax massaj — 300 000 so‘m\n"
        "• Bo‘yin massaj — 90 000 so‘m\n"
        "• Oyoq sohasiga massaj — 90 000 so‘m\n"
        "• Bollar massaj — 60 000 dan 130 000 so‘m gacha\n"
        "• Asalli massaj — 150 000 so‘m\n\n"
        "🪱 ZULUK\n"
        "• Zuluk donasi — 50 000 so‘mdan\n"
        "• Vaginalniy zuluk — 400 000 so‘m\n"
        "• Zuluklar — Turkiyaniki 🇹🇷"
    )


async def hijoma_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🩸 HIJOMA MUOLAJALARI\n\nKerakli xizmatni tanlang:",
        reply_markup=service_keyboard("hijoma")
    )


async def massaj_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💆 MASSAJ MUOLAJALARI\n\nKerakli xizmatni tanlang:",
        reply_markup=service_keyboard("massaj")
    )


async def zuluk_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🪱 ZULUK MUOLAJALARI\n\nKerakli xizmatni tanlang:",
        reply_markup=service_keyboard("zuluk")
    )


async def hijoma_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

🕐 Har kuni: 09:00–17:00"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Qabulga yozilish", callback_data="booking:start")],
        [InlineKeyboardButton("📞 Telefon qilish", url="tel:+998945040918")],
    ])

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📍 MANZIL\n\n"
        f"🏠 {ADDRESS}\n\n"
        "🕐 Ish vaqti: har kuni 09:00–17:00\n\n"
        f"📞 {PHONE}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺️ Xaritada ochish", url=MAP_URL)],
        [InlineKeyboardButton("📞 Telefon qilish", url="tel:+998945040918")],
    ])

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )


async def operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Operatorga qo‘ng‘iroq", url="tel:+998945040918")]
    ])

    await update.message.reply_text(
        f"📞 Operator bilan bog‘lanish\n\n{PHONE}",
        reply_markup=keyboard
    )


async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga o‘tish", url=CHANNEL)]
    ])

    await update.message.reply_text(
        "🌷 Bizning Telegram kanalimiz:",
        reply_markup=keyboard
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "booking:start" or data == "back:categories":
        context.user_data.clear()

        await query.message.reply_text(
            "📅 Qabulga yozilish\n\n"
            "Muolaja turini tanlang:",
            reply_markup=category_keyboard()
        )
        return

    if data.startswith("bookcat:"):
        category = data.split(":")[1]
        context.user_data["category"] = category

        await query.message.reply_text(
            "Kerakli xizmatni tanlang:",
            reply_markup=service_keyboard(category)
        )
        return

    if data.startswith("service:"):
        _, category, index = data.split(":")
        index = int(index)

        name, price = SERVICES[category][index]

        context.user_data["service"] = name
        context.user_data["price"] = price
        context.user_data["step"] = "date"

        info = ""

        if category == "hijoma":
            info = (
                "\n\nℹ️ Muolaja bo‘yicha aniq tavsiyalar "
                "mijozning individual holatiga qarab beriladi."
            )

        await query.message.reply_text(
            f"🌷 {name}\n"
            f"💰 Narxi: {price}"
            f"{info}\n\n"
            "📅 Qaysi sanaga yozilmoqchisiz?\n\n"
            "Masalan: 25.09.2026"
        )
        return


async def booking_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("step")

    if not step:
        return

    if step == "date":
        try:
            date_obj = datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            await update.message.reply_text(
                "❗ Sana noto‘g‘ri.\n"
                "Masalan: 25.09.2026"
            )
            return

        today = datetime.now(TZ).date()

        if date_obj < today:
            await update.message.reply_text(
                "❗ O‘tgan sanani tanlab bo‘lmaydi.\n"
                "Iltimos, boshqa sana kiriting."
            )
            return

        context.user_data["date"] = text
        context.user_data["step"] = "time"

        await update.message.reply_text(
            "🕐 Vaqtni kiriting.\n\n"
            "Masalan: 14:30\n\n"
            "Qabul vaqti: 09:00–17:00"
        )
        return

    if step == "time":
        try:
            time_obj = datetime.strptime(text, "%H:%M").time()
        except ValueError:
            await update.message.reply_text(
                "❗ Vaqt noto‘g‘ri.\n"
                "Masalan: 14:30"
            )
            return

        if time_obj < datetime.strptime("09:00", "%H:%M").time():
            await update.message.reply_text("❗ Qabul 09:00 dan boshlanadi.")
            return

        if time_obj > datetime.strptime("17:00", "%H:%M").time():
            await update.message.reply_text("❗ Qabul 17:00 gacha.")
            return

        date = context.user_data["date"]

        conn = db()
        existing = conn.execute(
            "SELECT id FROM bookings WHERE date=? AND time=?",
            (date, text)
        ).fetchone()
        conn.close()

        if existing:
            await update.message.reply_text(
                "❗ Bu vaqt band.\n"
                "Iltimos, boshqa vaqt tanlang."
            )
            return

        context.user_data["time"] = text
        context.user_data["step"] = "name"

        await update.message.reply_text(
            "👤 Ismingizni kiriting:"
        )
        return

    if step == "name":
        context.user_data["name"] = text
        context.user_data["step"] = "phone"

        await update.message.reply_text(
            "📞 Telefon raqamingizni kiriting:"
        )
        return

    if step == "phone":
        phone = text

        if len(phone) < 7:
            await update.message.reply_text(
                "❗ Telefon raqam noto‘g‘ri ko‘rinmoqda.\n"
                "Iltimos, qayta kiriting."
            )
            return

        context.user_data["phone"] = phone

        service = context.user_data["service"]
        price = context.user_data["price"]
        date = context.user_data["date"]
        time = context.user_data["time"]
        name = context.user_data["name"]

        username = update.effective_user.username or ""

        conn = db()

        cur = conn.execute(
            """
            INSERT INTO bookings
            (user_id, username, service, date, time, name, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                update.effective_user.id,
                username,
                service,
                date,
                time,
                name,
                phone
            )
        )

        booking_id = cur.lastrowid
        conn.commit()

        admins = conn.execute(
            "SELECT user_id FROM admins"
        ).fetchall()

        conn.close()

        await update.message.reply_text(
            "✅ QABULGA YOZILISH QABUL QILINDI!\n\n"
            f"🆔 Buyurtma: #{booking_id}\n"
            f"🌷 Xizmat: {service}\n"
            f"💰 Narxi: {price}\n"
            f"📅 Sana: {date}\n"
            f"🕐 Vaqt: {time}\n"
            f"👤 Ism: {name}\n"
            f"📞 Telefon: {phone}\n\n"
            "Operator siz bilan bog‘lanadi.",
            reply_markup=main_keyboard()
        )

        admin_text = (
            "🔔 YANGI QABUL!\n\n"
            f"🆔 #{booking_id}\n"
            f"🌷 Xizmat: {service}\n"
            f"💰 Narxi: {price}\n"
            f"📅 Sana: {date}\n"
            f"🕐 Vaqt: {time}\n"
            f"👤 Ism: {name}\n"
            f"📞 Telefon: {phone}\n"
            f"👤 Telegram: @{username if username else 'yo‘q'}"
        )

        for admin in admins:
            try:
                await context.bot.send_message(
                    chat_id=admin[0],
                    text=admin_text
                )
            except Exception:
                pass

        context.user_data.clear()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "❌ Qabulga yozilish bekor qilindi.",
        reply_markup=main_keyboard()
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ("administrator", "creator"):
        await update.message.reply_text(
            "❌ Bu buyruq faqat guruh administratorlari uchun."
        )
        return

    conn = db()

    conn.execute(
        "INSERT OR IGNORE INTO admins (user_id) VALUES (?)",
        (update.effective_user.id,)
    )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        "✅ Siz admin sifatida ro‘yxatdan o‘tdingiz.\n\n"
        "Endi shaxsiy chatda /admin buyrug‘ini yuboring."
    )


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db()

    admin_exists = conn.execute(
        "SELECT user_id FROM admins WHERE user_id=?",
        (update.effective_user.id,)
    ).fetchone()

    conn.close()

    if not admin_exists:
        await update.message.reply_text(
            "❌ Siz admin sifatida ro‘yxatdan o‘tmagansiz."
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Qabullar", callback_data="admin:bookings")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin:stats")],
    ])

    await update.message.reply_text(
        "👑 ADMIN PANEL",
        reply_markup=keyboard
    )


async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = db()

    admin_exists = conn.execute(
        "SELECT user_id FROM admins WHERE user_id=?",
        (query.from_user.id,)
    ).fetchone()

    if not admin_exists:
        conn.close()
        return

    if query.data == "admin:bookings":
        rows = conn.execute(
            """
            SELECT id, service, date, time, name, phone
            FROM bookings
            ORDER BY id DESC
            LIMIT 20
            """
        ).fetchall()

        conn.close()

        if not rows:
            await query.message.reply_text(
                "📅 Hozircha qabullar yo‘q."
            )
            return

        text = "📅 SO‘NGGI QABULLAR\n\n"

        for row in rows:
            text += (
                f"#{row[0]}\n"
                f"🌷 {row[1]}\n"
                f"📅 {row[2]}  🕐 {row[3]}\n"
                f"👤 {row[4]}\n"
                f"📞 {row[5]}\n\n"
            )

        await query.message.reply_text(text)
        return

    if query.data == "admin:stats":
        total = conn.execute(
            "SELECT COUNT(*) FROM bookings"
        ).fetchone()[0]

        today = datetime.now(TZ).strftime("%d.%m.%Y")

        today_count = conn.execute(
            "SELECT COUNT(*) FROM bookings WHERE date=?",
            (today,)
        ).fetchone()[0]

        conn.close()

        await query.message.reply_text(
            "📊 STATISTIKA\n\n"
            f"📅 Jami qabullar: {total}\n"
            f"🕐 Bugungi qabullar: {today_count}"
        )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 GURUH QOIDALARI\n\n"
        "1️⃣ Reklama va spam taqiqlanadi.\n"
        "2️⃣ Shubhali havolalar yubormang.\n"
        "3️⃣ Hurmat bilan muloqot qiling.\n"
        "4️⃣ Takroriy spam uchun foydalanuvchi vaqtincha cheklanadi."
    )


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    for member in update.message.new_chat_members:
        try:
            await update.message.reply_text(
                f"🌷 Xush kelibsiz, {member.full_name}!\n\n"
                "Shafran Hijoma guruhiga xush kelibsiz."
            )

            try:
                await update.message.delete()
            except Exception:
                pass

        except Exception:
            pass


async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except Exception:
        pass


async def spam_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    spam_words = [
        "reklama",
        "reklamа",
        "casino",
        "stavka",
        "bet",
        "forex",
        "telegram.me",
        "t.me/",
    ]

    has_link = (
        "http://" in text
        or "https://" in text
        or "www." in text
        or "t.me/" in text
    )

    has_spam_word = any(word in text for word in spam_words)

    if not has_link and not has_spam_word:
        return

    user_id = update.effective_user.id

    warnings = context.application.bot_data.setdefault(
        "warnings",
        {}
    )

    count = warnings.get(user_id, 0) + 1
    warnings[user_id] = count

    try:
        await update.message.delete()
    except Exception:
        pass

    if count == 1:
        try:
            await update.effective_chat.send_message(
                f"⚠️ {update.effective_user.full_name}, "
                "reklama/spam yuborish mumkin emas.\n"
                "Bu birinchi ogohlantirish."
            )
        except Exception:
            pass

    else:
        try:
            until = datetime.now(TZ) + timedelta(hours=1)

            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                permissions={
                    "can_send_messages": False
                },
                until_date=until
            )

            await update.effective_chat.send_message(
                f"🔇 {update.effective_user.full_name} "
                "1 soatga cheklab qo‘yildi."
            )
        except Exception:
            pass


async def reminder_loop(application):
    while True:
        try:
            now = datetime.now(TZ)

            conn = db()

            rows = conn.execute(
                """
                SELECT id, user_id, service, date, time
                FROM bookings
                WHERE reminded=0
                """
            ).fetchall()

            for row in rows:
                booking_id, user_id, service, date, time = row

                try:
                    dt = datetime.strptime(
                        f"{date} {time}",
                        "%d.%m.%Y %H:%M"
                    ).replace(tzinfo=TZ)
                except Exception:
                    continue

                difference = dt - now

                if timedelta(minutes=0) <= difference <= timedelta(hours=2):
                    try:
                        await application.bot.send_message(
                            chat_id=user_id,
                            text=(
                                "🔔 ESLATMA\n\n"
                                f"🌷 Sizning qabul vaqtingiz yaqin.\n"
                                f"Xizmat: {service}\n"
                                f"📅 {date}\n"
                                f"🕐 {time}\n\n"
                                "Shafran Hijoma sizni kutadi 🌷"
                            )
                        )

                        conn.execute(
                            "UPDATE bookings SET reminded=1 WHERE id=?",
                            (booking_id,)
                        )

                        conn.commit()

                    except Exception:
                        pass

            conn.close()

        except Exception:
            pass

        await asyncio.sleep(60)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Shafran Hijoma Bot is running!")

    def log_message(self, format, *args):
        return


def start_web_server():
    port = int(os.environ.get("PORT", "10000"))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    server.serve_forever()


async def post_init(application):
    asyncio.create_task(reminder_loop(application))


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi!")

    db()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(
        MessageHandler(
            filters.Regex("^📅 Qabulga yozilish$"),
            lambda update, context: booking_start_message(update, context)
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^💰 Xizmatlar va narxlar$"),
            services
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^🩸 Hijoma muolajalari$"),
            hijoma_category
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^💆 Massaj muolajalari$"),
            massaj_category
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^🪱 Zuluk muolajalari$"),
            zuluk_category
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^ℹ️ Hijoma haqida$"),
            hijoma_about
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📍 Manzil$"),
            address
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📞 Operator bilan bog‘lanish$"),
            operator
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📢 Kanalimiz$"),
            channel
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            admin_callbacks,
            pattern="^admin:"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callbacks
        )
    )

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome_new_member
        )
    )

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.LEFT_CHAT_MEMBER,
            left_member
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            spam_or_booking_handler
        )
    )

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


async def booking_start_message(update, context):
    context.user_data.clear()

    await update.message.reply_text(
        "📅 QABULGA YOZILISH\n\n"
        "Muolaja turini tanlang:",
        reply_markup=category_keyboard()
    )


async def spam_or_booking_handler(update, context):
    if context.user_data.get("step"):
        await booking_text(update, context)
    else:
        await spam_moderation(update, context)


if __name__ == "__main__":
    Thread(
        target=start_web_server,
        daemon=True
    ).start()

    asyncio.run(main())
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            service TEXT,
            date TEXT,
            time TEXT,
            name TEXT,
            phone TEXT,
            reminded INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📅 Qabulga yozilish"],
            ["💰 Xizmatlar va narxlar"],
            ["🩸 Hijoma muolajalari", "💆 Massaj muolajalari"],
            ["🪱 Zuluk muolajalari"],
            ["ℹ️ Hijoma haqida"],
            ["📍 Manzil", "📞 Operator bilan bog‘lanish"],
            ["📢 Kanalimiz"],
        ],
        resize_keyboard=True
    )


def category_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🩸 Hijoma", callback_data="bookcat:hijoma")],
        [InlineKeyboardButton("💆 Massaj", callback_data="bookcat:massaj")],
        [InlineKeyboardButton("🪱 Zuluk", callback_data="bookcat:zuluk")],
    ])


def service_keyboard(category):
    buttons = []

    for i, (name, price) in enumerate(SERVICES[category]):
        buttons.append([
            InlineKeyboardButton(
                f"{name} — {price}",
                callback_data=f"service:{category}:{i}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("⬅️ Orqaga", callback_data="back:categories")
    ])

    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    text = (
        "🌷 Shafran Hijoma markaziga xush kelibsiz!\n\n"
        "Quyidagi bo‘limlardan birini tanlang:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard()
    )


async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 XIZMATLAR VA NARXLAR\n\n"
        "🩸 HIJOMA\n"
        "• Hijoma + zaytunli massaj — 300 000 so‘m\n"
        "• Yuz hijomasi + yengil chiskasi bilan — 450 000 so‘m\n"
        "• Chertma hijoma — 150 000 so‘m\n"
        "• Lab uchun hijoma — 100 000 so‘m\n"
        "• Oyoqdagi shishlar va og‘riqlar uchun hijoma — 200 000 so‘m\n"
        "• Boshda hijoma — 200 000 so‘m\n"
        "• Detoks hijoma — 300 000 so‘m\n\n"
        "💆 MASSAJ\n"
        "• Bitta sohaga massaj — 100 000 so‘m\n"
        "• Obshiy massaj — 400 000 so‘m\n"
        "• Koreyksya figura massaj — 300 000 so‘m\n"
        "• Relax massaj — 300 000 so‘m\n"
        "• Bo‘yin massaj — 90 000 so‘m\n"
        "• Oyoq sohasiga massaj — 90 000 so‘m\n"
        "• Bollar massaj — 60 000 dan 130 000 so‘m gacha\n"
        "• Asalli massaj — 150 000 so‘m\n\n"
        "🪱 ZULUK\n"
        "• Zuluk donasi — 50 000 so‘mdan\n"
        "• Vaginalniy zuluk — 400 000 so‘m\n"
        "• Zuluklar — Turkiyaniki 🇹🇷"
    )


async def hijoma_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🩸 HIJOMA MUOLAJALARI\n\nKerakli xizmatni tanlang:",
        reply_markup=service_keyboard("hijoma")
    )


async def massaj_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💆 MASSAJ MUOLAJALARI\n\nKerakli xizmatni tanlang:",
        reply_markup=service_keyboard("massaj")
    )


async def zuluk_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🪱 ZULUK MUOLAJALARI\n\nKerakli xizmatni tanlang:",
        reply_markup=service_keyboard("zuluk")
    )


async def hijoma_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

🕐 Har kuni: 09:00–17:00"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Qabulga yozilish", callback_data="booking:start")],
        [InlineKeyboardButton("📞 Telefon qilish", url="tel:+998945040918")],
    ])

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📍 MANZIL\n\n"
        f"🏠 {ADDRESS}\n\n"
        "🕐 Ish vaqti: har kuni 09:00–17:00\n\n"
        f"📞 {PHONE}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺️ Xaritada ochish", url=MAP_URL)],
        [InlineKeyboardButton("📞 Telefon qilish", url="tel:+998945040918")],
    ])

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )


async def operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Operatorga qo‘ng‘iroq", url="tel:+998945040918")]
    ])

    await update.message.reply_text(
        f"📞 Operator bilan bog‘lanish\n\n{PHONE}",
        reply_markup=keyboard
    )


async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga o‘tish", url=CHANNEL)]
    ])

    await update.message.reply_text(
        "🌷 Bizning Telegram kanalimiz:",
        reply_markup=keyboard
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "booking:start" or data == "back:categories":
        context.user_data.clear()

        await query.message.reply_text(
            "📅 Qabulga yozilish\n\n"
            "Muolaja turini tanlang:",
            reply_markup=category_keyboard()
        )
        return

    if data.startswith("bookcat:"):
        category = data.split(":")[1]
        context.user_data["category"] = category

        await query.message.reply_text(
            "Kerakli xizmatni tanlang:",
            reply_markup=service_keyboard(category)
        )
        return

    if data.startswith("service:"):
        _, category, index = data.split(":")
        index = int(index)

        name, price = SERVICES[category][index]

        context.user_data["service"] = name
        context.user_data["price"] = price
        context.user_data["step"] = "date"

        info = ""

        if category == "hijoma":
            info = (
                "\n\nℹ️ Muolaja bo‘yicha aniq tavsiyalar "
                "mijozning individual holatiga qarab beriladi."
            )

        await query.message.reply_text(
            f"🌷 {name}\n"
            f"💰 Narxi: {price}"
            f"{info}\n\n"
            "📅 Qaysi sanaga yozilmoqchisiz?\n\n"
            "Masalan: 25.09.2026"
        )
        return


async def booking_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("step")

    if not step:
        return

    if step == "date":
        try:
            date_obj = datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            await update.message.reply_text(
                "❗ Sana noto‘g‘ri.\n"
                "Masalan: 25.09.2026"
            )
            return

        today = datetime.now(TZ).date()

        if date_obj < today:
            await update.message.reply_text(
                "❗ O‘tgan sanani tanlab bo‘lmaydi.\n"
                "Iltimos, boshqa sana kiriting."
            )
            return

        context.user_data["date"] = text
        context.user_data["step"] = "time"

        await update.message.reply_text(
            "🕐 Vaqtni kiriting.\n\n"
            "Masalan: 14:30\n\n"
            "Qabul vaqti: 09:00–17:00"
        )
        return

    if step == "time":
        try:
            time_obj = datetime.strptime(text, "%H:%M").time()
        except ValueError:
            await update.message.reply_text(
                "❗ Vaqt noto‘g‘ri.\n"
                "Masalan: 14:30"
            )
            return

        if time_obj < datetime.strptime("09:00", "%H:%M").time():
            await update.message.reply_text("❗ Qabul 09:00 dan boshlanadi.")
            return

        if time_obj > datetime.strptime("17:00", "%H:%M").time():
            await update.message.reply_text("❗ Qabul 17:00 gacha.")
            return

        date = context.user_data["date"]

        conn = db()
        existing = conn.execute(
            "SELECT id FROM bookings WHERE date=? AND time=?",
            (date, text)
        ).fetchone()
        conn.close()

        if existing:
            await update.message.reply_text(
                "❗ Bu vaqt band.\n"
                "Iltimos, boshqa vaqt tanlang."
            )
            return

        context.user_data["time"] = text
        context.user_data["step"] = "name"

        await update.message.reply_text(
            "👤 Ismingizni kiriting:"
        )
        return

    if step == "name":
        context.user_data["name"] = text
        context.user_data["step"] = "phone"

        await update.message.reply_text(
            "📞 Telefon raqamingizni kiriting:"
        )
        return

    if step == "phone":
        phone = text

        if len(phone) < 7:
            await update.message.reply_text(
                "❗ Telefon raqam noto‘g‘ri ko‘rinmoqda.\n"
                "Iltimos, qayta kiriting."
            )
            return

        context.user_data["phone"] = phone

        service = context.user_data["service"]
        price = context.user_data["price"]
        date = context.user_data["date"]
        time = context.user_data["time"]
        name = context.user_data["name"]

        username = update.effective_user.username or ""

        conn = db()

        cur = conn.execute(
            """
            INSERT INTO bookings
            (user_id, username, service, date, time, name, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                update.effective_user.id,
                username,
                service,
                date,
                time,
                name,
                phone
            )
        )

        booking_id = cur.lastrowid
        conn.commit()

        admins = conn.execute(
            "SELECT user_id FROM admins"
        ).fetchall()

        conn.close()

        await update.message.reply_text(
            "✅ QABULGA YOZILISH QABUL QILINDI!\n\n"
            f"🆔 Buyurtma: #{booking_id}\n"
            f"🌷 Xizmat: {service}\n"
            f"💰 Narxi: {price}\n"
            f"📅 Sana: {date}\n"
            f"🕐 Vaqt: {time}\n"
            f"👤 Ism: {name}\n"
            f"📞 Telefon: {phone}\n\n"
            "Operator siz bilan bog‘lanadi.",
            reply_markup=main_keyboard()
        )

        admin_text = (
            "🔔 YANGI QABUL!\n\n"
            f"🆔 #{booking_id}\n"
            f"🌷 Xizmat: {service}\n"
            f"💰 Narxi: {price}\n"
            f"📅 Sana: {date}\n"
            f"🕐 Vaqt: {time}\n"
            f"👤 Ism: {name}\n"
            f"📞 Telefon: {phone}\n"
            f"👤 Telegram: @{username if username else 'yo‘q'}"
        )

        for admin in admins:
            try:
                await context.bot.send_message(
                    chat_id=admin[0],
                    text=admin_text
                )
            except Exception:
                pass

        context.user_data.clear()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "❌ Qabulga yozilish bekor qilindi.",
        reply_markup=main_keyboard()
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ("administrator", "creator"):
        await update.message.reply_text(
            "❌ Bu buyruq faqat guruh administratorlari uchun."
        )
        return

    conn = db()

    conn.execute(
        "INSERT OR IGNORE INTO admins (user_id) VALUES (?)",
        (update.effective_user.id,)
    )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        "✅ Siz admin sifatida ro‘yxatdan o‘tdingiz.\n\n"
        "Endi shaxsiy chatda /admin buyrug‘ini yuboring."
    )


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = db()

    admin_exists = conn.execute(
        "SELECT user_id FROM admins WHERE user_id=?",
        (update.effective_user.id,)
    ).fetchone()

    conn.close()

    if not admin_exists:
        await update.message.reply_text(
            "❌ Siz admin sifatida ro‘yxatdan o‘tmagansiz."
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Qabullar", callback_data="admin:bookings")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin:stats")],
    ])

    await update.message.reply_text(
        "👑 ADMIN PANEL",
        reply_markup=keyboard
    )


async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = db()

    admin_exists = conn.execute(
        "SELECT user_id FROM admins WHERE user_id=?",
        (query.from_user.id,)
    ).fetchone()

    if not admin_exists:
        conn.close()
        return

    if query.data == "admin:bookings":
        rows = conn.execute(
            """
            SELECT id, service, date, time, name, phone
            FROM bookings
            ORDER BY id DESC
            LIMIT 20
            """
        ).fetchall()

        conn.close()

        if not rows:
            await query.message.reply_text(
                "📅 Hozircha qabullar yo‘q."
            )
            return

        text = "📅 SO‘NGGI QABULLAR\n\n"

        for row in rows:
            text += (
                f"#{row[0]}\n"
                f"🌷 {row[1]}\n"
                f"📅 {row[2]}  🕐 {row[3]}\n"
                f"👤 {row[4]}\n"
                f"📞 {row[5]}\n\n"
            )

        await query.message.reply_text(text)
        return

    if query.data == "admin:stats":
        total = conn.execute(
            "SELECT COUNT(*) FROM bookings"
        ).fetchone()[0]

        today = datetime.now(TZ).strftime("%d.%m.%Y")

        today_count = conn.execute(
            "SELECT COUNT(*) FROM bookings WHERE date=?",
            (today,)
        ).fetchone()[0]

        conn.close()

        await query.message.reply_text(
            "📊 STATISTIKA\n\n"
            f"📅 Jami qabullar: {total}\n"
            f"🕐 Bugungi qabullar: {today_count}"
        )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 GURUH QOIDALARI\n\n"
        "1️⃣ Reklama va spam taqiqlanadi.\n"
        "2️⃣ Shubhali havolalar yubormang.\n"
        "3️⃣ Hurmat bilan muloqot qiling.\n"
        "4️⃣ Takroriy spam uchun foydalanuvchi vaqtincha cheklanadi."
    )


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    for member in update.message.new_chat_members:
        try:
            await update.message.reply_text(
                f"🌷 Xush kelibsiz, {member.full_name}!\n\n"
                "Shafran Hijoma guruhiga xush kelibsiz."
            )

            try:
                await update.message.delete()
            except Exception:
                pass

        except Exception:
            pass


async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except Exception:
        pass


async def spam_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    spam_words = [
        "reklama",
        "reklamа",
        "casino",
        "stavka",
        "bet",
        "forex",
        "telegram.me",
        "t.me/",
    ]

    has_link = (
        "http://" in text
        or "https://" in text
        or "www." in text
        or "t.me/" in text
    )

    has_spam_word = any(word in text for word in spam_words)

    if not has_link and not has_spam_word:
        return

    user_id = update.effective_user.id

    warnings = context.application.bot_data.setdefault(
        "warnings",
        {}
    )

    count = warnings.get(user_id, 0) + 1
    warnings[user_id] = count

    try:
        await update.message.delete()
    except Exception:
        pass

    if count == 1:
        try:
            await update.effective_chat.send_message(
                f"⚠️ {update.effective_user.full_name}, "
                "reklama/spam yuborish mumkin emas.\n"
                "Bu birinchi ogohlantirish."
            )
        except Exception:
            pass

    else:
        try:
            until = datetime.now(TZ) + timedelta(hours=1)

            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                permissions={
                    "can_send_messages": False
                },
                until_date=until
            )

            await update.effective_chat.send_message(
                f"🔇 {update.effective_user.full_name} "
                "1 soatga cheklab qo‘yildi."
            )
        except Exception:
            pass


async def reminder_loop(application):
    while True:
        try:
            now = datetime.now(TZ)

            conn = db()

            rows = conn.execute(
                """
                SELECT id, user_id, service, date, time
                FROM bookings
                WHERE reminded=0
                """
            ).fetchall()

            for row in rows:
                booking_id, user_id, service, date, time = row

                try:
                    dt = datetime.strptime(
                        f"{date} {time}",
                        "%d.%m.%Y %H:%M"
                    ).replace(tzinfo=TZ)
                except Exception:
                    continue

                difference = dt - now

                if timedelta(minutes=0) <= difference <= timedelta(hours=2):
                    try:
                        await application.bot.send_message(
                            chat_id=user_id,
                            text=(
                                "🔔 ESLATMA\n\n"
                                f"🌷 Sizning qabul vaqtingiz yaqin.\n"
                                f"Xizmat: {service}\n"
                                f"📅 {date}\n"
                                f"🕐 {time}\n\n"
                                "Shafran Hijoma sizni kutadi 🌷"
                            )
                        )

                        conn.execute(
                            "UPDATE bookings SET reminded=1 WHERE id=?",
                            (booking_id,)
                        )

                        conn.commit()

                    except Exception:
                        pass

            conn.close()

        except Exception:
            pass

        await asyncio.sleep(60)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Shafran Hijoma Bot is running!")

    def log_message(self, format, *args):
        return


def start_web_server():
    port = int(os.environ.get("PORT", "10000"))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    server.serve_forever()


async def post_init(application):
    asyncio.create_task(reminder_loop(application))


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi!")

    db()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(
        MessageHandler(
            filters.Regex("^📅 Qabulga yozilish$"),
            lambda update, context: booking_start_message(update, context)
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^💰 Xizmatlar va narxlar$"),
            services
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^🩸 Hijoma muolajalari$"),
            hijoma_category
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^💆 Massaj muolajalari$"),
            massaj_category
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^🪱 Zuluk muolajalari$"),
            zuluk_category
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^ℹ️ Hijoma haqida$"),
            hijoma_about
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📍 Manzil$"),
            address
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📞 Operator bilan bog‘lanish$"),
            operator
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📢 Kanalimiz$"),
            channel
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            admin_callbacks,
            pattern="^admin:"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callbacks
        )
    )

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome_new_member
        )
    )

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.LEFT_CHAT_MEMBER,
            left_member
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            spam_or_booking_handler
        )
    )

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


async def booking_start_message(update, context):
    context.user_data.clear()

    await update.message.reply_text(
        "📅 QABULGA YOZILISH\n\n"
        "Muolaja turini tanlang:",
        reply_markup=category_keyboard()
    )


async def spam_or_booking_handler(update, context):
    if context.user_data.get("step"):
        await booking_text(update, context)
    else:
        await spam_moderation(update, context)


if __name__ == "__main__":
    Thread(
        target=start_web_server,
        daemon=True
    ).start()

    asyncio.run(main())
