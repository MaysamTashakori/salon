from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters
)
from ..database.models import User, Appointment, Service, Payment, AppointmentStatus
from ..database.database import SessionLocal
from ..utils.date_helper import get_persian_date
from ..keyboards.main_keyboard import get_main_keyboard

# States
EDIT_NAME, EDIT_PHONE = range(2)

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile information"""
    query = update.callback_query
    await query.answer()
    
    user = User.get_by_telegram_id(update.effective_user.id)
    if not user:
        await query.message.reply_text(
            "⚠️ لطفا ابتدا ثبت‌نام کنید!",
            reply_markup=get_main_keyboard(update.effective_user.id)
        )
        return
    
    appointments = Appointment.get_user_appointments(user.id)
    total_appointments = len(appointments)
    active_appointments = len([a for a in appointments if a.status not in ['cancelled', 'completed']])
    
    text = f"""
👤 پروفایل شما:

نام: {user.full_name}
📱 شماره تماس: {user.phone}
📅 تاریخ عضویت: {get_persian_date(user.created_at)}

📊 آمار:
🗓 تعداد کل نوبت‌ها: {total_appointments}
✅ نوبت‌های فعال: {active_appointments}
"""
    
    keyboard = [
        [InlineKeyboardButton("🗓 نوبت‌های من", callback_data="my_appointments")],
        [
            InlineKeyboardButton("✏️ ویرایش نام", callback_data="edit_name"),
            InlineKeyboardButton("📱 ویرایش شماره", callback_data="edit_phone")
        ],
        [InlineKeyboardButton("💳 سوابق پرداخت", callback_data="payment_history")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]
    ]
    
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start name editing process"""
    query = update.callback_query
    await query.answer()
    
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("🔙 انصراف")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    sent_message = await query.message.reply_text(
        "👤 لطفا نام جدید خود را وارد کنید:",
        reply_markup=keyboard
    )
    
    context.user_data['last_bot_message'] = sent_message.message_id
    return EDIT_NAME

async def handle_edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new name input"""
    if update.message.text == "🔙 انصراف":
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت به پروفایل", callback_data="profile")
        ]])
        await update.message.reply_text(
            "عملیات ویرایش نام لغو شد.",
            reply_markup=keyboard
        )
        return ConversationHandler.END
    
    new_name = update.message.text
    user = User.get_by_telegram_id(update.effective_user.id)
    user.update_full_name(new_name)
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 بازگشت به پروفایل", callback_data="profile")
    ]])
    
    await update.message.reply_text(
        "✅ نام شما با موفقیت بروزرسانی شد!",
        reply_markup=keyboard
    )
    
    if 'last_bot_message' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['last_bot_message']
            )
        except:
            pass
    
    return ConversationHandler.END

async def start_edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start phone editing process"""
    query = update.callback_query
    await query.answer()
    
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 ارسال شماره تماس", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await query.message.reply_text(
        "📱 لطفا شماره تماس جدید خود را با استفاده از دکمه زیر ارسال کنید:",
        reply_markup=keyboard
    )
    return EDIT_PHONE

