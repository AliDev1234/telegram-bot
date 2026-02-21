import os
import asyncio
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)



# ===== قراءة التوكن من السيرفر =====
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("❌ لم يتم تعيين TOKEN في Railway Variables")

# ===== ضع الادمن مباشرة هنا =====
ADMIN_IDS = [1000660019, 1816045034]


# ===== قاعدة البيانات =====
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

# ===== إعداد الأزرار والقاموس =====
BUTTONS_PER_PAGE = 10
TOTAL_BUTTONS = 50

# ⚡ لا تغير أي شيء هنا، جميع الأقسام محفوظة
BUTTON_NAMES = {
    1: "طريقة التقديم على الكليات التقنية لعام 1446 (جديد)", 
    2: "شرح للمستجدين (المقبولين) بالكليات التقنية", 
    3: "مواعيد تسجيل المواد للترم الأول من عام 1447 بالكليات التقنية", 
    4: "الفرق بين المعدل الفصلي و التراكمي بالكليات التقنية", 
    5: "شرح للبرامج المساندة بالكليات التقنية",
    6: "طريقة الاطلاع على خطط التخصصات بالكليات التقنية", 
    7: "تفاصيل ومعلومات حول برنامج اللغة الانجليزية لخريجي وخريجات الكليات التقنية", 
    8: "ماذا بعد القبول النهائي بالكليات التقنية", 
    9: "كيف تعرف معنى حالة تقديمك بالكليات التقنية", 
    10: "شرح جدول المستجدين بالكليات التقنيةا",
    11: "طريقة معادلة المقررات بالكليات التقنية للعام الحالي", 
    12: "تصنيف التخصصات التعليمية", 
    13: "ماهو الاعتماد المهني لخريجي الكليات التقنية💡", 
    14: "هل تم إيقاف البكالوريوس التقني وهل سيعود؟", 
    15: "مواقف تواجه المستجدين بالكليات التقنية",
    16: "وضع المستجدين في الكليات التقنية", 
    17: "ماهي الكليات التقنية و مميزاتها وتفاصيلها 🤯🤯", 
    18: "ما الفرق بين الكليات التقنية سابقًا ومستقبلًا 💡", 
    19: "شرح موزونة القبول بدبلوم الكليات التقنية", 
    20: "تبغى تكمل بكالوريوس او ماجستير ومشكلتك في الرسوم هنا الحل",
    21: "الحالات المعفيه من الرسوم المسائي", 
    22: "طريقة اضافة الايبان عن طريق موقع رايات", 
    23: "المكافأه الشهرية للكلية التقنية", 
    24: "توزيع الأسابيع التدريبية للفصل الاول لعام 1447", 
    25: "شروط الدبلوم المسائي للكيات التقنية",
    26: "الفرق بين التدريب التعاوني والمشروع الإنتاجي", 
    27: "طلب النقل لكلية اخرى", 
    28: "المكافأء والمساعدة المالية", 
    29: "طلب التأجيل لمدة ترم", 
    30: "الأنذارات والفصل",
    31: "شرح تفصيلي لتفاصيل الجدول عبر رايات", 
    32: "الفرق بين السلفة والاعانة",
    33: "الزي الموحد في الكليات التقنية", 
    34: "طريقة متابعة المسير المالي من رايات", 
    35: "شروط برنامج الانجليزي المكثف",
    36: "التقويم التدريبي لعام 1447", 
    37: "معاني الكلمات في حال الطلبات الالكترونية", 
    38: "معدل التخرج ومراتب الشرف", 
    39: "الفرق بين التاجيل والانسحاب وطي القيد", 
    40: "شروط مكافاة التفوق الفصلية",
    41: "طريقة حساب الرسوم المسائي",
    42: "شروط القبول بكليات التقية مسائي", 
    43: "كل مايخص التدريب التعاوني في ارامكو", 
    44: "شروط القبول ببرنامج اللغة الانجليزية عن بعد", 
    45: "طلب تغير التخصص",
    46: "طلب النقل لكلية اخرى",
    47: "حالات انقطاع المكافاة", 
    48: "المكافأت والمساعدة المالية", 
    49: "ملخص مبادرة رافد", 
    50: "معادلة المقررات بالكلية",
}

# ===== توليد لوحة الأزرار =====
def generate_keyboard(page=0):
    keyboard = []
    start = page * BUTTONS_PER_PAGE + 1
    end = min(start + BUTTONS_PER_PAGE, TOTAL_BUTTONS + 1)
    for i in range(start, end):
        name = BUTTON_NAMES.get(i, f"زر {i}")
        keyboard.append([InlineKeyboardButton(name, callback_data=f"btn{i}")])

    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton("⬅ السابق", callback_data=f"page_{page-1}"))
    if end <= TOTAL_BUTTONS:
        navigation.append(InlineKeyboardButton("التالي ➡", callback_data=f"page_{page+1}"))
    if navigation:
        keyboard.append(navigation)
    return InlineKeyboardMarkup(keyboard)

# ===== لوحة تحكم الأدمن =====
def generate_admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 تحديث", callback_data="refresh_admin")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ])

