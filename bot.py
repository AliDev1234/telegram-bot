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
    raise ValueError("❌ BOT_TOKEN غير موجود")

ADMIN_IDS = [1000660019, 1816045034]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# حذف Webhook
# =========================
bot = Bot(TOKEN)

async def clear_webhook():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ تم حذف أي Webhook موجود")
        await asyncio.sleep(1)  # انتظر ثانية قبل بدء polling
    except Exception as e:
        print("⚠ تحذير عند حذف Webhook:", e)

# =========================
# DATABASE
# =========================
from db import save_button, get_button, add_click, get_stats, delete_button

# =========================
# الأزرار
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
# الكيبورد
# =========================
def generate_keyboard(page=0):
    keyboard = []
    start = page * BUTTONS_PER_PAGE + 1
    end = min(start + BUTTONS_PER_PAGE, TOTAL_BUTTONS + 1)

    for i in range(start, end):
        keyboard.append([
            InlineKeyboardButton(
                BUTTON_NAMES.get(i, f"قسم {i}"),
                callback_data=f"btn{i}"
            )
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
        return await update.message.reply_text("❌ للأدمن فقط")

    total_buttons, total_clicks = get_stats()

    await update.message.reply_text(
        f"📊 الإحصائيات:\n"
        f"الأزرار: {total_buttons}\n"
        f"الضغطات: {total_clicks}"
    )

# =========================
# /edit
# =========================
async def edit_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("❌ للأدمن فقط")

    if not context.args:
        return await update.message.reply_text("اكتب رقم الزر\nمثال:\n/edit 5")

    context.user_data["editing"] = f"btn{context.args[0]}"
    await update.message.reply_text("أرسل المحتوى الآن (نص، صورة، أو فيديو)")

# =========================
# /delete
# =========================
async def delete_button_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        return await update.message.reply_text("مثال:\n/delete 5")

    delete_button(f"btn{context.args[0]}")
    await update.message.reply_text("🗑 تم الحذف")

# =========================
# حفظ المحتوى
# =========================
async def receive_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "editing" not in context.user_data:
        return

    button_id = context.user_data["editing"]
    old_button = get_button(button_id) or {}

    if update.message.text:
        save_button(
            button_id,
            "text",
            update.message.text,
            old_button.get("caption")
        )

    elif update.message.photo:
        save_button(
            button_id,
            "photo",
            update.message.photo[-1].file_id,
            update.message.caption or old_button.get("caption")
        )

    elif update.message.video:
        save_button(
            button_id,
            "video",
            update.message.video.file_id,
            update.message.caption or old_button.get("caption")
        )

    context.user_data.pop("editing")
    await update.message.reply_text("✅ تم الحفظ")

# =========================
# الضغط على الأزرار
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        return await query.edit_message_reply_markup(reply_markup=generate_keyboard(page))

    button = get_button(data)
    if not button:
        return await query.message.reply_text("⚠ لا يوجد محتوى")

    add_click(data)

    if button["type"] == "text":
        await query.message.reply_text(button["text"])
    elif button["type"] == "photo":
        await query.message.reply_photo(button["file_id"], caption=button["caption"])
    elif button["type"] == "video":
        await query.message.reply_video(button["file_id"], caption=button["caption"])

# =========================
# التشغيل مع حل Conflict
# =========================
async def main():
    await clear_webhook()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("edit", edit_button))
    app.add_handler(CommandHandler("delete", delete_button_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, receive_content))

    # حل Conflict: retry loop
    while True:
        try:
            print("🚀 البوت يعمل الآن بدون Conflict")
            await app.run_polling(drop_pending_updates=True)
        except Exception as e:
            print("⚠ خطأ أثناء polling، إعادة المحاولة:", e)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())