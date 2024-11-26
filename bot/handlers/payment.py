from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from ..database.models import Payment, Appointment, Service, User
from ..utils.payment_helper import create_payment_link, verify_payment as verify_payment_transaction, format_price
from ..utils.date_helper import get_persian_date
from ..keyboards.main_keyboard import get_main_keyboard

# Payment States
PAYMENT_METHOD, CONFIRM_PAYMENT = range(2)

async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available payment methods"""
    query = update.callback_query
    await query.answer()
    
    appointment_id = int(query.data.split('_')[1])
    appointment = Appointment.get_by_id(appointment_id)
    service = Service.get_by_id(appointment.service_id)
    
    keyboard = [
        [InlineKeyboardButton("💳 پرداخت آنلاین", callback_data=f"online_{appointment_id}")],
        [InlineKeyboardButton("💵 پرداخت حضوری", callback_data=f"cash_{appointment_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="appointments")]
    ]
    
    await query.message.edit_text(
        f"💳 پرداخت نوبت {appointment.date}\n\n"
        f"💇‍♀️ خدمت: {service.name}\n"
        f"💰 مبلغ: {format_price(service.price)}\n\n"
        "لطفاً روش پرداخت را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process online payment"""
    query = update.callback_query
    await query.answer()
    
    appointment_id = int(query.data.split('_')[1])
    appointment = Appointment.get_by_id(appointment_id)
    service = Service.get_by_id(appointment.service_id)
    
    payment = Payment.create(
        appointment_id=appointment_id,
        amount=service.price
    )
    
    payment_link = create_payment_link(service.price, payment.id)
    
    keyboard = [
        [InlineKeyboardButton("💳 پرداخت آنلاین", url=payment_link)],
        [InlineKeyboardButton("✅ تأیید پرداخت", callback_data=f"verify_{payment.id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"pay_{appointment_id}")]
    ]
    
    await query.message.edit_text(
        "🔄 در حال انتقال به درگاه پرداخت...\n\n"
        "پس از پرداخت، دکمه «تأیید پرداخت» را بزنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify payment status"""
    query = update.callback_query
    await query.answer()
    
    payment_id = int(query.data.split('_')[1])
    payment = Payment.get_by_id(payment_id)
    
    if not payment:
        await query.message.edit_text(
            "❌ پرداخت مورد نظر یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="appointments")
            ]])
        )
        return
    
    if payment.status == 'completed':
        await query.message.edit_text(
            "✅ این پرداخت قبلاً تأیید شده است!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت به نوبت‌ها", callback_data="appointments")
            ]])
        )
        return
    
    result = verify_payment_transaction(payment.id)
    
    if result['success']:
        payment.confirm_payment(result['ref_id'])
        appointment = Appointment.get_by_id(payment.appointment_id)
        appointment.confirm()
        
        await query.message.edit_text(
            "✅ پرداخت با موفقیت انجام شد!\n\n"
            f"🔵 شماره پیگیری: {result['ref_id']}\n"
            f"💰 مبلغ: {format_price(payment.amount)}\n"
            f"📅 تاریخ: {get_persian_date(payment.created_at)}\n\n"
            "نوبت شما تأیید شد و در سیستم ثبت گردید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 مشاهده نوبت‌ها", callback_data="appointments")
            ]])
        )
    else:
        await query.message.edit_text(
            "❌ پرداخت تأیید نشد!\n"
            "لطفاً مجدداً تلاش کنید یا روش پرداخت دیگری را انتخاب کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 تلاش مجدد", callback_data=f"pay_{payment.appointment_id}")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="appointments")]
            ])
        )

async def process_cash_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cash payment"""
    query = update.callback_query
    await query.answer()
    
    appointment_id = int(query.data.split('_')[1])
    appointment = Appointment.get_by_id(appointment_id)
    service = Service.get_by_id(appointment.service_id)
    
    payment = Payment.create(
        appointment_id=appointment_id,
        amount=service.price,
        payment_type='cash'
    )
    
    await query.message.edit_text(
        "✅ انتخاب پرداخت حضوری ثبت شد\n\n"
        f"💰 مبلغ قابل پرداخت: {format_price(service.price)}\n"
        "لطفاً در روز نوبت، مبلغ را به صورت نقدی پرداخت نمایید.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت به نوبت‌ها", callback_data="appointments")
        ]])
    )

async def show_payment_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show payment history"""
    query = update.callback_query
    await query.answer()
    
    user = User.get_by_telegram_id(update.effective_user.id)
    payments = Payment.get_user_payments(user.id)
    
    if not payments:
        await query.message.edit_text(
            "📝 تاریخچه پرداخت‌های شما خالی است!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="profile")
            ]])
        )
        return
    
    text = "📝 تاریخچه پرداخت‌های شما:\n\n"
    
    for payment in payments:
        appointment = Appointment.get_by_id(payment.appointment_id)
        service = Service.get_by_id(appointment.service_id)
        
        text += f"💇‍♀️ {service.name}\n"
        text += f"💰 مبلغ: {format_price(payment.amount)}\n"
        text += f"📅 تاریخ: {get_persian_date(payment.created_at)}\n"
        text += f"🔵 وضعیت: {get_payment_status_text(payment.status)}\n"
        if payment.transaction_id:
            text += f"🔢 شماره پیگیری: {payment.transaction_id}\n"
        text += "─────────────\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="profile")]]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def get_payment_status_text(status):
    """Convert payment status to Persian text"""
    return {
        'pending': 'در انتظار پرداخت',
        'completed': 'پرداخت شده',
        'failed': 'ناموفق',
        'cancelled': 'لغو شده'
    }.get(status, 'نامشخص')
