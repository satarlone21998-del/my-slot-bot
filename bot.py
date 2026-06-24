import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8500678472:AAGGLKJiJivVisv4mNf1YD7p6YdXgzhSQTSok"
GAME_LINK = "https://satarlone.may9.vip/register.html"
GUIDE_LINK = "https://t.me/may9office"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome_text = (
        f"👋 မင်္ဂလာပါ {user.first_name} ခင်ဗျာ။\n\n"
        "🎰 ကျွန်တော်တို့ရဲ့ ယုံကြည်စိတ်ချရတဲ့ အွန်လိုင်းဂိမ်းပလတ်ဖောင်းမှ ကြိုဆိုပါတယ်။\n"
        "🔥 အခမဲ့အကောင့်ဖွင့်ပြီး ကစားနိုင်သလို၊ အထူးပရိုမိုးရှင်းတွေလည်း ရှိပါတယ်။\n\n"
        "👇 အောက်က ခလုတ်တွေကို နှိပ်ပြီး အခုပဲ စတင်လိုက်ပါ!"
    )
    keyboard = [
        [InlineKeyboardButton("🎰 အခုပဲ ဂိမ်းဆော့ရန်", url=GAME_LINK)],
        [
            InlineKeyboardButton("📑 အကောင့်ဖွင့်နည်း", url=GUIDE_LINK),
            InlineKeyboardButton("🎁 ပရိုမိုးရှင်းများ", url=GUIDE_LINK)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=welcome_text, reply_markup=reply_markup)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def main() -> None:
    threading.Thread(target=run_health_check, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Bot စတင်ပွင့်နေပါပြီ...")
    application.run_polling()

if __name__ == "__main__":
    main()
