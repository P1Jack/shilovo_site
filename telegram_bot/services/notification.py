import logging
from typing import Optional
from models.booking import Booking
from models.plot import Plot

logger = logging.getLogger(__name__)

class NotificationService:
    """Сервис уведомлений для покупателя"""
    
    def __init__(self):
        self.logger = logger
    
    async def notify_booking_created(self, booking: Booking) -> bool:
        """Уведомляет покупателя о создании брони"""
        try:
            self.logger.info(f"📋 Booking {booking.id} created for user")
            
            # Заглушка для демонстрации
            print(f"""
📧 УВЕДОМЛЕНИЕ ПОКУПАТЕЛЮ:
Бронь #{booking.id} создана успешно!

Участок: {booking.plot_title}
Цена: {booking.plot_price} руб.
Статус: {booking.status}

Ожидайте подтверждения от менеджера.
            """)
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending booking notification: {e}")
            return False
    
    async def notify_booking_confirmed(self, booking: Booking) -> bool:
        """Уведомляет покупателя о подтверждении брони"""
        try:
            self.logger.info(f"✅ Booking {booking.id} confirmed")
            
            print(f"""
🎉 УВЕДОМЛЕНИЕ ПОКУПАТЕЛЮ:
Бронь #{booking.id} подтверждена!

Участок: {booking.plot_title} 
Цена: {booking.plot_price} руб.

Свяжитесь с менеджером для оформления документов.
            """)
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending confirmation notification: {e}")
            return False
    
    async def notify_booking_cancelled(self, booking: Booking) -> bool:
        """Уведомляет покупателя об отмене брони"""
        try:
            self.logger.info(f"🚫 Booking {booking.id} cancelled")
            
            print(f"""
📝 УВЕДОМЛЕНИЕ ПОКУПАТЕЛЮ:
Бронь #{booking.id} отменена.

Участок: {booking.plot_title}
            """)
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending cancellation notification: {e}")
            return False
    
    async def notify_new_plots_available(self, plots: list, user_ids: list) -> bool:
        """Уведомляет покупателей о новых участках"""
        try:
            self.logger.info(f"🔔 Notifying about {len(plots)} new plots")
            
            for plot in plots:
                print(f"""
🏞 НОВЫЙ УЧАСТОК ДОСТУПЕН:
{plot.title}
Цена: {plot.price} руб.
Местоположение: {plot.location}
                """)
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending new plots notification: {e}")
            return False

# Глобальный экземпляр сервиса уведомлений
notification_service = NotificationService()
