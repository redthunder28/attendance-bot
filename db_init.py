import sqlite3

DB = "attendance.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# جدول الموظفين
cur.execute("""
CREATE TABLE IF NOT EXISTS employees (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    hourly_rate REAL DEFAULT 0
)
""")

# جدول الحضور والانصراف
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    type TEXT,
    timestamp TEXT,
    location TEXT,
    photo_path TEXT
)
""")

conn.commit()
conn.close()

print("✅ قاعدة البيانات تم إنشاؤها بنجاح: attendance.db")
