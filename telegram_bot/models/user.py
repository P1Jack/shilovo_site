from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """Модель пользователя Telegram (покупателя)"""
    
    id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    
    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property 
    def mention(self) -> str:
        """Возвращает упоминание пользователя для Telegram"""
        if self.username:
            return f"@{self.username}"
        return self.full_name

    @classmethod
    def from_telegram_user(cls, telegram_user):
        """Создает объект User из объекта пользователя Telegram"""
        return cls(
            id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name
        )
