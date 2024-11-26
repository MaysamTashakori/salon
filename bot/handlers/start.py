from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database.models import User
from ..keyboards.main_keyboard import get_main_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user = User.get_by_telegram_id(update.effective_user.id)
    
    welcome_text = (
        "👋 سلام به سالن زیبایی ما خوش آمدید!\n\n"
        "🌟 خدمات ما:\n"
        "💇‍♀️ کوتاهی مو\n"
        "💅 مانیکور و پدیکور\n"
        "👰 آرایش عروس\n"
        "💆‍♀️ اصلاح صورت\n"
        "🎨 رنگ مو\n\n"
    )
    
    if not user:
        keyboard = [
            [InlineKeyboardButton("📝 ثبت‌نام", callback_data="register")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")]
        ]
        welcome_text += "🔔 برای استفاده از خدمات، لطفا ابتدا ثبت‌نام کنید."
    else:
        keyboard = [
            [
                InlineKeyboardButton("🗓 رزرو نوبت", callback_data="services"),
                InlineKeyboardButton("👤 پروفایل من", callback_data="profile")
            ],
            [
                InlineKeyboardButton("📅 نوبت‌های من", callback_data="appointments"),
                InlineKeyboardButton("❓ راهنما", callback_data="help")
            ]
        ]
        welcome_text += "🎉 خوشحالیم که همراه ما هستید!"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    help_text = (
        "🔰 راهنمای استفاده از ربات:\n\n"
        "1️⃣ ثبت‌نام:\n"
        "برای استفاده از خدمات، ابتدا باید ثبت‌نام کنید.\n\n"
        "2️⃣ رزرو نوبت:\n"
        "- انتخاب خدمت\n"
        "- انتخاب تاریخ\n"
        "- انتخاب ساعت\n"
        "- پرداخت\n\n"
        "3️⃣ مدیریت نوبت‌ها:\n"
        "در بخش «نوبت‌های من» می‌توانید:\n"
        "- نوبت‌های فعال را ببینید\n"
        "- نوبت‌ها را لغو کنید\n\n"
        "4️⃣ پشتیبانی:\n"
        "برای ارتباط با پشتیبانی پیام خود را ارسال کنید.\n\n"
        "📞 شماره تماس: 021-12345678\n"
        "📍 آدرس: تهران، خیابان ولیعصر"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup)

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle return to main menu"""
    query = update.callback_query
    await query.answer()
    
    user = User.get_by_telegram_id(update.effective_user.id)
    keyboard = get_main_keyboard(user.id if user else None)
    
    await query.message.edit_text(
        "🏠 منوی اصلی\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard
    )
