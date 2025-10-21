from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import logging
from config import States
from services.booking_service import booking_service
from services.notification import notification_service
from keyboards import get_main_menu_keyboard, get_back_to_menu_keyboard

logger = logging.getLogger(__name__)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает отправку контактных данных и создает бронь
    """
    user = update.effective_user
    contact = update.message.contact
    
    if not contact:
        await update.message.reply_text(
            "Пожалуйста, отправьте контакт используя кнопку ниже 📱",
            reply_markup=get_back_to_menu_keyboard()
        )
        return States.WAITING_CONTACT
    
    plot_id = context.user_data.get('booking_plot_id')
    
    if not plot_id:
        await update.message.reply_text(
            "❌ Ошибка: участок не найден",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    # Собираем данные пользователя
    user_data = {
        'user_id': user.id,
        'name': user.first_name,
        'phone': contact.phone_number,
        'email': f"{user.username}@telegram" if user.username else "not_provided@telegram"
    }
    
    # Создаем бронирование
    await update.message.reply_text("🔄 Создаю бронирование...")
    
    booking = await booking_service.create_booking(plot_id, user_data)
    
    if booking:
        # Отправляем уведомление
        await notification_service.notify_booking_created(booking)
        
        success_text = f"""
🎉 <b>Бронирование создано успешно!</b>

📋 <b>Номер брони:</b> #{booking.id}
🏞 <b>Участок:</b> {booking.plot_title}
💰 <b>Цена:</b> {booking.plot_price:,} руб.

⏳ <b>Статус:</b> Ожидает подтверждения менеджером

Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.

Вы можете отслеживать статус брони в разделе "📋 Мои брони"
        """
        
        await update.message.reply_text(
            success_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode='HTML'
        )
        
        # Логируем успешное создание брони
        logger.info(f"✅ Booking {booking.id} created for user {user.id}")
        
    else:
        error_text = """
❌ <b>Не удалось создать бронирование</b>

Пожалуйста, попробуйте позже или свяжитесь с нами по телефону:

📞 +7 (999) 123-45-67
        """
        
        await update.message.reply_text(
            error_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode='HTML'
        )
    
    # Очищаем контекст
    context.user_data.pop('booking_plot_id', None)
    
    return ConversationHandler.END

async def cancel_booking_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отменяет процесс бронирования
    """
    # Очищаем контекст
    context.user_data.pop('booking_plot_id', None)
    
    await update.message.reply_text(
        "❌ Бронирование отменено",
        reply_markup=get_main_menu_keyboard()
    )
    
    return ConversationHandler.END
