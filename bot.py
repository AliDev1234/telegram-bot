import os
import sys
import json
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# تشغيل فقط على Railway
# =========================
if not os.getenv("RAILWAY"):
    print("⚠ البوت لا يعمل إلا على Railway. إنهاء العملية.")
    sys.exit(0)

# =========================
# الإعدادات
# =========================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في Railway Variables")

ADMIN_IDS = [1000660019, 1816045034]  # الأدمنين

logging.basicConfig(level=logging.INFO)

# =========================
# حذف أي Webhook قديم قبل تشغيل البوت
# =========================
bot = Bot(TOKEN)

async def clear_webhook():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ تم حذف Webhook القديم")
    except Exception as e:
        print(f"⚠ حدث خطأ أثناء مسح Webhook: {e}")

# =========================
# ملف التخزين
# =========================
BUTTONS_FILE = "buttons.json"

if os.path.exists(BUTTONS_FILE):
    with open(BUTTONS_FILE, "r", encoding="utf-8") as f:
        buttons_data = json.load(f)
else:
    buttons_data = {}

# =========================
# أسماء الأقسام الـ50
# =========================
BUTTONS_PER_PAGE = 10
TOTAL_BUTTONS = 50
BUTTON_NAMES = {
    1: "الرياضة", 2: "التقنية", 3: "الأخبار", 4: "التسلية", 5: "الموسيقى",
    6: "الأفلام", 7: "البرمجة", 8: "التصوير", 9: "الأدب", 10: "التاريخ",
    11: "العلم", 12: "الصحة", 13: "السفر", 14: "الطبخ", 15: "اللغات",
    16: "الذكاء الاصطناعي", 17: "الألعاب", 18: "الفنون", 19: "السياسة", 20: "المال والأعمال",
    21: "التعليم", 22: "الرياضيات", 23: "الفضاء", 24: "الأبراج", 25: "القصص",
    26: "الفلسفة", 27: "اليوغا", 28: "التطوير الذاتي", 29: "الحيوانات", 30: "البيئة",
    31: "الرياضة الإلكترونية", 32: "البرامج", 33: "الذكريات", 34: "التاريخ الإسلامي", 35: "الشعر",
    36: "القصائد", 37: "القصص القصيرة", 38: "الحرف اليدوية", 39: "الرياضة النسائية", 40: "الأخبار العاجلة",
    41: "الأسواق", 42: "التكنولوجيا الحديثة", 43: "السيارات", 44: "الطقس", 45: "الموضة",
    46: "الديكور", 47: "التجارة الإلكترونية", 48: "المناسبات", 49: "التنمية البشرية", 50: "المشاريع الصغيرة"
}

# =========================
# توليد لوحة الأزرار
# =========================
def generate_keyboard(page=0):
    keyboard = []
    start = page * BUTTONS_PER_PAGE + 1
    end = min(start + BUTTONS_PER_PAGE, TOTAL_BUTTONS + 1)
    for i in range(start, end):
        keyboard.append([
            InlineKeyboardButton(BUTTON_NAMES.get(i, f"قسم {i}"), callback_data=f"btn{i}")
        ])
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
    await update.message.reply_text(
        "مرحباً بك 🔥 اختر أحد الأقسام:",
        reply_markup=generate_keyboard(0)
    )

# =========================
# /admin
# =========================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ هذا الأمر خاص بالأدمن فقط")
        return
    total_buttons = len(buttons_data)
    total_clicks = sum(b.get("clicks", 0) for b in buttons_data.values())
    await update.message.reply_text(
        f"📊 إحصائيات البوت:\n\n"
        f"🔥 عدد الأزرار المخزنة: {total_buttons}\n"
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
    if button_id in buttons_data:
        buttons_data.pop(button_id)
        with open(BUTTONS_FILE, "w", encoding="utf-8") as f:
            json.dump(buttons_data, f, ensure_ascii=False, indent=4)
    await update.message.reply_text("🗑 تم حذف محتوى الزر بنجاح")

# =========================
# استقبال محتوى الأدمن
# =========================
async def receive_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "editing" not in context.user_data:
        return
    button_id = context.user_data["editing"]
    if update.message.text:
        buttons_data[button_id] = {
            "type": "text",
            "text": update.message.text,
            "clicks": buttons_data.get(button_id, {}).get("clicks", 0)
        }
    elif update.message.photo:
        buttons_data[button_id] = {
            "type": "photo",
            "file_id": update.message.photo[-1].file_id,
            "caption": update.message.caption,
            "clicks": buttons_data.get(button_id, {}).get("clicks", 0)
        }
    elif update.message.video:
        buttons_data[button_id] = {
            "type": "video",
            "file_id": update.message.video.file_id,
            "caption": update.message.caption,
            "clicks": buttons_data.get(button_id, {}).get("clicks", 0)
        }
    with open(BUTTONS_FILE, "w", encoding="utf-8") as f:
        json.dump(buttons_data, f, ensure_ascii=False, indent=4)
    context.user_data.pop("editing")
    await update.message.reply_text("✅ تم حفظ المحتوى بنجاح")

# =========================
# الأزرار
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.edit_message_reply_markup(reply_markup=generate_keyboard(page))
        return
    button = buttons_data.get(data)
    if button:
        button["clicks"] = button.get("clicks", 0) + 1
        with open(BUTTONS_FILE, "w", encoding="utf-8") as f:
            json.dump(buttons_data, f, ensure_ascii=False, indent=4)
        type_ = button["type"]
        if type_ == "text":
            await query.message.reply_text(button["text"])
        elif type_ == "photo":
            await query.message.reply_photo(button["file_id"], caption=button.get("caption"))
        elif type_ == "video":
            await query.message.reply_video(button["file_id"], caption=button.get("caption"))
    else:
        await query.message.reply_text("⚠ لا يوجد محتوى لهذا الزر بعد")

# =========================
# التشغيل النهائي
# =========================
async def main():
    # إزالة أي Webhook قديم قبل بدء البوت
    await clear_webhook()

    # تشغيل البوت
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("edit", edit_button))
    app.add_handler(CommandHandler("delete", delete_button))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, receive_content))

    print("🚀 البوت يعمل الآن على Railway مع حل /edit")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())