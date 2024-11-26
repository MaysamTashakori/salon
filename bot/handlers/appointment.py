from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..keyboards.appointment_keyboard import (
    get_services_keyboard,
    get_dates_keyboard,
    get_times_keyboard,
    get_appointments_keyboard,
)
from ..database.models import Service, Appointment
from ..utils.date_helper import get_persian_date, get_available_times
import jdatetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    services = Service.get_all_active()
    text = """
💇‍♀️ لطفاً خدمت مورد نظر خود را انتخاب کنید:

قیمت‌ها شامل مالیات و هزینه‌های جانبی است.
"""
    
    await query.edit_message_text(
        text,
        reply_markup=get_services_keyboard(services)
    )

async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    service_id = int(query.data.split('_')[1])
    service = Service.get_by_id(service_id)
    
    # نمایش 7 روز آینده
    dates = []
    today = jdatetime.datetime.now()
    
    for i in range(7):
        date = today + jdatetime.timedelta(days=i)
        has_time = Appointment.check_date_availability(service_id, date)
        if has_time:
            dates.append(date)
    
    text = f"""
🗓 انتخاب تاریخ برای {service.name}
💰 قیمت: {service.price:,} تومان
⏱ مدت زمان: {service.duration} دقیقه

لطفاً تاریخ مورد نظر را انتخاب کنید:
"""
    
    await query.edit_message_text(
        text,
        reply_markup=get_dates_keyboard(dates, service_id)
    )
async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, service_id, date_str = query.data.split('_')
    service = Service.get_by_id(int(service_id))
    selected_date = jdatetime.datetime.strptime(date_str, '%Y-%m-%d')
    
    available_times = get_available_times(service, selected_date)
    
    text = f"""
⏰ انتخاب ساعت برای {service.name}
📅 تاریخ: {get_persian_date(selected_date)}

لطفاً ساعت مورد نظر را انتخاب کنید:
"""
    
    await query.edit_message_text(
        text,
        reply_markup=get_times_keyboard(available_times, service_id, date_str)
    )

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, service_id, date_str, time_str = query.data.split('_')
    service = Service.get_by_id(int(service_id))
    
    # ایجاد نوبت در دیتابیس
    appointment = Appointment.create(
        user_id=query.from_user.id,
        service_id=service_id,
        date=date_str,
        time=time_str
    )
    
    text = f"""
✅ پیش‌رزرو نوبت شما ثبت شد

💇‍♀️ خدمت: {service.name}
📅 تاریخ: {get_persian_date(date_str)}
⏰ ساعت: {time_str}
💰 مبلغ قابل پرداخت: {service.price:,} تومان

لطفاً برای تکمیل رزرو، پرداخت را انجام دهید.
"""
    
    from ..keyboards.payment_keyboard import get_payment_keyboard
    await query.edit_message_text(
        text,
        reply_markup=get_payment_keyboard(appointment.id)
    )
async def show_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    appointments = Appointment.get_user_appointments(query.from_user.id)
    
    if not appointments:
        text = "📋 شما هیچ نوبت فعالی ندارید!"
    else:
        text = "📋 نوبت‌های شما:\n\n"
        for apt in appointments:
            service = Service.get_by_id(apt.service_id)
            status_emoji = {
                'pending': '⏳',
                'confirmed': '✅',
                'cancelled': '❌',
                'completed': '🏁'
            }
            
            text += f"""
{status_emoji[apt.status]} {service.name}
📅 تاریخ: {get_persian_date(apt.date)}
⏰ ساعت: {apt.time}
💰 مبلغ: {service.price:,} تومان
ــــــــــــــــــــــــــــــ
"""
    
    keyboard = get_appointments_keyboard(appointments)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
def get_services_keyboard(services_list):
    keyboard = []
    for service in services_list:
        keyboard.append([
            InlineKeyboardButton(
                f"{service.name} - {service.price:,} تومان",
                callback_data=f"service_{service.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)