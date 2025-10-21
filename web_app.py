from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "attendance.db"

def get_employees():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, hourly_rate FROM employees")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_records(start=None, end=None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    if not start or not end:
        cur.execute("SELECT name, type, timestamp, location FROM attendance WHERE date(timestamp)=date('now')")
    else:
        cur.execute("SELECT name, type, timestamp, location FROM attendance WHERE date(timestamp) BETWEEN ? AND ?", (start, end))
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route("/")
def home():
    employees = get_employees()
    return render_template("index.html", employees=employees)

@app.route("/report/today")
def report_today():
    records = get_records()
    return render_template("report.html", records=records, start="اليوم", end="اليوم")

@app.route("/salary")
def salary():
    user_id = request.args.get("user_id")
    start = request.args.get("start")
    end = request.args.get("end")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # حساب الساعات
    cur.execute("""
        SELECT timestamp, type FROM attendance
        WHERE user_id=? AND date(timestamp) BETWEEN ? AND ?
        ORDER BY timestamp ASC
    """, (user_id, start, end))
    records = cur.fetchall()

    cur.execute("SELECT name, hourly_rate FROM employees WHERE user_id=?", (user_id,))
    emp = cur.fetchone()
    conn.close()

    if not emp:
        return f"<h3>❌ الموظف غير موجود</h3>"

    total_hours = 0
    in_time = None
    for t, typ in records:
        if typ == "حضور":
            in_time = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        elif typ == "انصراف" and in_time:
            out_time = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            total_hours += (out_time - in_time).total_seconds() / 3600
            in_time = None

    salary = round(total_hours * emp[1], 2)
    return f"<h3>👤 {emp[0]}<br>⏱️ إجمالي الساعات: {round(total_hours,2)}<br>💰 المرتب: {salary}</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


