from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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

def get_dates_keyboard(dates, service_id):
    keyboard = []
    for date in dates:
        keyboard.append([
            InlineKeyboardButton(
                date.strftime("%Y-%m-%d"),
                callback_data=f"date_{service_id}_{date.strftime('%Y-%m-%d')}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_services")])
    return InlineKeyboardMarkup(keyboard)

def get_times_keyboard(times, service_id, date_str):
    keyboard = []
    for time in times:
        keyboard.append([
            InlineKeyboardButton(
                time,
                callback_data=f"time_{service_id}_{date_str}_{time}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"back_to_dates_{service_id}")])
    return InlineKeyboardMarkup(keyboard)

def get_appointments_keyboard(appointments):
    keyboard = []
    for appointment in appointments:
        keyboard.append([
            InlineKeyboardButton(
                f"❌ لغو نوبت {appointment.id}",
                callback_data=f"cancel_appointment_{appointment.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_profile")])
    return InlineKeyboardMarkup(keyboard)
