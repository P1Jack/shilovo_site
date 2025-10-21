import logging
import asyncio
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from config import config, States
from handlers.start import start_command, help_command, menu_handler, contacts_command, handle_unknown_message
from handlers.plot import (
    show_plot_detail, 
    start_booking_process,
    handle_plots_pagination,
    refresh_plots,
    back_to_catalog
)
from handlers.booking import (
    show_booking_detail,
    start_cancel_booking,
    handle_bookings_pagination, 
    refresh_bookings,
    back_to_bookings,
    confirm_cancel_booking
)
from handlers.booking_process import handle_contact, cancel_booking_process
from handlers.support import support_command, faq_command, send_feedback
from handlers.error_handler import global_error_handler
from api_client import api_client

# Настройка логирования с московским временем
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Главная функция запуска бота для покупателя"""
    logger.info("🚀 Запуск бота для покупателей земельных участков...")
    
    # Проверяем переменные окружения
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен в .env файле")
        return
    
    logger.info("✅ Все переменные окружения настроены корректно")
    
    try:
        # Создаем приложение
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Настраиваем обработчики
        setup_handlers(application)
        
        # Добавляем обработчик ошибок
        application.add_error_handler(global_error_handler)
        
        logger.info("✅ Приложение бота успешно создано и настроено")
        logger.info("📡 Запуск polling для получения обновлений...")
        logger.info(f"🔗 Подключение к API: {config.API_BASE_URL}")
        
        # Запускаем бота
        application.run_polling(
            poll_interval=1.0,
            timeout=30,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен по запросу пользователя (Ctrl+C)")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка при запуске бота: {e}")
    finally:
        logger.info("👋 Бот завершил работу")

def setup_handlers(application):
    """Настраивает все обработчики сообщений и команд"""
    
    # 1. ОБРАБОТЧИКИ КОМАНД
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("contacts", contacts_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("faq", faq_command))
    application.add_handler(CommandHandler("feedback", send_feedback))
    
    # 2. CONVERSATION HANDLER для процесса бронирования
    booking_conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_booking_process, pattern="^book_")],
        states={
            States.WAITING_CONTACT: [
                MessageHandler(filters.CONTACT, handle_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cancel_booking_process)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_booking_process),
            MessageHandler(filters.Text(["↩️ Отмена", "↩️ В главное меню"]), cancel_booking_process)
        ],
        name="booking_conversation",
        persistent=False,
        allow_reentry=True,
        per_message=False
    )
    application.add_handler(booking_conversation_handler)
    
    # 3. ОБРАБОТЧИКИ CALLBACK QUERY для участков
    application.add_handler(CallbackQueryHandler(show_plot_detail, pattern="^plot_"))
    application.add_handler(CallbackQueryHandler(handle_plots_pagination, pattern="^plots_page_"))
    application.add_handler(CallbackQueryHandler(refresh_plots, pattern="^refresh_plots$"))
    application.add_handler(CallbackQueryHandler(back_to_catalog, pattern="^back_to_catalog$"))
    
    # 4. ОБРАБОТЧИКИ CALLBACK QUERY для броней
    application.add_handler(CallbackQueryHandler(show_booking_detail, pattern="^booking_"))
    application.add_handler(CallbackQueryHandler(confirm_cancel_booking, pattern="^confirm_yes$"))
    application.add_handler(CallbackQueryHandler(back_to_bookings, pattern="^back_to_bookings$"))
    application.add_handler(CallbackQueryHandler(handle_bookings_pagination, pattern="^bookings_page_"))
    application.add_handler(CallbackQueryHandler(refresh_bookings, pattern="^refresh_bookings$"))
    
    # 5. Отмена брони (отдельный обработчик)
    application.add_handler(CallbackQueryHandler(start_cancel_booking, pattern="^cancel_booking_"))
    
    # 6. Отмена подтверждения
    application.add_handler(CallbackQueryHandler(back_to_bookings, pattern="^confirm_no$"))
    
    # 7. ОБРАБОТЧИКИ ТЕКСТОВЫХ СООБЩЕНИЙ (главное меню)
    application.add_handler(MessageHandler(
        filters.Text([
            "🏞 Каталог участков", 
            "📋 Мои брони",
            "📞 Контакты", 
            "🆘 Помощь",
            "↩️ В главное меню"
        ]),
        menu_handler
    ))
    
    # 8. ОБРАБОТЧИК НЕИЗВЕСТНЫХ СООБЩЕНИЙ
    application.add_handler(MessageHandler(filters.ALL, handle_unknown_message))
    
    logger.info("✅ Все обработчики успешно зарегистрированы")

if __name__ == "__main__":
    main()
