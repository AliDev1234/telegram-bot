import asyncio
from telegram import Bot
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(TOKEN)

async def clear_webhook():
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ تم حذف Webhook القديم")

asyncio.run(clear_webhook())