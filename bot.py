import os
import asyncio
import re
from datetime import datetime, timedelta

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
    ChatMemberHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

# Admin ID ni keyin Render orqali qo‘shishimiz mumkin.
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

PHONE = "+998 94 504 09 18"
ADDRESS = "Toshkent shahri, Shayxontohur tumani, General Uzoqov 32-uy"
WORKING_HOURS = "Har kuni 09:00–17:00"

MAP_URL = "https://www.google.com/maps/search/?api=1&query=General+Uzoqov+32+Toshkent"


# =========================
# ASOSIY MENYU
# =========================

MAIN_KEYBOARD = [
    ["📅 Qabulga yozilish"],
    ["💰 Xizmatlar va narxlar"],
    ["🩸 Hijoma muolajalari"],
    ["💆 Massaj muolajalari"],
    ["🪱 Zuluk muolajalari"],
    ["📍 Manzil"],
    ["📞 Operator bilan bog‘lanish"],
]


# =========================
# XIZMATLAR
# =========================

HIJOMA = [
    ("🩸 Hijoma + zaytunli massaj", "300 000 so‘m"),
    ("✨ Yuz hijomasi + yengil chistkasi bilan", "450 000 so‘m"),
    ("⚡ Chertma hijoma", "150 000 so‘m"),
    ("👄 Lab uchun hijoma", "100 000 so‘m"),
    ("🦵 Oyoqdagi shishlar va og‘riqlar uchun hijoma", "200 000 so‘m"),
    ("🧠 Boshda hijoma", "200 000 so‘m"),
    ("🌿 Detoks hijoma", "300 000 so‘m"),
]

MASSAJ = [
    ("💆 Bitta sohaga massaj", "100 000 so‘m"),
    ("💆 Obshiy massaj", "400 000 so‘m"),
    ("💃 Koreksiya figura massaj", "300 000 so‘m"),
    ("😌 Relax massaj", "300 000 so‘m"),
    ("🌸 Bo‘yin massaji", "90 000 so‘m"),
    ("🦶 Oyoq sohasiga massaj", "90 000 so‘m"),
    ("👶 Bolalar massaji", "60 000–130 000 so‘m"),
    ("🍯 Asalli massaj", "150 000 so‘m"),
]

ZULUK = [
    ("🪱 Zuluk donasi", "50 000 so‘mdan"),
    ("🌸 Vaginalniy zuluk", "400 000 so‘m"),
    ("🇹🇷 Zuluklar", "Turkiyaniki"),
]


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! 🌷\n\n"
        "Shafran Hijoma markaziga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD,
            resize_keyboard=True
        )
    )


# =========================
# XIZMATLAR RO‘YXATI
# =========================

def service_text(title, services):
    text = f"{title}\n\n"

    for i, (name, price) in enumerate(services, 1):
        text += f"{i}. {name}\n💰 {price}\n\n"

    text += "📅 Qabulga yozilish uchun quyidagi tugmani bosing."

    return text


def booking_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📅 Qabulga yozilish",
            callback_data="booking"
        )]
    ])


async def show_hijoma(update: Update):
    await update.message.reply_text(
        service_text("🩸 HIJOMA MUOLAJALARI", HIJOMA),
        reply_markup=booking_button()
    )


async def show_massaj(update: Update):
    await update.message.reply_text(
        service_text("💆 MASSAJ MUOLAJALARI", MASSAJ),
        reply_markup=booking_button()
    )


async def show_zuluk(update: Update):
    await update.message.reply_text(
        service_text("🪱 ZULUK MUOLAJALARI", ZULUK),
        reply_markup=booking_button()
    )


