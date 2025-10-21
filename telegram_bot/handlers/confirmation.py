from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import logging
from config import config
from models.booking import Booking
from services.booking_service import booking_service
from services.notification import notification_service
from keyboards import (
    get_booking_actions_keyboard, 
    get_bookings_list_keyboard,
    get_back_to_menu_keyboard
)

# Настройка логирования
logger = logging.getLogger(__name__)

async def show_pending_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает список броней ожидающих подтверждения
    Это основная функция которую видят менеджеры
    """
    # Показываем сообщение о загрузке
    await update.message.reply_text(
        "🔄 Загружаю список броней...",
        reply_markup=get_back_to_menu_keyboard()
    )
    
    # Получаем брони через сервис
    bookings = await booking_service.get_pending_bookings()
    
    if not bookings:
        # Если нет броней - сообщаем об этом
        await update.message.reply_text(
            "✅ На данный момент нет броней, ожидающих подтверждения.",
            reply_markup=get_back_to_menu_keyboard()
        )
        return
    
    # Сохраняем брони и текущую страницу в контексте пользователя
    # Это нужно для работы пагинации
    context.user_data['current_bookings'] = bookings
    context.user_data['current_page'] = 0
    
    # Формируем текст сообщения
    message_text = f"📋 <b>Брони на подтверждение</b>\n\nНайдено броней: {len(bookings)}"
    
    # Отправляем сообщение со списком броней
    await update.message.reply_text(
        message_text,
        reply_markup=get_bookings_list_keyboard(bookings, 0),
        parse_mode='HTML'
    )

async def show_booking_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает детальную информацию о конкретной брони
    Вызывается когда пользователь нажимает на бронь в списке
    """
    query = update.callback_query
    await query.answer()  # Ответить на callback чтобы убрать "часики" в кнопке
    
    # Извлекаем ID брони из callback_data (формат: "booking_123")
    booking_id = int(query.data.split('_')[1])
    
    # Получаем брони из контекста (из ранее загруженного списка)
    bookings = context.user_data.get('current_bookings', [])
    
    # Ищем нужную бронь в загруженном списке
    booking = next((b for b in bookings if b.id == booking_id), None)
    
    if not booking:
        # Если бронь не найдена в кеше - запрашиваем из API
        booking = await booking_service.api_client.get_booking_by_id(booking_id)
    
    if not booking:
        # Если бронь вообще не найдена - показываем ошибку
        await query.edit_message_text("❌ Бронь не найдена или была удалена")
        return
    
    # Форматируем детальную информацию о брони
    detailed_info = f"📋 <b>Детали брони #{booking.id}</b>\n{booking.formatted_info}"
    
    # Редактируем существующее сообщение (со списком) чтобы показать детали
    await query.edit_message_text(
        detailed_info,
        reply_markup=get_booking_actions_keyboard(booking.id),
        parse_mode='HTML'
    )

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Подтверждает бронирование
    Вызывается когда менеджер нажимает "✅ Подтвердить"
    """
    query = update.callback_query
    await query.answer()
    
    # Извлекаем ID брони
    booking_id = int(query.data.split('_')[1])
    user = query.from_user
    
    # Получаем информацию о брони для уведомлений
    booking = await booking_service.api_client.get_booking_by_id(booking_id)
    
    if not booking:
        await query.edit_message_text("❌ Бронь не найдена")
        return
    
    # Формируем информацию о том кто подтвердил
    confirmed_by = f"@{user.username}" if user.username else user.first_name
    
    # Подтверждаем бронь через сервис
    success = await booking_service.confirm_booking(booking_id, confirmed_by)
    
    if success:
        # Если успешно - отправляем уведомление клиенту
        await notification_service.notify_booking_confirmed(booking, confirmed_by)
        
        success_text = f"✅ Бронь #{booking_id} успешно подтверждена!"
    else:
        success_text = "❌ Ошибка при подтверждении брони. Попробуйте позже."
    
    # Показываем результат пользователю
    await query.edit_message_text(success_text)
    
    # Показываем обновленный список броней
    await show_pending_bookings_from_query(query, context)

async def start_reject_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начинает процесс отклонения брони
    Переводит бота в состояние ожидания причины отклонения
    """
    query = update.callback_query
    await query.answer()
    
    # Извлекаем ID брони
    booking_id = int(query.data.split('_')[1])
    
    # Сохраняем ID брони в контексте пользователя
    # Это нужно чтобы в следующем шаге знать какую бронь отклоняем
    context.user_data['rejecting_booking_id'] = booking_id
    
    # Запрашиваем причину отклонения
    rejection_prompt = """
📝 <b>Укажите причину отклонения брони:</b>

Пожалуйста, напишите причину отклонения, которая будет отправлена клиенту.
    """
    
    await query.edit_message_text(
        rejection_prompt,
        parse_mode='HTML'
    )
    
    # Переводим бота в состояние ожидания причины
    return config.States.WAITING_REJECT_REASON

