#!/usr/bin/env python3
"""
Тестирование исправлений в генерации фраз
"""

import requests
import json

def test_phrase_generation():
    """Тестирование генерации фраз для португальского-французского"""
    
    url = "http://localhost:8001/api/cards/enrich"
    
    # Тестируем с ключевым словом "aprender"
    payload = {
        "original_phrase": "Eu quero aprender português",
        "keyword": "aprender",
        "deck_id": 2  # Колода с португальским -> французским
    }
    
    params = {"user_id": 1}
    
    print("🧪 Тестирование генерации фраз для 'aprender' (pt -> fr)...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"Params: {params}")
    print("\n" + "="*50 + "\n")
    
    try:
        response = requests.post(url, json=payload, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Успешный ответ!")
            print(f"Image Query: {data.get('image_query', 'N/A')}")
            print("\nСгенерированные фразы:")
            
            for i, example in enumerate(data.get('examples', []), 1):
                original = example.get('original', '')
                translation = example.get('translation', '')
                print(f"{i}. {original}")
                print(f"   -> {translation}")
                print()
                
                # Проверяем, что ключевое слово правильно используется
                if 'aprender' in original.lower():
                    print(f"   ✅ Ключевое слово найдено в оригинале")
                else:
                    print(f"   ❌ Ключевое слово НЕ найдено в оригинале")
                    
                if 'apprendre' in translation.lower():
                    print(f"   ✅ Перевод ключевого слова найден")
                else:
                    print(f"   ❌ Перевод ключевого слова НЕ найден")
                print()
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")

if __name__ == "__main__":
    test_phrase_generation()