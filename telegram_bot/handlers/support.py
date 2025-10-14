from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_menu_keyboard

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает запросы в техническую поддержку
    """
    support_text = """
🆘 <b>Техническая поддержка</b>

Если у вас возникли проблемы с работой бота:

<b>Для срочных вопросов:</b>
📞 Телефон: +7 (999) 123-45-69
📧 Email: support@land-site.ru

<b>Что указать в обращении:</b>
• Ваше имя и контакты
• Суть проблемы
• Когда произошла ошибка

<b>Время ответа:</b>
• По телефону: сразу в рабочее время
• По email: в течение 2 часов
    """
    
    await update.message.reply_text(
        support_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )

async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показывает ответы на часто задаваемые вопросы
    """
    faq_text = """
❓ <b>Часто задаваемые вопросы</b>

<b>Q: Как долго бронь сохраняется за мной?</b>
A: Бронь сохраняется 24 часа с момента создания.

<b>Q: Что делать если я передумал?</b>
A: Вы можете отменить бронь в разделе "Мои брони".

<b>Q: Сколько участков я могу забронировать?</b>
A: Одновременно вы можете иметь только одну активную бронь.

<b>Q: Что делать после подтверждения брони?</b>
A: Наш менеджер свяжется с вами для оформления документов.

<b>Q: Можно ли изменить данные в брони?</b>
A: Для изменения данных свяжитесь с менеджером.

<b>Q: Что если участок уже забронирован?</b>
A: В каталоге отображаются только доступные участки.
    """
    
    await update.message.reply_text(
        faq_text,
        parse_mode='HTML'
    )

async def send_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает отправку обратной связи
    """
    feedback_text = """
💡 <b>Обратная связь и предложения</b>

Мы будем рады вашим предложениям по улучшению сервиса!

<b>Что можно предложить:</b>
• Новые функции для бота
• Улучшение интерфейса
• Исправление неудобств

<b>Куда отправлять предложения:</b>
📧 Email: product@land-site.ru

<b>Спасибо за вашу обратную связь! 🚀</b>
    """
    
    await update.message.reply_text(
        feedback_text,
        parse_mode='HTML'
    )
