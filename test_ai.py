#!/usr/bin/env python3
"""
Тестовый скрипт для проверки AI сервиса
"""

import asyncio
import os
import sys

# Добавляем путь к backend для импорта
sys.path.append('backend')

from backend.app.services.ai_service import ai_service

async def test_ai_service():
    """
    Тестирует AI сервис с простым примером
    """
    print("🤖 Тестирование AI сервиса...")
    
    # Проверяем наличие ключа
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key or api_key == 'ваш_google_gemini_ключ':
        print("❌ ОШИБКА: Ключ GEMINI_API_KEY не установлен или содержит заглушку!")
        print("Пожалуйста, установите реальный ключ Google Gemini API в файле backend/.env")
        print("Получить ключ можно здесь: https://makersuite.google.com/app/apikey")
        return False
    
    print(f"✅ Ключ API найден: {api_key[:10]}...")
    
    try:
        # Тестируем генерацию фраз
        result = await ai_service.generate_phrases(
            original_phrase="Я иду домой",
            keyword="иду", 
            source_language="ru",
            target_language="en"
        )
        
        print("\n📝 Результат генерации:")
        print(f"🖼️  Запрос для изображения: {result.get('image_query', 'Не найден')}")
        print(f"📚 Количество примеров: {len(result.get('examples', []))}")
        
        if result.get('examples'):
            print("\n🔤 Примеры фраз:")
            for i, example in enumerate(result['examples'][:3], 1):
                print(f"  {i}. {example.get('original', 'N/A')}")
                print(f"     → {example.get('translation', 'N/A')}")
        
        print("\n✅ AI сервис работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании AI сервиса: {e}")
        return False

if __name__ == "__main__":
    # Загружаем переменные окружения из .env
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    
    # Запускаем тест
    success = asyncio.run(test_ai_service())
    
    if success:
        print("\n🎉 Тест пройден успешно! AI готов к работе.")
    else:
        print("\n💥 Тест не пройден. Проверьте настройки.")
        sys.exit(1)