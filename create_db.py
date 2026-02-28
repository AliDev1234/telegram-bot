import os
import sqlite3

# إنشاء مجلد db إذا لم يكن موجود
os.makedirs("db", exist_ok=True)

# مسار قاعدة البيانات
DB_PATH = os.path.join("db", "bot.db")

# إنشاء الاتصال بالقاعدة
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# إنشاء الجداول
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
conn.close()

print("✅ قاعدة البيانات تم إنشاؤها بنجاح في db/bot.db")