async def show_prices(update: Update):
    text = (
        "💰 XIZMATLAR VA NARXLAR\n\n"
        "🩸 HIJOMA\n"
        "Hijoma + zaytunli massaj — 300 000 so‘m\n"
        "Yuz hijomasi + yengil chistkasi — 450 000 so‘m\n"
        "Chertma hijoma — 150 000 so‘m\n"
        "Lab uchun hijoma — 100 000 so‘m\n"
        "Oyoqdagi shishlar va og‘riqlar uchun — 200 000 so‘m\n"
        "Boshda hijoma — 200 000 so‘m\n"
        "Detoks hijoma — 300 000 so‘m\n\n"
        
        "💆 MASSAJ\n"
        "Bitta sohaga — 100 000 so‘m\n"
        "Obshiy — 400 000 so‘m\n"
        "Koreksiya figura — 300 000 so‘m\n"
        "Relax — 300 000 so‘m\n"
        "Bo‘yin — 90 000 so‘m\n"
        "Oyoq sohasi — 90 000 so‘m\n"
        "Bolalar massaji — 60 000–130 000 so‘m\n"
        "Asalli massaj — 150 000 so‘m\n\n"

        "🪱 ZULUK\n"
        "Zuluk donasi — 50 000 so‘mdan\n"
        "Vaginalniy zuluk — 400 000 so‘m\n"
        "Zuluklar — Turkiyaniki 🇹🇷"
    )

    await update.message.reply_text(
        text,
        reply_markup=booking_button()
    )


# =========================
# MANZIL
# =========================

async def show_address(update: Update):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺️ Xaritada ochish", url=MAP_URL)]
    ])

    await update.message.reply_text(
        "📍 MANZIL\n\n"
        f"{ADDRESS}\n\n"
        f"🕐 {WORKING_HOURS}\n"
        f"📞 {PHONE}",
        reply_markup=keyboard
    )


# =========================
# OPERATOR
# =========================

async def show_operator(update: Update):
    await update.message.reply_text(
        "📞 OPERATOR BILAN BOG‘LANISH\n\n"
        f"Telefon: {PHONE}\n"
        f"🕐 {WORKING_HOURS}\n\n"
        "Qabul va xizmatlar bo‘yicha operator bilan bog‘lanishingiz mumkin."
    )


# =========================
# HIJOMA HAQIDA
# =========================

async def show_info(update: Update):
    await update.message.reply_text(
        "ℹ️ MUOLAJALAR HAQIDA\n\n"
        "🩸 Hijoma — an’anaviy muolaja usullaridan biri.\n\n"
        "💆 Massaj — turli sohalarga mo‘ljallangan massaj xizmatlari.\n\n"
        "🪱 Zuluk muolajalarida maxsus zuluklardan foydalaniladi.\n\n"
        "Har bir muolajaning mosligi individual holatga bog‘liq. "
        "Sog‘liq bilan bog‘liq muammolar bo‘lsa, muolajadan oldin "
        "mutaxassis yoki shifokor bilan maslahatlashish tavsiya etiladi.\n\n"
        f"📞 {PHONE}"
    )


# =========================
# QABULGA YOZILISH
# =========================

async def booking_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["booking_step"] = "name"

    await update.message.reply_text(
        "📅 QABULGA YOZILISH\n\n"
        "Avval ismingizni yozing 👇"
    )


async def booking_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["booking_step"] = "name"

    await query.message.reply_text(
        "📅 QABULGA YOZILISH\n\n"
        "Avval ismingizni yozing 👇"
    )


# =========================
# ADMIN XABARI
# =========================

async def send_booking_to_admin(context, user, name):
    if not ADMIN_ID:
        return

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📅 YANGI QABUL SO‘ROVI\n\n"
            f"👤 Ism: {name}\n"
            f"🆔 Telegram ID: {user.id}\n"
            f"📱 Username: @{user.username if user.username else 'yo‘q'}\n\n"
            f"🕐 So‘rov vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
    )


