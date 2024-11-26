from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
from bot.handlers import start, appointment, profile, payment, chat, admin
from bot.handlers.registration import get_registration_handler
from bot.config import BOT_TOKEN
import logging
from sys import exit
from telegram.ext import Application
from telegram.ext import ApplicationBuilder
from bot.handlers.profile import get_profile_handlers

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .connect_timeout(30)  # Increase timeout to 30 seconds
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add registration handler
    application.add_handler(get_registration_handler())
    
    # Add other handlers
    application.add_handler(CommandHandler("help", start.help_command))
    application.add_handler(CommandHandler("admin", admin.admin_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat.handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, chat.handle_photo))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(appointment.show_services, pattern="^services$"))
    application.add_handler(CallbackQueryHandler(appointment.select_date, pattern="^book_"))
    application.add_handler(CallbackQueryHandler(appointment.select_time, pattern="^date_"))
    application.add_handler(CallbackQueryHandler(appointment.confirm_booking, pattern="^time_"))
    application.add_handler(CallbackQueryHandler(profile.show_profile, pattern="^profile$"))
    application.add_handler(CallbackQueryHandler(profile.show_appointments, pattern="^appointments$"))
    application.add_handler(CallbackQueryHandler(profile.cancel_appointment, pattern="^cancel_"))
    application.add_handler(CallbackQueryHandler(payment.process_payment, pattern="^pay_"))
    application.add_handler(CallbackQueryHandler(payment.verify_payment, pattern="^verify_"))
    application.add_handler(CallbackQueryHandler(admin.handle_admin, pattern="^admin_"))
    profile_handlers = get_profile_handlers()
    for handler in profile_handlers:
        application.add_handler(handler)
    # Start the bot
    print("Bot started successfully! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped gracefully!")
        exit(0)
