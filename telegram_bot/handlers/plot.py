from telegram import Update
from telegram.ext import ContextTypes
import logging
from services.booking_service import booking_service
from keyboards import get_plots_keyboard, get_plot_detail_keyboard, get_back_to_menu_keyboard

logger = logging.getLogger(__name__)

async def show_plots_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает каталог доступных участков
    """
    await update.message.reply_text(
        "🔄 Загружаю каталог участков...",
        reply_markup=get_back_to_menu_keyboard()
    )
    
    plots = await booking_service.get_available_plots()
    
    if not plots:
        await update.message.reply_text(
            "😔 На данный момент нет доступных участков.\n\n"
            "Попробуйте позже или свяжитесь с нами для уточнения информации.",
            reply_markup=get_back_to_menu_keyboard()
        )
        return
    
    context.user_data['current_plots'] = plots
    context.user_data['current_plots_page'] = 0
    
    message_text = f"🏞 <b>Каталог участков</b>\n\nНайдено участков: {len(plots)}"
    
    await update.message.reply_text(
        message_text,
        reply_markup=get_plots_keyboard(plots, 0),
        parse_mode='HTML'
    )

async def show_plot_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает детальную информацию об участке
    """
    query = update.callback_query
    await query.answer()
    
    plot_id = int(query.data.split('_')[1])
    
    # Ищем участок в кеше или загружаем из API
    plots = context.user_data.get('current_plots', [])
    plot = next((p for p in plots if p.id == plot_id), None)
    
    if not plot:
        plot = await booking_service.get_plot_detail(plot_id)
    
    if not plot:
        await query.edit_message_text("❌ Участок не найден")
        return
    
    detailed_info = plot.formatted_info
    
    await query.edit_message_text(
        detailed_info,
        reply_markup=get_plot_detail_keyboard(plot.id),
        parse_mode='HTML'
    )

async def start_booking_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Начинает процесс бронирования участка
    """
    query = update.callback_query
    await query.answer()
    
    plot_id = int(query.data.split('_')[1])
    
    # Сохраняем ID участка для бронирования
    context.user_data['booking_plot_id'] = plot_id
    
    # Получаем информацию об участке
    plot = await booking_service.get_plot_detail(plot_id)
    
    if not plot:
        await query.edit_message_text("❌ Участок не найден")
        return
    
    if not plot.is_available:
        await query.edit_message_text("😔 Этот участок больше не доступен для бронирования")
        return
    
    booking_text = f"""
📋 <b>Бронирование участка</b>

🏞 <b>Участок:</b> {plot.title}
💰 <b>Цена:</b> {plot.price:,} руб.
📏 <b>Площадь:</b> {plot.area}
📍 <b>Местоположение:</b> {plot.location}

Для завершения бронирования отправьте свои контактные данные.

Нажмите кнопку ниже чтобы отправить телефон:
    """
    
    from keyboards import get_contact_keyboard
    await query.edit_message_text(
        booking_text,
        reply_markup=get_contact_keyboard(),
        parse_mode='HTML'
    )

async def handle_plots_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает перелистывание страниц в каталоге участков
    """
    query = update.callback_query
    await query.answer()
    
    page = int(query.data.split('_')[2])
    plots = context.user_data.get('current_plots', [])
    
    context.user_data['current_plots_page'] = page
    
    message_text = f"🏞 <b>Каталог участков</b>\n\nНайдено участков: {len(plots)}"
    
    await query.edit_message_text(
        message_text,
        reply_markup=get_plots_keyboard(plots, page),
        parse_mode='HTML'
    )

async def refresh_plots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обновляет список участков
    """
    query = update.callback_query
    await query.answer("🔄 Обновляю...")
    
    await show_plots_catalog_from_query(query, context)

async def show_plots_catalog_from_query(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Вспомогательная функция для показа каталога из callback query
    """
    plots = await booking_service.get_available_plots()
    
    if not plots:
        await query.edit_message_text(
            "😔 На данный момент нет доступных участков."
        )
        return
    
    context.user_data['current_plots'] = plots
    context.user_data['current_plots_page'] = 0
    
    message_text = f"🏞 <b>Каталог участков</b>\n\nНайдено участков: {len(plots)}"
    
    await query.edit_message_text(
        message_text,
        reply_markup=get_plots_keyboard(plots, 0),
        parse_mode='HTML'
    )

async def back_to_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Возвращает к каталогу участков
    """
    query = update.callback_query
    await query.answer()
    
    await show_plots_catalog_from_query(query, context)