async def process_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает причину отклонения и отклоняет бронь
    Вызывается после того как пользователь отправил текст с причиной
    """
    rejection_reason = update.message.text
    booking_id = context.user_data.get('rejecting_booking_id')
    user = update.effective_user
    
    # Проверяем что у нас есть ID брони
    if not booking_id:
        await update.message.reply_text("❌ Ошибка: бронь не найдена")
        return ConversationHandler.END
    
    # Получаем информацию о брони для уведомлений
    booking = await booking_service.api_client.get_booking_by_id(booking_id)
    
    if not booking:
        await update.message.reply_text("❌ Бронь не найдена")
        return ConversationHandler.END
    
    # Формируем информацию о том кто отклонил
    rejected_by = f"@{user.username}" if user.username else user.first_name
    
    # Отклоняем бронь через сервис
    success = await booking_service.reject_booking(
        booking_id,
        rejection_reason,
        rejected_by
    )
    
    if success:
        # Если успешно - отправляем уведомление клиенту
        await notification_service.notify_booking_rejected(booking, rejected_by, rejection_reason)
        
        result_text = f"❌ Бронь #{booking_id} отклонена.\n<b>Причина:</b> {rejection_reason}"
    else:
        result_text = "❌ Ошибка при отклонении брони. Попробуйте позже."
    
    # Показываем результат пользователю
    await update.message.reply_text(result_text, parse_mode='HTML')
    
    # Очищаем контекст
    context.user_data.pop('rejecting_booking_id', None)
    
    # Показываем обновленный список броней
    await show_pending_bookings(update, context)
    
    # Завершаем Conversation
    return ConversationHandler.END

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает перелистывание страниц в списке броней
    """
    query = update.callback_query
    await query.answer()
    
    # Извлекаем номер страницы из callback_data (формат: "page_2")
    page_number = int(query.data.split('_')[1])
    
    # Получаем сохраненные брони из контекста
    bookings = context.user_data.get('current_bookings', [])
    
    # Обновляем текущую страницу в контексте
    context.user_data['current_page'] = page_number
    
    # Формируем текст сообщения
    message_text = f"📋 <b>Брони на подтверждение</b>\n\nНайдено броней: {len(bookings)}"
    
    # Обновляем сообщение с новой страницей
    await query.edit_message_text(
        message_text,
        reply_markup=get_bookings_list_keyboard(bookings, page_number),
        parse_mode='HTML'
    )

async def refresh_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обновляет список броней (перезагружает из API)
    """
    query = update.callback_query
    await query.answer("🔄 Обновляю...")  # Показываем всплывающее уведомление
    
    # Перезагружаем и показываем список
    await show_pending_bookings_from_query(query, context)

async def show_pending_bookings_from_query(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Вспомогательная функция для показа списка броней из callback query
    Используется когда нужно обновить список после действий с бронью
    """
    # Загружаем актуальный список броней
    bookings = await booking_service.get_pending_bookings()
    
    if not bookings:
        # Если нет броней - сообщаем об этом
        await query.edit_message_text(
            "✅ На данный момент нет броней, ожидающих подтверждения."
        )
        return
    
    # Сохраняем брони в контексте
    context.user_data['current_bookings'] = bookings
    context.user_data['current_page'] = 0
    
    # Формируем текст сообщения
    message_text = f"📋 <b>Брони на подтверждение</b>\n\nНайдено броней: {len(bookings)}"
    
    # Обновляем сообщение
    await query.edit_message_text(
        message_text,
        reply_markup=get_bookings_list_keyboard(bookings, 0),
        parse_mode='HTML'
    )

async def cancel_rejection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отменяет процесс отклонения брони
    Используется как fallback в ConversationHandler
    """
    # Очищаем контекст
    context.user_data.pop('rejecting_booking_id', None)
    
    await update.message.reply_text(
        "❌ Отклонение брони отменено.",
        reply_markup=get_back_to_menu_keyboard()
    )
    
    # Завершаем Conversation
    return ConversationHandler.END
