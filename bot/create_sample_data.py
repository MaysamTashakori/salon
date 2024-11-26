from bot.database.models import User, Service, Appointment, Review, UserRole, AppointmentStatus
from datetime import datetime, timedelta
from bot.database.database import SessionLocal

def create_sample_data():
    # Create admin user
    admin = User.create_user(
        telegram_id=123456789,
        phone="+989123456789",
        full_name="مدیر سالن"
    )
    admin.role = UserRole.ADMIN
    
    # Create staff members
    staff1 = User.create_user(
        telegram_id=987654321,
        phone="+989111111111",
        full_name="سارا محمدی"
    )
    staff1.role = UserRole.STAFF
    
    staff2 = User.create_user(
        telegram_id=987654322,
        phone="+989222222222",
        full_name="مریم احمدی"
    )
    staff2.role = UserRole.STAFF

    # Create services
    services = [
        {
            "name": "کوتاهی مو",
            "description": "کوتاهی مو با جدیدترین متدها",
            "price": 250000,
            "duration": 45,
            "category": "مو",
            "image_url": "haircut.jpg"
        },
        {
            "name": "رنگ مو",
            "description": "رنگ مو با برندهای معتبر و تضمین کیفیت",
            "price": 850000,
            "duration": 120,
            "category": "مو",
            "image_url": "hair_color.jpg"
        },
        {
            "name": "مانیکور",
            "description": "مانیکور ناخن با طرح دلخواه",
            "price": 180000,
            "duration": 60,
            "category": "ناخن",
            "image_url": "manicure.jpg"
        },
        {
            "name": "پدیکور",
            "description": "پدیکور و مراقبت از پوست پا",
            "price": 200000,
            "duration": 60,
            "category": "ناخن",
            "image_url": "pedicure.jpg"
        },
        {
            "name": "اصلاح ابرو",
            "description": "اصلاح ابرو با متد تخصصی",
            "price": 150000,
            "duration": 30,
            "category": "صورت",
            "image_url": "eyebrow.jpg"
        },
        {
            "name": "میکاپ",
            "description": "آرایش صورت حرفه‌ای",
            "price": 900000,
            "duration": 90,
            "category": "صورت",
            "image_url": "makeup.jpg"
        }
    ]
    
    created_services = []
    for service_data in services:
        service = Service.create_service(**service_data)
        created_services.append(service)

    # Create some sample clients
    clients = [
        {
            "telegram_id": 111111111,
            "phone": "+989333333333",
            "full_name": "نیلوفر کریمی"
        },
        {
            "telegram_id": 222222222,
            "phone": "+989444444444",
            "full_name": "زهرا رضایی"
        }
    ]
    
    created_clients = []
    for client_data in clients:
        client = User.create_user(**client_data)
        created_clients.append(client)

    # Create sample appointments
    base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    
    appointments = [
        {
            "user": created_clients[0],
            "service": created_services[0],
            "staff": staff1,
            "appointment_time": base_time + timedelta(days=1),
            "status": AppointmentStatus.CONFIRMED
        },
        {
            "user": created_clients[1],
            "service": created_services[1],
            "staff": staff2,
            "appointment_time": base_time + timedelta(days=1, hours=2),
            "status": AppointmentStatus.PENDING
        }
    ]
    
    for appt_data in appointments:
        appointment = Appointment(
            user_id=appt_data["user"].id,
            service_id=appt_data["service"].id,
            staff_id=appt_data["staff"].id,
            appointment_time=appt_data["appointment_time"],
            end_time=appt_data["appointment_time"] + timedelta(minutes=appt_data["service"].duration),
            status=appt_data["status"]
        )
        with SessionLocal() as session:
            session.add(appointment)
            session.commit()

    print("✅ نمونه داده‌ها با موفقیت ایجاد شدند!")

if __name__ == "__main__":
    create_sample_data()
