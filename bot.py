import os
import sqlite3
import logging
import asyncio
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

TOKEN = os.getenv("BOT_TOKEN")  # التوكن يتم قراءته من متغيرات البيئة في Railway

# ضع جميع الأدمن هنا (لن يتم حذفهم)
ADMIN_IDS = [1000660019, 1816045034]  # أدمن 1 وأدمن 2

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في Railway Variables")

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
# أوامر البوت
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    await update.message.reply_text("مرحباً بك 🔥 اختر أحد الأقسام:", reply_markup=generate_keyboard(0))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ هذا الأمر خاص بالأدمن فقط")
        return
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    await update.message.reply_text(f"👥 عدد المستخدمين: {users}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.edit_message_reply_markup(reply_markup=generate_keyboard(page))
        return

    await query.edit_message_text("تم الضغط على الزر ✅")

# =========================
# التشغيل الاحترافي بدون Loop Error
# =========================

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # إضافة كل الهاندلرز
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 البوت يعمل الآن بدون Loop Error")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()
    await app.stop()
    await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("⚠ خطأ أثناء التشغيل:", e)