import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Инициализация бота
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

def get_start_instruction():
    """Get start instruction text"""
    return """
🎉 <b>Добро пожаловать в PhraseWeaver!</b>

📚 <b>Что умеет этот бот:</b>
• Создавать колоды для изучения языков
• Генерировать карточки с фразами по ключевому слову и переводами
• Проводить тренировки с разными типами упражнений
• Отслеживать прогресс обучения

🚀 <b>Как начать:</b>
1️⃣ Нажмите кнопку "Открыть приложение" ниже
2️⃣ Создайте свою первую колоду, нажав на <b>"+"</b> и выбрать язык изучения и язык перевода
3️⃣ Напишите или вставьте фразу для изучения
4️⃣ Выберите или введите ключевое слово из этой фразы, которое вы хотите запомнить
5️⃣ Далее можете сохранить фарзу с переводом, либо создають фразы с ключевым словом в разных формах с переводом
6️⃣ Начните тренировку!

💡 <b>Типы упражнений:</b>
• Перевод фраз
• Обратный перевод
• Заполнение пропусков

<i>Готовы начать изучение? Нажмите кнопку ниже! 👇</i>
    """.strip()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Handle /start command"""
    try:
        # Get instruction text
        instruction_text = get_start_instruction()
        
        # Create Web App button
        web_app_url = settings.API_BASE_URL or "https://pw-new.club"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть приложение",
                    web_app=WebAppInfo(url=web_app_url)
                )
            ]
        ])
        
        # Send welcome message with instruction
        await message.answer(
            text=instruction_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        logger.info(f"Start command handled for chat {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling start command: {e}")
        # Send fallback message
        await message.answer(
            "Добро пожаловать в PhraseWeaver! Произошла ошибка при загрузке инструкции, но вы можете начать использовать приложение."
        )

@dp.message()
async def handle_other_messages(message: types.Message):
    """Handle other messages"""
    if message.text and message.text.startswith("/"):
        await message.answer(
            "Извините, эта команда пока не поддерживается. Используйте /start для начала работы."
        )
    else:
        await message.answer(
            "Привет! Используйте /start для начала работы с PhraseWeaver."
        )

async def set_webhook():
    """Set webhook for the bot"""
    webhook_url = f"{settings.API_BASE_URL}/api/telegram/webhook"
    try:
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")

async def process_webhook_update(update_data: dict):
    """Process webhook update"""
    try:
        update = types.Update(**update_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}")
        raise