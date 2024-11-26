from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_profile_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📱 ویرایش شماره", callback_data="edit_phone"),
            InlineKeyboardButton("👤 ویرایش نام", callback_data="edit_name")
        ],
        [
            InlineKeyboardButton("💰 شارژ کیف پول", callback_data="charge_wallet"),
            InlineKeyboardButton("⭐️ امتیازات من", callback_data="my_points")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_appointments_keyboard():
    keyboard = [
        [InlineKeyboardButton("🗑 لغو نوبت", callback_data="cancel_appointment")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
