from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters
)
from ..database.models import User

# States
PHONE, NAME, CONFIRM = range(3)

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start registration process"""
    user = User.get_by_telegram_id(update.effective_user.id)
    if user:
        keyboard = [
            [InlineKeyboardButton("🗓 رزرو نوبت", callback_data="services")],
            [InlineKeyboardButton("👤 پروفایل من", callback_data="profile")]
        ]
        message = f"👋 {user.full_name} عزیز، خوش آمدید!\n\nشما قبلاً ثبت‌نام کرده‌اید."
        
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.edit_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    keyboard = [[KeyboardButton("📱 ارسال شماره تماس", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    message = "👋 به سالن زیبایی ما خوش آمدید!\n\n📱 برای ثبت‌نام، شماره تماس خود را ارسال کنید:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's phone number"""
    if not update.message.contact:
        await update.message.reply_text("⚠️ لطفاً از دکمه ارسال شماره تماس استفاده کنید.")
        return PHONE
    
    context.user_data['phone'] = update.message.contact.phone_number
    
    await update.message.reply_text(
        "✅ شماره تماس ثبت شد.\n\n👤 نام و نام خانوادگی خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's full name"""
    full_name = update.message.text.strip()
    
    if len(full_name.split()) < 2:
        await update.message.reply_text("⚠️ لطفاً نام و نام خانوادگی کامل را وارد کنید.")
        return NAME
    
    context.user_data['full_name'] = full_name
    
    keyboard = [[InlineKeyboardButton("✅ تأیید و ثبت نام", callback_data="confirm")]]
    
    await update.message.reply_text(
        f"📝 اطلاعات شما:\n\n"
        f"📱 شماره تماس: {context.user_data['phone']}\n"
        f"👤 نام و نام خانوادگی: {context.user_data['full_name']}\n\n"
        "آیا اطلاعات فوق را تأیید می‌کنید؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CONFIRM

async def confirm_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save user data"""
    query = update.callback_query
    await query.answer()
    
    user = User.create_user(
        telegram_id=update.effective_user.id,
        phone=context.user_data['phone'],
        full_name=context.user_data['full_name']
    )
    
    keyboard = [
        [InlineKeyboardButton("🗓 رزرو نوبت", callback_data="services")],
        [InlineKeyboardButton("👤 پروفایل من", callback_data="profile")]
    ]
    
    await query.message.edit_text(
        f"✅ {user.full_name} عزیز، ثبت‌نام شما انجام شد!\n\n"
        "از منوی زیر انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ConversationHandler.END

def get_registration_handler():
    """Get registration conversation handler"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start_registration),
            CallbackQueryHandler(start_registration, pattern="^register$")
        ],
        states={
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, get_phone)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CONFIRM: [CallbackQueryHandler(confirm_registration, pattern="^confirm$")]
        },
        fallbacks=[],
        name="registration",
        persistent=False
    )
