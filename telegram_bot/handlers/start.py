from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_menu_keyboard
from models.user import User
from config import get_moscow_time

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает команду /start - приветствие покупателя
    """
    user = update.effective_user
    telegram_user = User.from_telegram_user(user)
    
    # Сохраняем информацию о пользователе в контексте
    context.user_data['user_info'] = {
        'id': telegram_user.id,
        'name': telegram_user.full_name,
        'username': telegram_user.username
    }
    
    welcome_text = f"""
👋 Привет, {telegram_user.first_name}!

<b>LandBooking Bot</b> - поможет тебе найти и забронировать идеальный земельный участок!

🏞 <b>Что я умею:</b>
• Показать каталог доступных участков
• Забронировать понравившийся участок
• Показать твои текущие бронирования
• Ответить на вопросы

Выбери действие в меню ниже 👇
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает команду /help - справка для покупателя
    """
    help_text = """
🆘 <b>Как пользоваться ботом:</b>

1. <b>🏞 Каталог участков</b> - просмотри все доступные участки
2. <b>📋 Мои брони</b> - посмотри свои текущие бронирования
3. <b>📞 Контакты</b> - свяжись с нами для консультации

<b>Процесс бронирования:</b>
1. Выбери участок из каталога
2. Нажми "Забронировать"
3. Укажи свои контактные данные
4. Подтверди бронирование

<b>Статусы броней:</b>
⏳ <b>pending</b> - ожидает подтверждения менеджером
✅ <b>confirmed</b> - подтверждена менеджером
❌ <b>rejected</b> - отклонена менеджером
🏁 <b>completed</b> - сделка завершена
🚫 <b>cancelled</b> - отменена

<b>Нужна помощь?</b>
📞 +7 (999) 123-45-67
📧 support@land-site.ru
    """
    
    await update.message.reply_text(help_text, parse_mode='HTML')

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает нажатия кнопок главного меню
    """
    user_message = update.message.text
    
    if user_message == "🏞 Каталог участков":
        from handlers.plots import show_plots_catalog
        await show_plots_catalog(update, context)
        
    elif user_message == "📋 Мои брони":
        from handlers.bookings import show_user_bookings
        await show_user_bookings(update, context)
        
    elif user_message == "📞 Контакты":
        await contacts_command(update, context)
        
    elif user_message == "🆘 Помощь":
        await help_command(update, context)
        
    elif user_message == "↩️ В главное меню":
        await start_command(update, context)
        
    else:
        await update.message.reply_text(
            "Используй кнопки меню для навигации 🗺",
            reply_markup=get_main_menu_keyboard()
        )

async def contacts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает контактную информацию
    """
    contacts_text = """
🏢 <b>Наши контакты</b>

📞 <b>Телефон для консультаций:</b> +7 (999) 123-45-67
📧 <b>Email:</b> info@land-site.ru
🌐 <b>Сайт:</b> www.land-site.ru

📍 <b>Адрес офиса:</b>
Москва, ул. Примерная, д. 123
(метро "Примерная")

⏰ <b>Время работы:</b>
Пн-Пт: 9:00-18:00
Сб: 10:00-16:00
Вс: выходной

🚗 <b>Как добраться:</b>
На машине: парковка у офиса
На метро: 5 минут от станции

<b>Мы всегда рады помочь вам с выбором участка!</b> 😊
    """
    
    await update.message.reply_text(
        contacts_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )

async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает неизвестные сообщения
    """
    await update.message.reply_text(
        "Я понимаю только команды из меню 😊\n\n"
        "Используй кнопки ниже для навигации:",
        reply_markup=get_main_menu_keyboard()
    )
