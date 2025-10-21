import logging
import traceback
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import (
    TelegramError, 
    NetworkError, 
    BadRequest, 
    Forbidden,
    TimedOut
)
from config import get_moscow_time

logger = logging.getLogger(__name__)

async def global_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Глобальный обработчик ошибок
    """
    # Логируем ошибку с московским временем
    error_time = get_moscow_time().strftime('%Y-%m-%d %H:%M:%S')
    logger.error(f"Error at {error_time}:", exc_info=context.error)
    
    # Определяем тип ошибки и формируем сообщение
    user_friendly_message = get_user_friendly_error_message(context.error)
    
    # Отправляем сообщение пользователю
    chat_id = get_chat_id_from_update(update)
    
    if chat_id:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=user_friendly_message
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")
    
    # Логируем детали для отладки
    log_error_details(update, context)

def get_user_friendly_error_message(error: Exception) -> str:
    """
    Преобразует технические ошибки в понятные сообщения
    """
    if isinstance(error, NetworkError):
        return """
🔌 <b>Проблемы с соединением</b>

Не удалось подключиться к серверу. Пожалуйста:
• Проверьте ваше интернет-соединение
• Попробуйте again через несколько минут

Если проблема повторяется, обратитесь в поддержку.
        """
    
    elif isinstance(error, TimedOut):
        return """
⏰ <b>Превышено время ожидания</b>

Сервер не ответил вовремя. Попробуйте повторить запрос через минуту.
        """
    
    elif isinstance(error, BadRequest):
        return """
❌ <b>Некорректный запрос</b>

Произошла ошибка при обработке вашего запроса.
Попробуйте начать заново с команды /start
        """
    
    elif isinstance(error, Forbidden):
        return """
🔒 <b>Нет доступа</b>

Бот не может отправить вам сообщение. 
Пожалуйста, запустите бота командой /start
        """
    
    else:
        return """
😵 <b>Произошла непредвиденная ошибка</b>

Мы уже работаем над устранением проблемы.
Попробуйте повторить действие через несколько минут.

Если ошибка повторяется, обратитесь в поддержку.
        """

def get_chat_id_from_update(update: Update) -> int | None:
    """
    Извлекает chat_id из объекта update
    """
    if update and update.effective_chat:
        return update.effective_chat.id
    
    if update and update.callback_query:
        return update.callback_query.message.chat_id
    
    return None

def log_error_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Логирует дополнительную информацию об ошибке
    """
    error_details = {
        'error_type': type(context.error).__name__,
        'error_message': str(context.error),
        'update_id': update.update_id if update else 'None',
    }
    
    if update and update.effective_user:
        error_details['user_id'] = update.effective_user.id
        error_details['username'] = update.effective_user.username
    
    if update and update.effective_message:
        error_details['message_text'] = update.effective_message.text
        error_details['message_type'] = update.effective_message.content_type
    
    logger.error("Error details: %s", error_details)
