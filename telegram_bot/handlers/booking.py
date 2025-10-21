from telegram import Update
from telegram.ext import ContextTypes
import logging
from services.booking_service import booking_service
from services.notification import notification_service
from keyboards import get_bookings_keyboard, get_booking_detail_keyboard, get_confirmation_keyboard, get_back_to_menu_keyboard

logger = logging.getLogger(__name__)

async def show_user_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает бронирования пользователя
    """
    user = update.effective_user
    
    await update.message.reply_text(
        "🔄 Загружаю ваши бронирования...",
        reply_markup=get_back_to_menu_keyboard()
    )
    
    bookings = await booking_service.get_user_bookings(user.id)
    
    if not bookings:
        await update.message.reply_text(
            "📭 У вас пока нет бронирований.\n\n"
            "Перейдите в каталог участков чтобы сделать первую бронь! 🏞",
            reply_markup=get_back_to_menu_keyboard()
        )
        return
    
    context.user_data['current_bookings'] = bookings
    context.user_data['current_bookings_page'] = 0
    
    message_text = f"📋 <b>Ваши бронирования</b>\n\nНайдено броней: {len(bookings)}"
    
    await update.message.reply_text(
        message_text,
        reply_markup=get_bookings_keyboard(bookings, 0),
        parse_mode='HTML'
    )

async def show_booking_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает детальную информацию о брони
    """
    query = update.callback_query
    await query.answer()
    
    booking_id = int(query.data.split('_')[1])
    
    # Получаем брони из контекста
    bookings = context.user_data.get('current_bookings', [])
    booking = next((b for b in bookings if b.id == booking_id), None)
    
    if not booking:
        await query.edit_message_text("❌ Бронь не найдена")
        return
    
    detailed_info = booking.formatted_info
    
    # Показываем кнопку отмены только для pending броней
    if booking.status == 'pending':
        await query.edit_message_text(
            detailed_info,
            reply_markup=get_booking_detail_keyboard(booking.id),
            parse_mode='HTML'
        )
    else:
        await query.edit_message_text(
            detailed_info,
            parse_mode='HTML'
        )

async def start_cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Начинает процесс отмены брони
    """
    query = update.callback_query
    await query.answer()
    
    booking_id = int(query.data.split('_')[2])
    
    # Сохраняем ID брони для отмены
    context.user_data['cancelling_booking_id'] = booking_id
    
    confirmation_text = """
🚫 <b>Отмена бронирования</b>

Вы уверены что хотите отменить эту бронь?

После отмены вы сможете забронировать этот участок снова, 
если он будет еще доступен.
    """
    
    await query.edit_message_text(
        confirmation_text,
        reply_markup=get_confirmation_keyboard(),
        parse_mode='HTML'
    )

async def confirm_cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Подтверждает отмену брони
    """
    query = update.callback_query
    await query.answer()
    
    booking_id = context.user_data.get('cancelling_booking_id')
    user = query.from_user
    
    if not booking_id:
        await query.edit_message_text("❌ Ошибка: бронь не найдена")
        return
    
    # Отменяем бронь
    success = await booking_service.cancel_booking(booking_id)
    
    if success:
        # Получаем информацию о брони для уведомления
        bookings = context.user_data.get('current_bookings', [])
        booking = next((b for b in bookings if b.id == booking_id), None)
        
        if booking:
            await notification_service.notify_booking_cancelled(booking)
        
        success_text = f"✅ Бронь #{booking_id} успешно отменена!"
    else:
        success_text = "❌ Ошибка при отмене брони. Попробуйте позже."
    
    await query.edit_message_text(success_text)
    
    # Очищаем контекст
    context.user_data.pop('cancelling_booking_id', None)
    
    # Показываем обновленный список броней
    await show_user_bookings_from_query(query, context)

async def handle_bookings_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает перелистывание страниц в списке броней
    """
    query = update.callback_query
    await query.answer()
    
    page = int(query.data.split('_')[2])
    bookings = context.user_data.get('current_bookings', [])
    
    context.user_data['current_bookings_page'] = page
    
    message_text = f"📋 <b>Ваши бронирования</b>\n\nНайдено броней: {len(bookings)}"
    
    await query.edit_message_text(
        message_text,
        reply_markup=get_bookings_keyboard(bookings, page),
        parse_mode='HTML'
    )

async def refresh_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обновляет список броней
    """
    query = update.callback_query
    await query.answer("🔄 Обновляю...")
    
    await show_user_bookings_from_query(query, context)

async def show_user_bookings_from_query(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Вспомогательная функция для показа броней из callback query
    """
    user = query.from_user
    bookings = await booking_service.get_user_bookings(user.id)
    
    if not bookings:
        await query.edit_message_text(
            "📭 У вас пока нет бронирований."
        )
        return
    
    context.user_data['current_bookings'] = bookings
    context.user_data['current_bookings_page'] = 0
    
    message_text = f"📋 <b>Ваши бронирования</b>\n\nНайдено броней: {len(bookings)}"
    
    await query.edit_message_text(
        message_text,
        reply_markup=get_bookings_keyboard(bookings, 0),
        parse_mode='HTML'
    )

async def back_to_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Возвращает к списку броней
    """
    query = update.callback_query
    await query.answer()
    
    await show_user_bookings_from_query(query, context)