# ===== إدارة الأدمن =====
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ هذا الأمر خاص بالأدمن فقط")
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM buttons")
    buttons_count = cursor.fetchone()[0]

    cursor.execute("SELECT button_id, clicks FROM buttons ORDER BY button_id ASC")
    stats = cursor.fetchall()
    stats_text = "\n".join([f"{btn}: {clicks} نقرة" for btn, clicks in stats]) or "لا يوجد أزرار مفعلة بعد."

    admin_text = (
        f"📊 *لوحة تحكم الأدمن*\n\n"
        f"👥 عدد المستخدمين: {users_count}\n"
        f"🔘 عدد الأزرار المفعلة: {buttons_count}\n\n"
        f"📈 إحصائيات النقرات لكل زر:\n{stats_text}"
    )

    if hasattr(update, "message"):
        await update.message.reply_text(admin_text, parse_mode="Markdown", reply_markup=generate_admin_keyboard())
    elif hasattr(update, "callback_query"):
        await update.callback_query.edit_message_text(admin_text, parse_mode="Markdown", reply_markup=generate_admin_keyboard())

# ===== المعالجة الخلفية للأزرار =====
async def process_button(query, context):
    cursor.execute("SELECT type, file_id, text, caption FROM buttons WHERE button_id=?", (query.data,))
    result = cursor.fetchone()
    back_button = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back")]])
    if not result:
        await query.edit_message_text("لا يوجد رد لهذا الزر بعد.")
        return

    btn_type, file_id, text, caption = result
    cursor.execute("UPDATE buttons SET clicks = clicks + 1 WHERE button_id=?", (query.data,))
    conn.commit()
    await query.message.delete()

    if btn_type == "photo":
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=file_id, caption=caption, reply_markup=back_button)
    elif btn_type == "video":
        await context.bot.send_video(chat_id=query.message.chat.id, video=file_id, caption=caption, reply_markup=back_button)
    elif btn_type == "text":
        await context.bot.send_message(chat_id=query.message.chat.id, text=text, reply_markup=back_button)

# ===== التعامل مع ضغط الأزرار =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.edit_message_reply_markup(reply_markup=generate_keyboard(page))
        return
    if data == "back":
        await query.edit_message_text("مرحباً! اختر أحد الأزرار:", reply_markup=generate_keyboard(0))
        return
    if data == "refresh_admin":
        await admin_panel(update, context)
        return
    asyncio.create_task(process_button(query, context))

# ===== start مع رسالة ترحيبية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

    welcome_text = (
        "مرحباً بك في بوتنا 🔥\n\n"
        "يمكنك اختيار أحد الأزرار للأجابة على سؤالك.\n"
        "إذا كنت أدمن، استخدم /admin لمشاهدة لوحة التحكم."
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=generate_keyboard(0)
    )

# ===== /edit زر =====
async def edit_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ هذا الأمر خاص بالأدمن فقط")
        return
    if not context.args:
        await update.message.reply_text("استخدم:\n/edit btn1")
        return

    button_id = context.args[0].lower()
    if not button_id.startswith("btn"):
        await update.message.reply_text("❌ اسم زر غير صحيح")
        return

    context.user_data["editing"] = button_id
    await update.message.reply_text(f"✏️ أرسل الآن نص أو صورة أو فيديو لتعيينه للزر {button_id}")

# ===== استقبال محتوى الأدمن =====
async def receive_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    button_id = context.user_data.get("editing")
    if not button_id:
        return

    btn_type, file_id, text, caption = None, None, None, None
    if update.message.photo:
        btn_type = "photo"
        file_id = update.message.photo[-1].file_id
        caption = update.message.caption or ""
    elif update.message.video:
        btn_type = "video"
        file_id = update.message.video.file_id
        caption = update.message.caption or ""
    elif update.message.text:
        btn_type = "text"
        text = update.message.text
    else:
        await update.message.reply_text("❌ أرسل نص أو صورة أو فيديو فقط")
        return

    cursor.execute("DELETE FROM buttons WHERE button_id=?", (button_id,))
    cursor.execute("INSERT INTO buttons (button_id, type, file_id, text, caption) VALUES (?, ?, ?, ?, ?)",
                   (button_id, btn_type, file_id, text, caption))
    conn.commit()
    context.user_data.pop("editing")
    await update.message.reply_text(f"✅ تم تحديث {button_id} بنجاح")

# ===== /delete زر =====
async def delete_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        return
    button_id = context.args[0]
    cursor.execute("DELETE FROM buttons WHERE button_id=?", (button_id,))
    conn.commit()
    await update.message.reply_text("تم حذف الرد ✅")

# ===== تشغيل البوت مع Webhook لتجنب Conflict =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("edit", edit_button))
    app.add_handler(CommandHandler("delete", delete_button))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, receive_content))

    print("البوت يعمل الآن 🔥")
    
    # ⚡ استخدام polling مع استثناءات لتجنب conflict
    async def main():
        try:
            await app.run_polling()
        except Exception as e:
            print("⚠ خطأ أثناء التشغيل:", e)

    asyncio.run(main())