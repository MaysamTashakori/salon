from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📋 مدیریت خدمات", callback_data="admin_services"),
            InlineKeyboardButton("🗓 نوبت‌ها", callback_data="admin_appointments")
        ],
        [
            InlineKeyboardButton("👥 کاربران", callback_data="admin_users"),
            InlineKeyboardButton("💰 گزارش مالی", callback_data="admin_finance")
        ],
        [
            InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_services_management_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ افزودن خدمت جدید", callback_data="admin_add_service")],
        [InlineKeyboardButton("✏️ ویرایش خدمات", callback_data="admin_edit_services")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_users_management_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="admin_search_user"),
            InlineKeyboardButton("📊 آمار کاربران", callback_data="admin_users_stats")
        ],
        [
            InlineKeyboardButton("⭐️ کاربران ویژه", callback_data="admin_vip_users"),
            InlineKeyboardButton("❌ کاربران مسدود", callback_data="admin_blocked_users")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)
