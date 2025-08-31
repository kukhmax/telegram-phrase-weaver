from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import logging
import json
import aiohttp
from typing import Dict, Any
from ..core.config import get_settings

router = APIRouter(prefix="/telegram", tags=["telegram"])

logger = logging.getLogger(__name__)
settings = get_settings()

class WebhookUpdate(BaseModel):
    """Telegram webhook update model"""
    update_id: int
    message: Dict[str, Any] = None
    callback_query: Dict[str, Any] = None
    inline_query: Dict[str, Any] = None

async def send_telegram_message(chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: Dict = None):
    """Send message to Telegram chat"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token not configured")
        return False
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Message sent successfully to chat {chat_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send message: {response.status} - {error_text}")
                    return False
    except Exception as e:
        logger.error(f"Error sending message to Telegram: {e}")
        return False

def get_start_instruction():
    """Get start instruction text"""
    return """
🎉 <b>Добро пожаловать в PhraseWeaver!</b>

📚 <b>Что умеет этот бот:</b>
• Создавать колоды для изучения языков
• Генерировать карточки с фразами и переводами
• Проводить тренировки с разными типами упражнений
• Отслеживать прогресс обучения

🚀 <b>Как начать:</b>
1️⃣ Нажмите кнопку "Открыть приложение" ниже
2️⃣ Создайте свою первую колоду
3️⃣ Добавьте карточки с фразами
4️⃣ Начните тренировку!

💡 <b>Типы упражнений:</b>
• Перевод фраз
• Обратный перевод
• Заполнение пропусков

🎯 <b>Система повторений:</b>
Используем умный алгоритм для оптимального запоминания!

<i>Готовы начать изучение? Нажмите кнопку ниже! 👇</i>
    """.strip()

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram webhook endpoint.
    Receives updates from Telegram Bot API.
    """
    try:
        # Get raw request body
        body = await request.body()
        
        # Log the webhook request
        logger.info(f"Received Telegram webhook: {body.decode('utf-8')[:200]}...")
        
        # Parse JSON
        update_data = json.loads(body)
        
        # Process the update
        logger.info(f"Telegram update received: {update_data.get('update_id')}")
        
        # Handle messages
        if "message" in update_data:
            message = update_data["message"]
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            
            logger.info(f"Message from chat {chat_id}: {text}")
            
            # Handle /start command
            if text == "/start":
                await handle_start_command(chat_id)
            
            # Handle other commands here if needed
            elif text.startswith("/"):
                await send_telegram_message(
                    chat_id, 
                    "Извините, эта команда пока не поддерживается. Используйте /start для начала работы."
                )
        
        # Handle callback queries (button presses)
        elif "callback_query" in update_data:
            callback_query = update_data["callback_query"]
            # Handle button presses here if needed
            logger.info(f"Callback query received: {callback_query}")
        
        return {"ok": True}
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def handle_start_command(chat_id: int):
    """Handle /start command"""
    try:
        # Get instruction text
        instruction_text = get_start_instruction()
        
        # Create Web App button
        web_app_url = settings.API_BASE_URL or "https://pw-new.club"
        
        reply_markup = {
            "inline_keyboard": [[
                {
                    "text": "🚀 Открыть приложение",
                    "web_app": {"url": web_app_url}
                }
            ]]
        }
        
        # Send welcome message with instruction
        await send_telegram_message(
            chat_id=chat_id,
            text=instruction_text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        logger.info(f"Start command handled for chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error handling start command: {e}")
        # Send fallback message
        await send_telegram_message(
            chat_id,
            "Добро пожаловать в PhraseWeaver! Произошла ошибка при загрузке инструкции, но вы можете начать использовать приложение."
        )

@router.get("/webhook")
async def webhook_info():
    """
    GET endpoint for webhook info (for debugging)
    """
    return {
        "message": "Telegram webhook endpoint",
        "method": "POST",
        "description": "This endpoint receives updates from Telegram Bot API"
    }