from telegram import (
    ReplyKeyboardMarkup, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    KeyboardButton
)
from typing import List
from models.plot import Plot
from models.booking import Booking
from config import config

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота для покупателя"""
    keyboard_layout = [
        ['🏞 Каталог участков'],
        ['📋 Мои брони', '🆘 Помощь'],
        ['📞 Контакты']
    ]
    
    return ReplyKeyboardMarkup(
        keyboard_layout,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

def get_plots_keyboard(plots: List[Plot], page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура со списком участков"""
    buttons = []
    
    start_idx = page * config.PAGE_SIZE
    end_idx = start_idx + config.PAGE_SIZE
    current_page_plots = plots[start_idx:end_idx]
    
    for plot in current_page_plots:
        button_text = f"🏞 {plot.title} - {plot.price:,} руб."
        if len(button_text) > 50:
            button_text = button_text[:47] + "..."
            
        buttons.append([
            InlineKeyboardButton(button_text, callback_data=f"plot_{plot.id}")
        ])
    
    # Кнопки навигации
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"plots_page_{page-1}"))
    
    if end_idx < len(plots):
        navigation_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"plots_page_{page+1}"))
    
    if navigation_buttons:
        buttons.append(navigation_buttons)
    
    buttons.append([InlineKeyboardButton("🔄 Обновить", callback_data="refresh_plots")])
    
    return InlineKeyboardMarkup(buttons)

def get_plot_detail_keyboard(plot_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для деталей участка"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 Забронировать", callback_data=f"book_{plot_id}"),
            InlineKeyboardButton("⭐ В избранное", callback_data=f"fav_{plot_id}")
        ],
        [InlineKeyboardButton("↩️ Назад к каталогу", callback_data="back_to_catalog")]
    ])

def get_bookings_keyboard(bookings: List[Booking], page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура со списком броней пользователя"""
    buttons = []
    
    start_idx = page * config.PAGE_SIZE
    end_idx = start_idx + config.PAGE_SIZE
    current_page_bookings = bookings[start_idx:end_idx]
    
    for booking in current_page_bookings:
        status_emoji = booking.get_status_emoji()
        button_text = f"{status_emoji} Бронь #{booking.id} - {booking.plot_title}"
        if len(button_text) > 50:
            button_text = button_text[:47] + "..."
            
        buttons.append([
            InlineKeyboardButton(button_text, callback_data=f"booking_{booking.id}")
        ])
    
    # Кнопки навигации
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"bookings_page_{page-1}"))
    
    if end_idx < len(bookings):
        navigation_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"bookings_page_{page+1}"))
    
    if navigation_buttons:
        buttons.append(navigation_buttons)
    
    buttons.append([InlineKeyboardButton("🔄 Обновить", callback_data="refresh_bookings")])
    
    return InlineKeyboardMarkup(buttons)

def get_booking_detail_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для деталей брони"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Отменить бронь", callback_data=f"cancel_booking_{booking_id}")],
        [InlineKeyboardButton("↩️ Назад к списку", callback_data="back_to_bookings")]
    ])

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Нет", callback_data="confirm_no")
        ]
    ])

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отправки контакта"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("📱 Отправить контакт", request_contact=True)],
        ['↩️ Отмена']
    ], resize_keyboard=True)

def get_back_to_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой возврата в меню"""
    return ReplyKeyboardMarkup([['↩️ В главное меню']], resize_keyboard=True)
