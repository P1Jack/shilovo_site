import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
import logging
from config import config
from models.booking import Booking
from models.plot import Plot

logger = logging.getLogger(__name__)

class ApiClient:
    """Асинхронный клиент для работы с API бэкенда (для покупателя)"""
    
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.timeout = config.API_TIMEOUT
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def ensure_session(self):
        """Создает HTTP сессию если она не существует"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                timeout=timeout
            )
    
    async def close(self):
        """Корректно закрывает HTTP сессию"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """Универсальный метод для выполнения HTTP запросов"""
        await self.ensure_session()
        
        try:
            async with self.session.request(method, endpoint, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"API {method} {endpoint}: SUCCESS")
                    return data
                else:
                    logger.error(f"API {method} {endpoint}: ERROR {response.status}")
                    return None
        except Exception as e:
            logger.error(f"API {method} {endpoint}: ERROR - {e}")
            return None
    
    async def get_available_plots(self, page: int = 1, limit: int = 10) -> List[Plot]:
        """Получает список доступных участков"""
        endpoint = config.API_ENDPOINTS['plots']
        params = {'status': 'available', 'page': page, 'limit': limit}
        
        data = await self._make_request('GET', endpoint, params=params)
        
        if data and isinstance(data, list):
            return [Plot(**item) for item in data]
        
        # Заглушка для тестирования
        return [
            Plot(
                id=1,
                title="Участок в коттеджном поселке",
                price=250000,
                area="10 соток",
                location="Московская область",
                description="Прекрасный участок с коммуникациями в охраняемом поселке.",
                status="available",
                images=[],
                features=["Электричество", "Газ", "Вода", "Охрана"]
            ),
            Plot(
                id=2,
                title="Земля под ИЖС у леса",
                price=180000,
                area="8 соток", 
                location="Калужская область",
                description="Участок для строительства дома в экологически чистом районе.",
                status="available",
                images=[],
                features=["Электричество", "Рядом лес", "Хорошая экология"]
            )
        ]
    
    async def get_plot_detail(self, plot_id: int) -> Optional[Plot]:
        """Получает детальную информацию об участке"""
        endpoint = config.API_ENDPOINTS['plot_detail'].format(id=plot_id)
        
        data = await self._make_request('GET', endpoint)
        
        if data:
            return Plot(**data)
        
        return None
    
    async def get_user_bookings(self, user_id: int) -> List[Booking]:
        """Получает бронирования пользователя"""
        endpoint = config.API_ENDPOINTS['bookings']
        params = {'user_id': user_id}
        
        data = await self._make_request('GET', endpoint, params=params)
        
        if data and isinstance(data, list):
            return [Booking(**item) for item in data]
        
        return []
    
    async def create_booking(self, plot_id: int, user_data: Dict[str, Any]) -> Optional[Booking]:
        """Создает бронирование участка"""
        endpoint = config.API_ENDPOINTS['create_booking']
        
        booking_data = {
            'plot_id': plot_id,
            'customer_name': user_data.get('name'),
            'customer_phone': user_data.get('phone'),
            'customer_email': user_data.get('email'),
            'user_id': user_data.get('user_id')
        }
        
        data = await self._make_request('POST', endpoint, json=booking_data)
        
        if data:
            return Booking(**data)
        
        return None
    
    async def cancel_booking(self, booking_id: int) -> bool:
        """Отменяет бронирование"""
        endpoint = config.API_ENDPOINTS['cancel_booking'].format(id=booking_id)
        
        data = await self._make_request('POST', endpoint)
        
        return data is not None and data.get('success', False)

# Глобальный экземпляр API клиента
api_client = ApiClient()
