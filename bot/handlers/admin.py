from telegram import Update
from telegram.ext import ContextTypes
from ..config import ADMIN_IDS
from ..keyboards.admin_keyboard import get_admin_keyboard
from ..database.models import User, Appointment, Service
from telegram import Update
from telegram.ext import ContextTypes
from ..database.models import User, Appointment, Service
from ..utils.date_helper import get_persian_date
from ..utils.report_generator import ReportGenerator
from ..keyboards.admin_keyboard import (
    get_admin_keyboard,
    get_services_management_keyboard,
    get_users_management_keyboard
)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ شما دسترسی ادمین ندارید!")
        return

    stats = get_admin_stats()
    text = f"""
👤 پنل مدیریت

📊 آمار کلی:
• کاربران: {stats['users_count']}
• نوبت‌های امروز: {stats['today_appointments']}
• درآمد امروز: {stats['today_income']:,} تومان
• نوبت‌های در انتظار: {stats['pending_appointments']}
"""
    await update.message.reply_text(text, reply_markup=get_admin_keyboard())

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await query.answer("⛔️ دسترسی محدود شده", show_alert=True)
        return
    
    action = query.data.split('_')[1]
    
    if action == "services":
        await manage_services(query)
    elif action == "appointments":
        await show_all_appointments(query)
    elif action == "users":
        await manage_users(query)
    elif action == "broadcast":
        context.user_data['admin_state'] = 'waiting_broadcast'
        await query.edit_message_text("پیام خود را برای ارسال به همه کاربران وارد کنید:")

async def manage_services(query):
    services = Service.get_all_services()
    text = "📋 لیست خدمات:\n\n"
    for service in services:
        text += f"""
🔸 {service.name}
💰 قیمت: {service.price:,} تومان
⏱ مدت: {service.duration} دقیقه
وضعیت: {'فعال' if service.is_active else 'غیرفعال'}
──────────────
"""
    await query.edit_message_text(text, reply_markup=get_services_management_keyboard())
def get_admin_stats():
    """محاسبه آمار کلی برای پنل ادمین"""
    return {
        'users_count': User.count_all(),
        'today_appointments': Appointment.count_today(),
        'today_income': Appointment.calculate_today_income(),
        'pending_appointments': Appointment.count_pending()
    }

async def show_all_appointments(query):
    """نمایش تمام نوبت‌ها برای ادمین"""
    appointments = Appointment.get_all_appointments()
    text = "📋 لیست تمام نوبت‌ها:\n\n"
    for apt in appointments:
        text += f"""
🔹 {apt.service.name}
👤 کاربر: {apt.user.full_name}
📅 تاریخ: {get_persian_date(apt.date)}
⏰ ساعت: {apt.time}
وضعیت: {apt.get_status_display()}
──────────────
"""
    await query.edit_message_text(text, reply_markup=get_admin_keyboard())

async def manage_users(query):
    """مدیریت کاربران"""
    users = User.get_all_users()
    text = "👥 لیست کاربران:\n\n"
    for user in users:
        text += f"""
👤 {user.full_name}
📱 {user.phone}
💰 کیف پول: {user.wallet_balance:,} تومان
⭐️ امتیاز: {user.points}
──────────────
"""
    await query.edit_message_text(text, reply_markup=get_users_management_keyboard())


async def export_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    report_type = query.data.split('_')[2]
    
    if report_type == 'excel':
        file_path = ReportGenerator.generate_excel()
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=open(file_path, 'rb'),
            caption='📊 گزارش نوبت‌ها (Excel)'
        )
    elif report_type == 'pdf':
        file_path = ReportGenerator.generate_pdf()
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=open(file_path, 'rb'),
            caption='📊 گزارش نوبت‌ها (PDF)'
        )
