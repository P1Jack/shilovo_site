import os
import pytz
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Московское время
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

def get_moscow_time():
    """Возвращает текущее время в московском часовом поясе"""
    return datetime.now(MOSCOW_TZ)

class Config:
    """Конфигурация приложения для покупателя"""
    
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
    
    # Эндпоинты API для покупателя
    API_ENDPOINTS = {
        'plots': '/plots',                          # Список участков
        'plot_detail': '/plots/{id}',              # Детали участка
        'bookings': '/bookings',                    # Брони пользователя
        'create_booking': '/bookings',              # Создание брони
        'booking_detail': '/bookings/{id}',         # Детали брони
        'cancel_booking': '/bookings/{id}/cancel',  # Отмена брони
    }
    
    API_TIMEOUT = 30
    PAGE_SIZE = 5

class States:
    """Состояния для FSM (бронирование участка)"""
    SELECTING_PLOT = 1
    CONFIRMING_BOOKING = 2
    WAITING_CONTACT = 3

class BookingStatus:
    """Статусы бронирования"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

config = Config()
