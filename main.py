import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types

# Tokenni Render Environment Variables (Muhit o'zgaruvchilari)dan olamiz
# Agar u yerda bo'lmasa, zaxira token ishlatiladi
TOKEN = os.environ.get("BOT_TOKEN", "9273189771:AAGeG54QLlRWBcyhUb2Ple2YhEAtVLGUsDM")
bot = telebot.TeleBot(TOKEN)

# Menyu va narxlar (so'mda)
menu = {
    "Капучино ☕": 25000,
    "Латте ☕": 28000,
    "Американо ☕": 20000,
    "Чай 🍵": 15000,
    "Круассан 🥐": 20000
}


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        types.KeyboardButton("📋 Меню"),
        types.KeyboardButton("🛒 Заказать")
    )
    keyboard.add(types.KeyboardButton("ℹ️ О кофейне"))

    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Добро пожаловать в нашу кофейню ☕\n\n"
        "Выбеri действие ниже:",
        reply_markup=keyboard
    )


@bot.message_handler(commands=["menu"])
@bot.message_handler(func=lambda message: message.text == "📋 Меню")
def show_menu(message):
    text = "📋 НАШЕ МЕНЮ:\n\n"
    for name, price in menu.items():
        text += f"• {name} — {price:,} сум\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.text == "🛒 Заказать")
def order(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for name, price in menu.items():
        button = types.InlineKeyboardButton(
            text=f"{name} — {price:,} сум",
            callback_data=name
        )
        keyboard.add(button)

    bot.send_message(
        message.chat.id,
        "☕ Выбери напиток или еду:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def choose_product(call):
    product = call.data

    if product in menu:
        price = menu[product]
        bot.answer_callback_query(call.id, text=f"Вы выбрали {product}")

        bot.send_message(
            call.message.chat.id,
            f"✅ Заказ принят!\n\n"
            f"🍴 Товар: {product}\n"
            f"💰 Цена: {price:,} сум\n\n"
            f"Спасибо за заказ! Скоро всё будет готово ☕"
        )
    else:
        bot.answer_callback_query(call.id, text="Товар не найден", show_alert=True)


@bot.message_handler(func=lambda message: message.text == "ℹ️ О кофейне")
def about(message):
    bot.send_message(
        message.chat.id,
        "☕ НАША КОФЕЙНЯ\n\n"
        "📍 Адрес: Ташкент, Узбекистан\n"
        "🕐 Работаем: 08:00–22:00 (без выходных)\n"
        "📞 Номер телефона: +998 90 123 45 67\n"
        "💬 Приятного аппетита и хорошего дня!"
    )


# -------------------------------------------------------------
# RENDER SERVER UCHUN HEALTH CHECK (Veb-server qismi)
# Render bepul Web Service bo'lishi uchun PORT'ni tinglash shart.
# -------------------------------------------------------------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running 24/7 on Render!")

    def log_message(self, format, *args):
        # Render konsolini ortiqcha loglar bilan to'ldirmaslik uchun
        return


def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Health-check server running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # Render uchun alohida oqimda (thread) veb-serverni ishga tushiramiz
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()

    print("Bot muvaffaqiyatli ishga tushdi! Render polling boshlandi...")
    bot.infinity_polling(skip_pending=True)
