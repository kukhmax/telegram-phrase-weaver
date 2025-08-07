#!/usr/bin/env python3

import requests
import json

def check_decks():
    """Проверяем существующие колоды и их языки"""
    print("=== Проверка существующих колод ===")
    
    # Получаем список всех колод
    try:
        response = requests.get('http://localhost:8001/api/decks/?user_id=1')
        print(f"Статус запроса списка колод: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            decks = data.get('decks', [])
            print(f"Найдено колод: {len(decks)}")
            print()
            
            for deck in decks:
                print(f"ID: {deck['id']}")
                print(f"Название: {deck['name']}")
                print(f"Исходный язык: {deck['source_language']}")
                print(f"Целевой язык: {deck['target_language']}")
                print(f"Количество карточек: {deck.get('card_count', 0)}")
                print("-" * 40)
        else:
            print(f"Ошибка получения списка колод: {response.text}")
            
    except Exception as e:
        print(f"Ошибка при запросе: {e}")

def test_specific_deck(deck_id):
    """Тестируем конкретную колоду"""
    print(f"\n=== Тестирование колоды {deck_id} ===")
    
    try:
        # Получаем информацию о колоде
        response = requests.get(f'http://localhost:8001/api/decks/{deck_id}?user_id=1')
        print(f"Статус получения колоды: {response.status_code}")
        
        if response.status_code == 200:
            deck = response.json()
            print(f"Название: {deck['name']}")
            print(f"Исходный язык: {deck['source_language']}")
            print(f"Целевой язык: {deck['target_language']}")
            
            # Тестируем генерацию фраз для этой колоды
            print(f"\nТестирование генерации фраз для колоды {deck_id}...")
            enrich_data = {
                'original_phrase': 'орmo',
                'keyword': 'aprender',
                'deck_id': deck_id
            }
            
            response = requests.post(
                'http://localhost:8001/api/cards/enrich?user_id=1',
                json=enrich_data
            )
            
            print(f"Статус генерации: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Исходный язык из API: {result.get('source_language')}")
                print(f"Целевой язык из API: {result.get('target_language')}")
                print(f"Количество фраз: {len(result.get('phrases', []))}")
                
                # Показываем первую фразу как пример
                phrases = result.get('phrases', [])
                if phrases:
                    first_phrase = phrases[0]
                    print(f"Пример фразы: {first_phrase.get('original')} → {first_phrase.get('translation')}")
            else:
                print(f"Ошибка генерации: {response.text}")
        else:
            print(f"Ошибка получения колоды: {response.text}")
            
    except Exception as e:
        print(f"Ошибка при тестировании колоды {deck_id}: {e}")

if __name__ == "__main__":
    check_decks()
    
    # Тестируем колоды 1, 2, 3
    for deck_id in [1, 2, 3]:
        test_specific_deck(deck_id)