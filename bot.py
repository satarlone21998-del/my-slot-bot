import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION (COMPLETELY FIXED) ---
BOT_TOKEN = "8500678472:AAGGLKJiJivVisv4wNf1YD7p6YdXgzhSQTSok"
ADMIN_ID = 8660958097
GAME_LINK = "https://satarlone.may9.vip/register.html"
GUIDE_LINK = "https://t.me/may9office"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

USER_LIST = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    USER_LIST.add(chat_id)
    
    if chat_id != ADMIN_ID:
        notify_text = f"🔔 **လူသစ်တစ်ယောက် Bot ကို Start လုပ်လိုက်ပါတယ်!**\n\n👤 အမည်: {user.first_name}\n🆔 User ID: `{chat_id}`\n🔗 Username: @{user.username if user.username else 'မရှိပါ'}"
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=notify_text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Notification error: {e}")

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

async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == ADMIN_ID:
        total = len(USER_LIST)
        await update.message.reply_text(f"📊 **လက်ရှိ Bot သုံးနေသူ စုစုပေါင်း:** {total} ယောက်")
    else:
        await update.message.reply_text("❌ သင်သည် ပိုင်ရှင် (Admin) မဟုတ်ပါ။")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် ပိုင်ရှင် (Admin) မဟုတ်ပါ။")
        return
        
    if not context.args:
        await update.message.reply_text("❌ စာသားထည့်ရန် လိုအပ်ပါသည်။\nℹ️ အသုံးပြုပုံ - `/send ပရိုမိုးရှင်းအသစ် ရပါပြီ`")
        return
        
    broadcast_message = " ".join(context.args)
    success_count = 0
    
    for user_id in list(USER_LIST):
        try:
            await context.bot.send_message(chat_id=user_id, text=broadcast_message)
            success_count += 1
        except Exception:
            continue
            
    await update.message.reply_text(f"🚀 လူပေါင်း {success_count} ယောက်ဆီ စာပို့ခြင်း အောင်မြင်ပါသည်။")

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
    application.add_handler(CommandHandler("users", view_users))
    application.add_handler(CommandHandler("send", broadcast))
    
    print("Bot စတင်ပွင့်နေပါပြီ...")
    application.run_polling()

if __name__ == "__main__":
    main()
