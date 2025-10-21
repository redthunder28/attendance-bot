import logging
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

# إعداد السجل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
DB = "attendance.db"

# توكن البوت (غيّره بالتوكن الخاص بك)
TOKEN = "8002555160:AAGQIvaczmNUygsZSr-0myXLohG2rhw7HKE"

# مجلد الصور
os.makedirs("photos", exist_ok=True)

# إضافة موظف
def add_employee(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        update.message.reply_text("❌ استخدم الأمر بهذا الشكل:\n/add_employee رقم_الموظف الاسم")
        return
    user_id = int(context.args[0])
    name = " ".join(context.args[1:])
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO employees (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()
    update.message.reply_text(f"✅ تم إضافة الموظف: {name}")

# تعيين قيمة الساعة
def set_hourly_rate(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        update.message.reply_text("❌ استخدم:\n/set_rate رقم_الموظف قيمة_الساعة")
        return
    user_id = int(context.args[0])
    rate = float(context.args[1])
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE employees SET hourly_rate=? WHERE user_id=?", (rate, user_id))
    conn.commit()
    conn.close()
    update.message.reply_text(f"✅ تم تحديث قيمة الساعة للموظف {user_id} إلى {rate} جنيه")

# تسجيل الحضور أو الانصراف بصورة
def photo_handler(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    name = user.full_name

    # تحميل الصورة
    photo_file = update.message.photo[-1].get_file()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    photo_path = f"photos/{user_id}_{timestamp}.jpg"
    photo_file.download(photo_path)

    # تحديد النوع (حضور أو انصراف)
    msg = update.message.caption or ""
    if "انصراف" in msg:
        record_type = "انصراف"
    else:
        record_type = "حضور"

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO attendance (user_id, name, type, timestamp, location, photo_path) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, name, record_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "الموقع الافتراضي", photo_path))
    conn.commit()
    conn.close()

    update.message.reply_text(f"📸 تم تسجيل {record_type} بنجاح للموظف {name}")

# عرض تقرير يومي
def report(update: Update, context: CallbackContext):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name, type, timestamp FROM attendance WHERE date(timestamp)=date('now') ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        update.message.reply_text("لا يوجد تسجيلات اليوم بعد.")
        return

    msg = "🗓️ تقرير اليوم:\n"
    for r in rows:
        msg += f"{r[0]} - {r[1]} - {r[2]}\n"
    update.message.reply_text(msg)

# بدء التشغيل
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("add_employee", add_employee))
    dp.add_handler(CommandHandler("set_rate", set_hourly_rate))
    dp.add_handler(CommandHandler("report", report))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
