from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_payment_keyboard(appointment_id):
    keyboard = [
        [
            InlineKeyboardButton("💳 درگاه بانکی", callback_data=f"pay_bank_{appointment_id}"),
            InlineKeyboardButton("👝 کیف پول", callback_data=f"pay_wallet_{appointment_id}")
        ],
        [InlineKeyboardButton("💎 استفاده از تخفیف", callback_data=f"pay_discount_{appointment_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="appointments")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_methods_keyboard(appointment_id):
    keyboard = [
        [
            InlineKeyboardButton("🏧 سامان", callback_data=f"bank_saman_{appointment_id}"),
            InlineKeyboardButton("🏧 ملت", callback_data=f"bank_mellat_{appointment_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"pay_{appointment_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)
