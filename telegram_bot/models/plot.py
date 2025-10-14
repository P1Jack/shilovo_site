from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Plot:
    """Модель земельного участка"""
    
    id: int
    title: str
    price: float
    area: str
    location: str
    description: str
    status: str  # available, booked, sold
    images: List[str]
    features: List[str]
    
    @property
    def formatted_info(self) -> str:
        """Форматирует информацию об участке"""
        text = f"""
🏞 <b>{self.title}</b>

💰 <b>Цена:</b> {self.price:,.0f} руб.
📏 <b>Площадь:</b> {self.area}
📍 <b>Местоположение:</b> {self.location}

📝 <b>Описание:</b>
{self.description}
        """
        
        if self.features:
            text += f"\n⚡ <b>Особенности:</b>\n" + "\n".join([f"• {feature}" for feature in self.features])
        
        text += f"\n\n<b>Статус:</b> {self.get_status_emoji()} {self.status.title()}"
        
        return text.strip()
    
    def get_status_emoji(self) -> str:
        """Возвращает эмодзи статуса"""
        emoji_map = {
            'available': '✅',
            'booked': '⏳',
            'sold': '🏁'
        }
        return emoji_map.get(self.status, '📝')
    
    @property
    def is_available(self) -> bool:
        """Проверяет, доступен ли участок для бронирования"""
        return self.status == 'available'
