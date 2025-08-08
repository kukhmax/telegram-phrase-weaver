from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import hmac
import hashlib
from urllib.parse import unquote, parse_qsl

router = APIRouter()

class TelegramAuthRequest(BaseModel):
    init_data: str
    user: dict = None

# Токен вашего бота (получите от @BotFather)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")

def verify_telegram_data(init_data: str) -> dict:
    """Проверка подлинности данных от Telegram WebApp"""
    try:
        parsed = dict(parse_qsl(unquote(init_data)))
        received_hash = parsed.pop('hash', None)
        
        if not received_hash:
            raise ValueError("Хеш не найден")
        
        # Создаем строку для проверки
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed.items())])
        
        # Создаем секретный ключ
        secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash != received_hash:
            raise ValueError("Неверная подпись")
            
        # Парсим данные пользователя
        user_data = json.loads(parsed.get('user', '{}'))
        return user_data
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Ошибка проверки данных Telegram: {str(e)}")

@router.post("/api/auth/telegram/verify")
async def verify_telegram_auth(request: TelegramAuthRequest):
    try:
        if request.init_data:
            user_data = verify_telegram_data(request.init_data)
        else:
            # Для тестирования
            user_data = request.user or {"id": 123456789, "first_name": "Test"}
        
        # Здесь должна быть логика создания/получения пользователя из БД
        # и создание JWT токена
        
        token = f"test-token-{user_data['id']}"  # В продакшене использовать JWT
        
        return {
            "token": token,
            "user": user_data,
            "message": "Аутентификация успешна"
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))