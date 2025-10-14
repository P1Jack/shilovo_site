from typing import List, Optional, Dict, Any
import logging
from models.booking import Booking
from models.plot import Plot
from api_client import api_client

logger = logging.getLogger(__name__)

class BookingService:
    """Сервис для работы с бронированиями (для покупателя)"""
    
    def __init__(self):
        self.api_client = api_client
    
    async def get_available_plots(self, page: int = 1) -> List[Plot]:
        """Получает доступные для бронирования участки"""
        try:
            plots = await self.api_client.get_available_plots(page=page)
            return [plot for plot in plots if plot.is_available]
        except Exception as e:
            logger.error(f"Error getting available plots: {e}")
            return []
    
    async def get_plot_detail(self, plot_id: int) -> Optional[Plot]:
        """Получает детальную информацию об участке"""
        try:
            return await self.api_client.get_plot_detail(plot_id)
        except Exception as e:
            logger.error(f"Error getting plot detail {plot_id}: {e}")
            return None
    
    async def get_user_bookings(self, user_id: int) -> List[Booking]:
        """Получает бронирования пользователя"""
        try:
            bookings = await self.api_client.get_user_bookings(user_id)
            # Сортируем по дате создания (новые сверху)
            bookings.sort(key=lambda x: x.created_at, reverse=True)
            return bookings
        except Exception as e:
            logger.error(f"Error getting user bookings: {e}")
            return []
    
    async def create_booking(self, plot_id: int, user_data: Dict[str, Any]) -> Optional[Booking]:
        """Создает бронирование участка"""
        try:
            return await self.api_client.create_booking(plot_id, user_data)
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return None
    
    async def cancel_booking(self, booking_id: int) -> bool:
        """Отменяет бронирование"""
        try:
            return await self.api_client.cancel_booking(booking_id)
        except Exception as e:
            logger.error(f"Error cancelling booking {booking_id}: {e}")
            return False

# Глобальный экземпляр сервиса
booking_service = BookingService()
