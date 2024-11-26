import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from bot.database.models import Database, User, Service

def seed_database():
    db = Database()
    
    # اضافه کردن خدمات نمونه
    services = [
        ("کوتاه کردن مو", "کوتاهی مو با متدهای روز", 120000, 45),
        ("رنگ مو", "رنگ مو با برندهای معتبر", 450000, 120),
        ("اصلاح ابرو", "اصلاح ابرو با متد تخصصی", 80000, 30),
        ("میکاپ", "آرایش صورت حرفه‌ای", 350000, 90),
        ("پاکسازی پوست", "پاکسازی عمیق پوست", 250000, 60),
        ("مانیکور", "مانیکور ناخن با طرح دلخواه", 150000, 45),
    ]
    
    cursor = db.conn.cursor()
    cursor.executemany("""
        INSERT INTO services (name, description, price, duration)
        VALUES (?, ?, ?, ?)
    """, services)
    
    # اضافه کردن کاربران نمونه
    users = [
        (11111111, "user1", "مریم", "احمدی", "09121111111"),
        (22222222, "user2", "زهرا", "محمدی", "09122222222"),
        (33333333, "user3", "فاطمه", "حسینی", "09123333333"),
    ]
    
    cursor.executemany("""
        INSERT INTO users (telegram_id, username, first_name, last_name, phone)
        VALUES (?, ?, ?, ?, ?)
    """, users)
    
    # اضافه کردن نوبت‌های نمونه
    appointments = [
        (1, 1, "2024-01-20", "10:00", "confirmed"),
        (2, 3, "2024-01-20", "11:00", "pending"),
        (3, 2, "2024-01-21", "14:30", "confirmed"),
    ]
    
    cursor.executemany("""
        INSERT INTO appointments (user_id, service_id, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    """, appointments)
    
    db.conn.commit()
    print("✅ داده‌های نمونه با موفقیت اضافه شدند")

if __name__ == "__main__":
    seed_database()
