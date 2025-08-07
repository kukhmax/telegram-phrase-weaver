#!/usr/bin/env python3

import requests
import json
import os

# Установим тестовый API ключ
os.environ['GOOGLE_API_KEY'] = 'test_key_for_demo'

def test_phrase_generation():
    """Тестирует генерацию фраз через API"""
    
    base_url = "http://localhost:8001"
    
    # Данные для тестирования
    test_data = {
        "original_phrase": "I like to eat apples",
        "keyword": "eat",
        "deck_id": 1
    }
    
    print("=== Тест генерации фраз ===")
    print(f"Исходная фраза: {test_data['original_phrase']}")
    print(f"Ключевое слово: {test_data['keyword']}")
    print(f"ID колоды: {test_data['deck_id']}")
    print()
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            f"{base_url}/api/cards/enrich",
            params={"user_id": 1},
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Успешно!")
            print(f"Количество сгенерированных фраз: {len(result.get('phrases', []))}")
            print(f"Запрос для изображения: {result.get('image_query', 'Не указан')}")
            print()
            print("Сгенерированные фразы:")
            for i, phrase in enumerate(result.get('phrases', []), 1):
                print(f"{i}. {phrase['original']} → {phrase['translation']}")
        else:
            print("❌ Ошибка!")
            print(f"Ответ сервера: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу. Убедитесь, что бэкенд запущен на порту 8001.")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    test_phrase_generation()