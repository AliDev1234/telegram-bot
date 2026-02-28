import os
import sqlite3

DB_FOLDER = os.path.join(os.getcwd(), "db")
os.makedirs(DB_FOLDER, exist_ok=True)
DB_PATH = os.path.join(DB_FOLDER, "bot.db")

# حذف قاعدة البيانات القديمة إذا وجدت
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑 تم حذف قاعدة البيانات القديمة.")

# إنشاء قاعدة بيانات جديدة
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# جدول المستخدمين
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY
)
""")

# جدول الأزرار
cursor.execute("""
CREATE TABLE buttons (
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
print(f"✅ قاعدة البيانات تم إنشاؤها بنجاح في {DB_PATH}")