import os
import sqlite3
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
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

ADMIN_IDS = [1000660019, 1816045034]

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
# الإعدادات العامة
# =========================
BUTTONS_PER_SECTION = 10
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
# القوائم
# =========================
def main_menu():
    keyboard = [
        ["📚 القسم 1", "📚 القسم 2"],
        ["📚 القسم 3", "📚 القسم 4"],
        ["📚 القسم 5"],
        ["❌ إخفاء الكيبورد"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def section_keyboard(section_number):
    keyboard = []
    start = (section_number - 1) * BUTTONS_PER_SECTION + 1
    end = start + BUTTONS_PER_SECTION

    row = []
    for i in range(start, end):
        row.append(BUTTON_NAMES[i])
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append(["🔙 رجوع", "🏠 الرئيسية"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

    await update.message.reply_text(
        "مرحباً بك 🔥 في بوت الأسئلة الشائعة:",
        reply_markup=main_menu()
    )

# =========================
# لوحة الأدمن
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

    context.user_data["editing"] = f"btn{context.args[0]}"
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
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "❌ إخفاء الكيبورد":
        await update.message.reply_text("تم الإخفاء", reply_markup=ReplyKeyboardRemove())
        return

    if text == "🏠 الرئيسية":
        await update.message.reply_text("🏠 القائمة الرئيسية:", reply_markup=main_menu())
        return

    if text == "🔙 رجوع":
        await update.message.reply_text("📚 الأقسام:", reply_markup=main_menu())
        return

    if text.startswith("📚 القسم"):
        try:
            section_number = int(text.split()[-1])
            await update.message.reply_text(
                f"📂 القسم {section_number}",
                reply_markup=section_keyboard(section_number)
            )
        except ValueError:
            await update.message.reply_text("⚠ حدث خطأ في تحديد القسم")
        return

    # التعامل مع محتوى الزر
    button_number = None
    for key, value in BUTTON_NAMES.items():
        if value == text:
            button_number = key
            break

    if button_number is None:
        return

    button_id = f"btn{button_number}"

    cursor.execute("SELECT * FROM buttons WHERE button_id=?", (button_id,))
    button = cursor.fetchone()

    if button:
        cursor.execute("UPDATE buttons SET clicks = clicks + 1 WHERE button_id=?", (button_id,))
        conn.commit()

        _, type_, file_id, text_data, caption, _ = button

        if type_ == "text" and text_data:
            await update.message.reply_text(text_data)
        elif type_ == "photo" and file_id:
            await update.message.reply_photo(file_id, caption=caption)
        elif type_ == "video" and file_id:
            await update.message.reply_video(file_id, caption=caption)
        else:
            await update.message.reply_text("⚠ لا يوجد محتوى لهذا الزر بعد")
    else:
        await update.message.reply_text("⚠ لا يوجد محتوى لهذا الزر بعد")

# =========================
# تشغيل البوت
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("edit", edit_button))
    app.add_handler(CommandHandler("delete", delete_button))

    # ترتيب الهاندلرز مهم
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, receive_content))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("🚀 Bot Started Successfully")
    app.run_polling()

if __name__ == "__main__":
    main()