async def handle_edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new phone input"""
    contact = update.message.contact
    user = User.get_by_telegram_id(update.effective_user.id)
    user.update_phone_number(contact.phone_number)
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 بازگشت به پروفایل", callback_data="profile")
    ]])
    
    await update.message.reply_text(
        "✅ شماره تماس شما با موفقیت بروزرسانی شد!",
        reply_markup=keyboard
    )
    return ConversationHandler.END

async def show_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user appointments"""
    query = update.callback_query
    await query.answer()
    
    user = User.get_by_telegram_id(update.effective_user.id)
    appointments = Appointment.get_user_appointments(user.id)
    
    if not appointments:
        text = "📅 شما هیچ نوبت فعالی ندارید!"
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="profile")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    text = "📅 نوبت‌های شما:\n\n"
    keyboard = []
    
    status_emojis = {
        'pending': '⏳',
        'confirmed': '✅',
        'cancelled': '❌',
        'completed': '🏁'
    }
    
    for apt in appointments:
        service = Service.get_by_id(apt.service_id)
        status_emoji = status_emojis.get(apt.status, '❓')
        
        text += f"{status_emoji} {service.name}\n"
        text += f"📅 تاریخ: {get_persian_date(apt.appointment_time)}\n"
        text += f"⏰ ساعت: {apt.appointment_time.strftime('%H:%M')}\n"
        text += f"💰 مبلغ: {apt.final_price:,} تومان\n"
        text += f"🔵 وضعیت: {get_status_text(apt.status)}\n"
        text += "─────────────\n"
        
        if apt.status in ['pending', 'confirmed']:
            keyboard.append([
                InlineKeyboardButton(f"❌ لغو نوبت", callback_data=f"cancel_appointment_{apt.id}")
            ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="profile")])
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_payments_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user payment history"""
    query = update.callback_query
    await query.answer()
    
    user = User.get_by_telegram_id(update.effective_user.id)
    payments = Payment.get_user_payments(user.id)
    
    if not payments:
        text = "💳 تاریخچه پرداخت‌های شما خالی است!"
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="profile")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    text = "💳 تاریخچه پرداخت‌های شما:\n\n"
    
    for payment in payments:
        appointment = payment.appointment
        service = appointment.service
        
        text += f"🔵 {service.name}\n"
        text += f"💰 مبلغ: {payment.amount:,} تومان\n"
        text += f"📅 تاریخ: {get_persian_date(payment.created_at)}\n"
        text += f"🔵 وضعیت: {get_payment_status_text(payment.status)}\n"
        text += "─────────────\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="profile")]]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def cancel_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel user appointment"""
    query = update.callback_query
    await query.answer()
    
    appointment_id = int(query.data.split('_')[-1])
    user = User.get_by_telegram_id(update.effective_user.id)
    
    with SessionLocal() as session:
        appointment = session.query(Appointment).get(appointment_id)
        
        if not appointment:
            await query.message.edit_text(
                "❌ نوبت مورد نظر یافت نشد!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="my_appointments")
                ]])
            )
            return
        
        if appointment.user_id != user.id:
            await query.message.edit_text(
                "⚠️ شما مجاز به لغو این نوبت نیستید!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="my_appointments")
                ]])
            )
            return
        
        if appointment.status == AppointmentStatus.CANCELLED:
            await query.message.edit_text(
                "⚠️ این نوبت قبلاً لغو شده است!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="my_appointments")
                ]])
            )
            return
        
        appointment.cancel()
        service = appointment.service
        
        await query.message.edit_text(
            f"✅ نوبت شما با موفقیت لغو شد!\n\n"
            f"📅 تاریخ: {get_persian_date(appointment.appointment_time)}\n"
            f"⏰ ساعت: {appointment.appointment_time.strftime('%H:%M')}\n"
            f"💇‍♀️ خدمت: {service.name}\n",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت به نوبت‌ها", callback_data="my_appointments")
            ]])
        )

def get_status_text(status):
    """Convert status to Persian text"""
    status_texts = {
        'pending': 'در انتظار تأیید',
        'confirmed': 'تأیید شده',
        'cancelled': 'لغو شده',
        'completed': 'انجام شده'
    }
    return status_texts.get(status, 'نامشخص')

def get_payment_status_text(status):
    """Convert payment status to Persian text"""
    status_texts = {
        'pending': 'در انتظار پرداخت',
        'completed': 'پرداخت شده',
        'failed': 'ناموفق'
    }
    return status_texts.get(status, 'نامشخص')

def get_profile_handlers():
    """Return all profile related handlers"""
    edit_name_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_edit_name, pattern="^edit_name$")],
        states={
            EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_name)]
        },
        fallbacks=[
            CallbackQueryHandler(show_profile, pattern="^profile$"),
            MessageHandler(filters.Regex("^🔙 انصراف$"), handle_edit_name)
        ],
        per_message=True
    )
    
    edit_phone_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_edit_phone, pattern="^edit_phone$")],
        states={
            EDIT_PHONE: [MessageHandler(filters.CONTACT, handle_edit_phone)]
        },
        fallbacks=[CallbackQueryHandler(show_profile, pattern="^profile$")],
        per_message=True
    )
    
    handlers = [
        edit_name_handler,
        edit_phone_handler,
        CallbackQueryHandler(show_profile, pattern="^profile$"),
        CallbackQueryHandler(show_appointments, pattern="^my_appointments$"),
        CallbackQueryHandler(show_payments_history, pattern="^payment_history$"),
        CallbackQueryHandler(cancel_appointment, pattern="^cancel_appointment_\d+$")
    ]
    
    return handlers