# =========================
# UMUMIY MESSAGE HANDLER
# =========================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text = update.message.text

    # Qabul jarayoni
    if context.user_data.get("booking_step") == "name":
        context.user_data["booking_name"] = text
        context.user_data["booking_step"] = "phone"

        await update.message.reply_text(
            "📱 Telefon raqamingizni yozing.\n\n"
            "Masalan: +998 90 123 45 67"
        )
        return

    if context.user_data.get("booking_step") == "phone":
        context.user_data["booking_phone"] = text
        context.user_data["booking_step"] = None

        name = context.user_data.get("booking_name")

        await send_booking_to_admin(
            context,
            update.effective_user,
            name
        )

        await update.message.reply_text(
            "✅ So‘rovingiz qabul qilindi!\n\n"
            f"👤 Ism: {name}\n"
            f"📱 Telefon: {text}\n\n"
            "Operator siz bilan bog‘lanadi."
        )
        return

    # Menyu
    if text == "📅 Qabulga yozilish":
        await booking_start(update, context)

    elif text == "💰 Xizmatlar va narxlar":
        await show_prices(update)

    elif text == "🩸 Hijoma muolajalari":
        await show_hijoma(update)

    elif text == "💆 Massaj muolajalari":
        await show_massaj(update)

    elif text == "🪱 Zuluk muolajalari":
        await show_zuluk(update)

    elif text == "📍 Manzil":
        await show_address(update)

    elif text == "📞 Operator bilan bog‘lanish":
        await show_operator(update)

    else:
        await update.message.reply_text(
            "Kerakli bo‘limni menyudan tanlang 👇",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_KEYBOARD,
                resize_keyboard=True
            )
        )


# =========================
# GURUH MODERATORI
# =========================

async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    message = update.message
    text = message.text or ""

    # Reklama/spamga o‘xshash so‘zlar
    spam_words = [
        "reklama",
        "aksiya",
        "sotaman",
        "sotiladi",
        "telegram kanal",
        "obuna bo‘ling",
        "daromad",
        "pul ishlang",
        "investitsiya",
        "casino",
        "stavka",
        "kripto",
    ]

    lower_text = text.lower()

    if any(word in lower_text for word in spam_words):
        try:
            await message.delete()

            await context.bot.send_message(
                chat_id=message.chat_id,
                text=(
                    f"⚠️ {message.from_user.first_name}, "
                    "reklama va spam xabarlar guruhda taqiqlangan."
                )
            )

        except Exception:
            pass


# =========================
# YANGI A’ZO
# =========================

async def member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.chat_member:
        return

    old = update.chat_member.old_chat_member.status
    new = update.chat_member.new_chat_member.status

    # Yangi kirgan
    if new in ("member", "restricted") and old in ("left", "kicked"):
        user = update.chat_member.new_chat_member.user

        try:
            await context.bot.send_message(
                chat_id=update.chat_member.chat.id,
                text=(
                    f"🌷 Xush kelibsiz, {user.first_name}!\n\n"
                    "Shafran Hijoma guruhiga xush kelibsiz."
                )
            )
        except Exception:
            pass


# =========================
# RULES
# =========================

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📜 GURUH QOIDALARI\n\n"
        "1️⃣ Reklama va spam taqiqlanadi.\n"
        "2️⃣ Haqorat va janjalga yo‘l qo‘yilmaydi.\n"
        "3️⃣ Begona havolalarni tarqatmang.\n"
        "4️⃣ Guruh mavzusiga aloqador xabar yozing.\n"
        "5️⃣ Takroriy qoidabuzarlikda cheklov qo‘llanishi mumkin.\n\n"
        "🌷 Guruhimizda hurmat va tartibni saqlaymiz."
    )


# =========================
# ADMIN
# =========================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if ADMIN_ID and update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Bu bo‘lim faqat admin uchun.")
        return

    await update.message.reply_text(
        "👑 ADMIN PANEL\n\n"
        "📅 Qabul so‘rovlari bot orqali keladi.\n"
        "📊 Statistika va qo‘shimcha boshqaruv funksiyalari keyingi bosqichda kengaytiriladi."
    )


# =========================
# PORT SERVER
# =========================

from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Shafran bot ishlayapti!")

    def log_message(self, format, *args):
        pass


def keep_alive():

    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    server.serve_forever()


# =========================
# MAIN
# =========================

async def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(
        CallbackQueryHandler(
            booking_callback,
            pattern="^booking$"
        )
    )

    app.add_handler(
        ChatMemberHandler(
            member_update,
            ChatMemberHandler.CHAT_MEMBER
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.TEXT,
            group_message_handler
        )
    )

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":

    Thread(
        target=keep_alive,
        daemon=True
    ).start()

    asyncio.run(main())
