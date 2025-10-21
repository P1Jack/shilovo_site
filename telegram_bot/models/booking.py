from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from config import get_moscow_time

@dataclass
class Booking:
    """Модель бронирования участка для покупателя"""
    
    id: int
    plot_id: int
    plot_title: str
    plot_price: float
    plot_area: str
    plot_location: str
    status: str
    created_at: str
    expires_at: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        """Проверяет, истекло ли время бронирования"""
        if not self.expires_at:
            return False
            
        try:
            expires_datetime = datetime.fromisoformat(
                self.expires_at.replace('Z', '+00:00')
            )
            current_time = datetime.now(expires_datetime.tzinfo)
            return current_time > expires_datetime
        except:
            return False
    
    @property
    def formatted_info(self) -> str:
        """Форматирует информацию о брони для покупателя"""
        status_emoji = self.get_status_emoji()
        
        text = f"""
📋 <b>Бронь #{self.id}</b>

🏞 <b>Участок:</b> {self.plot_title}
💰 <b>Цена:</b> {self.plot_price:,.0f} руб.
📏 <b>Площадь:</b> {self.plot_area}
📍 <b>Местоположение:</b> {self.plot_location}

🕐 <b>Создана:</b> {self.format_date(self.created_at)}
        """
        
        if self.expires_at:
            text += f"\n⏰ <b>Истекает:</b> {self.format_date(self.expires_at)}"
        
        text += f"\n\n<b>Статус:</b> {status_emoji} {self.status.title()}"
        
        return text.strip()
    
    def get_status_emoji(self) -> str:
        """Возвращает эмодзи статуса"""
        emoji_map = {
            'pending': '⏳',
            'confirmed': '✅',
            'rejected': '❌',
            'completed': '🏁',
            'cancelled': '🚫'
        }
        return emoji_map.get(self.status, '📝')
    
    @staticmethod
    def format_date(date_string: str) -> str:
        """Форматирует дату в московском времени"""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            moscow_dt = dt.astimezone(pytz.timezone('Europe/Moscow'))
            return moscow_dt.strftime('%d.%m.%Y %H:%M')
        except:
            return date_string
