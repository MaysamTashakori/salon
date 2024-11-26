from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard(user_id):
    keyboard = [
        [
            InlineKeyboardButton("🗓 رزرو نوبت", callback_data="services"),
            InlineKeyboardButton("👤 پروفایل من", callback_data="profile")
        ],
        [
            InlineKeyboardButton("📋 نوبت‌های من", callback_data="appointments"),
            InlineKeyboardButton("💰 کیف پول", callback_data="wallet")
        ],
        [
            InlineKeyboardButton("⭐️ امتیازات", callback_data="points"),
            InlineKeyboardButton("❓ راهنما", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
    ]])
