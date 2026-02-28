import os
import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# الإعدادات
# =========================
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في Railway Variables")

ADMIN_IDS = [1000660019, 1816045034]  # الأدمنين (لا نحذفهم)

logging.basicConfig(level=logging.INFO)

# =========================
# قاعدة البيانات
# =========================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS buttons (
    button_id TEXT PRIMARY KEY,
    type TEXT,
    file_id TEXT,
    text TEXT,
    caption TEXT,
    clicks INTEGER DEFAULT 0
)
""")

conn.commit()

# =========================
# الأقسام الـ50
# =========================
BUTTONS_PER_PAGE = 10
TOTAL_BUTTONS = 50

BUTTON_NAMES = {
    1: "طريقة التقديم على الكليات التقنية لعام 1446 (جديد)",
    2: "شرح للمستجدين (المقبولين) بالكليات التقنية",
    3: "مواعيد تسجيل المواد للترم الأول من عام 1447 بالكليات التقنية",
    4: "الفرق بين المعدل الفصلي و التراكمي بالكليات التقنية",
    5: "شرح للبرامج المساندة بالكليات التقنية",
    6: "طريقة الاطلاع على خطط التخصصات بالكليات التقنية",
    7: "تفاصيل ومعلومات حول برنامج اللغة الانجليزية",
    8: "ماذا بعد القبول النهائي بالكليات التقنية",
    9: "كيف تعرف معنى حالة تقديمك بالكليات التقنية",
    10: "شرح جدول المستجدين بالكليات التقنية",
    11: "طريقة معادلة المقررات بالكليات التقنية",
    12: "تصنيف التخصصات التعليمية",
    13: "ماهو الاعتماد المهني لخريجي الكليات التقنية",
    14: "هل تم إيقاف البكالوريوس التقني وهل سيعود؟",
    15: "مواقف تواجه المستجدين بالكليات التقنية",
    16: "وضع المستجدين في الكليات التقنية",
    17: "ماهي الكليات التقنية ومميزاتها",
    18: "الفرق بين الكليات التقنية سابقًا ومستقبلًا",
    19: "شرح موزونة القبول بدبلوم الكليات التقنية",
    20: "تكملة بكالوريوس أو ماجستير وحل مشكلة الرسوم",
    21: "الحالات المعفية من الرسوم المسائي",
    22: "طريقة اضافة الايبان عن طريق رايات",
    23: "المكافأة الشهرية",
    24: "توزيع الأسابيع التدريبية",
    25: "شروط الدبلوم المسائي",
    26: "الفرق بين التدريب التعاوني والمشروع الإنتاجي",
    27: "طلب النقل لكلية أخرى",
    28: "المكافآت والمساعدة المالية",
    29: "طلب التأجيل لمدة ترم",
    30: "الإنذارات والفصل",
    31: "شرح الجدول عبر رايات",
    32: "الفرق بين السلفة والإعانة",
    33: "الزي الموحد",
    34: "متابعة المسير المالي",
    35: "شروط برنامج الانجليزي المكثف",
    36: "التقويم التدريبي",
    37: "معاني الكلمات في الطلبات الالكترونية",
    38: "معدل التخرج ومراتب الشرف",
    39: "الفرق بين التأجيل والانسحاب وطي القيد",
    40: "شروط مكافأة التفوق",
    41: "طريقة حساب الرسوم",
    42: "شروط القبول مسائي",
    43: "التدريب التعاوني في ارامكو",
    44: "اللغة الانجليزية عن بعد",
    45: "طلب تغيير التخصص",
    46: "طلب النقل لكلية أخرى",
    47: "حالات انقطاع المكافأة",
    48: "المكافآت والمساعدة المالية",
    49: "ملخص مبادرة رافد",
    50: "معادلة المقررات",
}

# =========================
# توليد لوحة الأزرار
# =========================
def generate_keyboard(page=0):
    keyboard = []
    start = page * BUTTONS_PER_PAGE + 1
    end = min(start + BUTTONS_PER_PAGE, TOTAL_BUTTONS + 1)

    for i in range(start, end):
        keyboard.append([InlineKeyboardButton(BUTTON_NAMES.get(i, f"زر {i}"), callback_data=f"btn{i}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅ السابق", callback_data=f"page_{page-1}"))
    if end <= TOTAL_BUTTONS:
        nav.append(InlineKeyboardButton("التالي ➡", callback_data=f"page_{page+1}"))

    if nav:
        keyboard.append(nav)

    return InlineKeyboardMarkup(keyboard)

# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    await update.message.reply_text(
        "مرحباً بك 🔥  في بوتنا للأسالة الشائعة عن الكلية التقنية :",
        reply_markup=generate_keyboard(0)
    )

# =========================
# /admin
# =========================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ هذا الأمر خاص بالأدمن فقط")
        return
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(clicks) FROM buttons")
    total_clicks = cursor.fetchone()[0] or 0
    await update.message.reply_text(
        f"📊 إحصائيات البوت:\n\n"
        f"👥 عدد المستخدمين: {users}\n"
        f"🔥 مجموع الضغطات: {total_clicks}"
    )

# =========================
# /edit
# =========================
async def edit_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ هذا الأمر خاص بالأدمن فقط")
        return
    if not context.args:
        await update.message.reply_text("اكتب رقم الزر بعد الأمر مثال:\n/edit 5")
        return
    button_id = f"btn{context.args[0]}"
    context.user_data["editing"] = button_id
    await update.message.reply_text("أرسل الآن النص أو الصورة أو الفيديو لهذا الزر.")

# =========================
# /delete
# =========================
async def delete_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ هذا الأمر خاص بالأدمن فقط")
        return
    if not context.args:
        await update.message.reply_text("اكتب رقم الزر بعد الأمر مثال:\n/delete 5")
        return
    button_id = f"btn{context.args[0]}"
    cursor.execute("DELETE FROM buttons WHERE button_id=?", (button_id,))
    conn.commit()
    await update.message.reply_text("🗑 تم حذف محتوى الزر بنجاح")

# =========================
# استقبال محتوى الأدمن
# =========================
async def receive_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "editing" not in context.user_data:
        return
    button_id = context.user_data["editing"]

    if update.message.text:
        cursor.execute("""
        INSERT OR REPLACE INTO buttons (button_id, type, text, clicks)
        VALUES (?, 'text', ?, 0)
        """, (button_id, update.message.text))
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        cursor.execute("""
        INSERT OR REPLACE INTO buttons (button_id, type, file_id, caption, clicks)
        VALUES (?, 'photo', ?, ?, 0)
        """, (button_id, file_id, update.message.caption))
    elif update.message.video:
        file_id = update.message.video.file_id
        cursor.execute("""
        INSERT OR REPLACE INTO buttons (button_id, type, file_id, caption, clicks)
        VALUES (?, 'video', ?, ?, 0)
        """, (button_id, file_id, update.message.caption))

    conn.commit()
    context.user_data.pop("editing")
    await update.message.reply_text("✅ تم حفظ المحتوى بنجاح")

# =========================
# التعامل مع الأزرار
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.edit_message_reply_markup(reply_markup=generate_keyboard(page))
        return

    cursor.execute("SELECT * FROM buttons WHERE button_id=?", (data,))
    button = cursor.fetchone()

    if button:
        cursor.execute("UPDATE buttons SET clicks = clicks + 1 WHERE button_id=?", (data,))
        conn.commit()
        _, type_, file_id, text, caption, _ = button
        if type_ == "text":
            await query.message.reply_text(text)
        elif type_ == "photo":
            await query.message.reply_photo(file_id, caption=caption)
        elif type_ == "video":
            await query.message.reply_video(file_id, caption=caption)
    else:
        await query.message.reply_text("⚠ لا يوجد محتوى لهذا الزر بعد")

# =========================
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # إضافة الـ handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("edit", edit_button))
    app.add_handler(CommandHandler("delete", delete_button))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, receive_content))

    print("🚀 Bot Started Successfully")

    # ✅ الحل النهائي: تشغيل Polling لتجنب مشاكل Webhook على Railway
    app.run_polling()

if __name__ == "__main__":
    main()