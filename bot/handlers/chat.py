from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters
from ..utils.ai_chat import BeautySalonAI
from ..database.models import User, ChatHistory
from ..keyboards.main_keyboard import get_main_keyboard

QUICK_REPLIES = {
    "خدمات": "برای مشاهده لیست خدمات و قیمت‌ها، از منوی اصلی گزینه «خدمات» را انتخاب کنید.",
    "ساعت کاری": "ساعت کاری سالن از ۹ صبح تا ۹ شب می‌باشد.",
    "آدرس": "آدرس سالن: تهران، خیابان ولیعصر، نرسیده به میدان ونک، پلاک ۱۲۳",
    "رزرو": "برای رزرو نوبت از منوی اصلی گزینه «رزرو نوبت» را انتخاب کنید.",
    "لغو نوبت": "برای لغو نوبت از منوی اصلی وارد بخش «نوبت‌های من» شوید.",
    "قیمت": "برای مشاهده لیست قیمت‌ها، از منوی اصلی گزینه «خدمات» را انتخاب کنید.",
    "مشاوره": "برای دریافت مشاوره تخصصی، می‌توانید سوال خود را مطرح کنید یا با شماره ۰۹۱۲۳۴۵۶۷۸۹ تماس بگیرید.",
    "پرداخت": "پرداخت هزینه خدمات در محل انجام می‌شود. همچنین امکان پرداخت آنلاین نیز وجود دارد.",
}

DEFAULT_RESPONSES = [
    "متوجه نشدم. لطفا واضح‌تر بیان کنید.",
    "می‌توانید سوال خود را به شکل دیگری مطرح کنید؟",
    "برای راهنمایی بیشتر با شماره ۰۹۱۲۳۴۵۶۷۸۹ تماس بگیرید.",
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    user = User.get_by_telegram_id(update.effective_user.id)
    message_text = update.message.text.lower()

    if not user:
        from ..handlers.registration import start_registration
        return await start_registration(update, context)

    await send_typing_action(update, context)

    # Check quick replies
    for keyword, response in QUICK_REPLIES.items():
        if keyword in message_text:
            await save_and_respond(update, user, message_text, response)
            return

    # Use AI for complex responses
    ai = BeautySalonAI()
    response = ai.get_response(message_text)
    await save_and_respond(update, user, message_text, response)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos"""
    user = User.get_by_telegram_id(update.effective_user.id)
    
    if not user:
        from ..handlers.registration import start_registration
        return await start_registration(update, context)

    response = (
        "برای مشاوره با عکس، لطفاً با شماره ۰۹۱۲۳۴۵۶۷۸۹ تماس بگیرید "
        "یا از طریق واتساپ پیام دهید."
    )
    
    await save_and_respond(update, user, "[PHOTO]", response)

async def save_and_respond(update: Update, user, user_message: str, bot_response: str):
    """Save chat history and send response"""
    ChatHistory.add_message(
        user_id=user.id,
        message=user_message,
        is_from_user=True
    )
    
    ChatHistory.add_message(
        user_id=user.id,
        message=bot_response,
        is_from_user=False
    )

    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")],
        [InlineKeyboardButton("❓ سوال دیگری دارم", callback_data="continue_chat")]
    ]
    
    await update.message.reply_text(
        bot_response,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_typing_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send typing action while processing message"""
    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id,
        action="typing"
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to menu button"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "برای ادامه از منوی اصلی استفاده کنید:",
        reply_markup=get_main_keyboard(update.effective_user.id)
    )

async def continue_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle continue chat button"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]]
    await query.edit_message_text(
        "سوال خود را بپرسید. من در خدمت شما هستم! 😊",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def get_chat_handlers():
    """Return all chat related handlers"""
    return [
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
        MessageHandler(filters.PHOTO, handle_photo),
        CallbackQueryHandler(back_to_menu, pattern="^main_menu$"),
        CallbackQueryHandler(continue_chat, pattern="^continue_chat$")
    ]
