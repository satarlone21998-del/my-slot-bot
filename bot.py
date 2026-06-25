import logging
import os
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = "8512151793:AAGPySDE5ad2Ye1mG7dSu02hDpqV_qlddfo"
ADMIN_ID = 8660958097
GAME_LINK = "https://satarlone.may9.vip/register.html"
GUIDE_LINK = "https://t.me/may9office"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- DATABASE SETUP ---
DB_FILE = "bot_users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # လူသစ်ဖြစ်မှ ထည့်ရန်၊ ရှိပြီးသားဆိုလျှင် ကျော်ရန်
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (user_id, username, first_name, joined_date) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, current_date)
        )
        conn.commit()
        conn.close()
        return True # လူသစ်ဖြစ်ကြောင်း အကြောင်းပြန်ခြင်း
    conn.close()
    return False

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_users_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(user_id) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Database ကို စတင်ဆောက်လုပ်ခြင်း
init_db()

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # လူသစ် ဟုတ်/မဟုတ် စစ်ပြီး Database ထဲထည့်ခြင်း
    is_new = add_user(chat_id, user.username, user.first_name)
    
    # လူသစ်အစစ်အမှန် ဝင်လာမှသာ ပိုင်ရှင် (အစ်ကို့ဆီ) သို့ စာလှမ်းပို့ခြင်း
    if is_new and chat_id != ADMIN_ID:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notify_text = (
            f"🔔 **လူသစ်တစ်ယောက် Bot ကို Start လုပ်လိုက်ပါတယ်!**\n\n"
            f"👤 အမည်: {user.first_name}\n"
            f"🆔 User ID: `{chat_id}`\n"
            f"🔗 Username: @{user.username if user.username else 'မရှိပါ'}\n"
            f"📅 ရက်စွဲ: {current_date}"
        )
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

# အစ်ကိုတစ်ယောက်တည်း သုံးသူစာရင်းကြည့်ရန် Command (/users)
async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id == ADMIN_ID:
        total = get_users_count()
        await update.message.reply_text(f"📊 **လက်ရှိ Database ထဲရှိ သုံးနေသူ စုစုပေါင်း:** {total} ယောက်")
    else:
        await update.message.reply_text("❌ သင်သည် ပိုင်ရှင် (Admin) မဟုတ်ပါ။")

# အစ်ကိုတစ်ယောက်တည်း လူအားလုံးဆီ စာလှမ်းပို့ရန် Command (/send စာသား)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် ပိုင်ရှင် (Admin) မဟုတ်ပါ။")
        return
        
    if not context.args:
        await update.message.reply_text("❌ စာသားထည့်ရန် လိုအပ်ပါသည်။\nℹ️ အသုံးပြုပုံ - `/send ပရိုမိုးရှင်းအသစ် ရပါပြီ`")
        return
        
    broadcast_message = " ".join(context.args)
    all_users = get_all_users()
    success_count = 0
    
    for user_id in all_users:
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
