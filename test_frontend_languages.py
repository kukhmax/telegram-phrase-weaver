#!/usr/bin/env python3

import requests
import json

def test_deck_api():
    """Тестируем API для получения информации о колоде"""
    print("=== Тестирование API колод ===")
    
    # Тестируем колоду 1 (английский -> русский)
    response = requests.get('http://localhost:8000/api/decks/1?user_id=1')
    print(f"Колода 1 - Статус: {response.status_code}")
    if response.status_code == 200:
        deck_data = response.json()
        print(f"Название: {deck_data['name']}")
        print(f"Исходный язык: {deck_data['source_language']}")
        print(f"Целевой язык: {deck_data['target_language']}")
    print()
    
    # Тестируем колоду 2 (французский -> русский)
    response = requests.get('http://localhost:8000/api/decks/2?user_id=1')
    print(f"Колода 2 - Статус: {response.status_code}")
    if response.status_code == 200:
        deck_data = response.json()
        print(f"Название: {deck_data['name']}")
        print(f"Исходный язык: {deck_data['source_language']}")
        print(f"Целевой язык: {deck_data['target_language']}")
    print()

def test_enrich_api():
    """Тестируем API обогащения карточек"""
    print("=== Тестирование API обогащения ===")
    
    # Тестируем с колодой 1 (английский -> русский)
    payload = {
        "deck_id": 1,
        "original_phrase": "Hello world",
        "keyword": "hello"
    }
    
    response = requests.post(
        'http://localhost:8000/api/cards/enrich?user_id=1',
        json=payload
    )
    
    print(f"Обогащение колоды 1 - Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Исходный язык: {data.get('source_language')}")
        print(f"Целевой язык: {data.get('target_language')}")
        print(f"ID колоды: {data.get('deck_id')}")
    print()
    
    # Тестируем с колодой 2 (французский -> русский)
    payload = {
        "deck_id": 2,
        "original_phrase": "Bonjour le monde",
        "keyword": "bonjour"
    }
    
    response = requests.post(
        'http://localhost:8000/api/cards/enrich?user_id=1',
        json=payload
    )
    
    print(f"Обогащение колоды 2 - Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Исходный язык: {data.get('source_language')}")
        print(f"Целевой язык: {data.get('target_language')}")
        print(f"ID колоды: {data.get('deck_id')}")
    print()

if __name__ == "__main__":
    test_deck_api()
    test_enrich_api()
    print("Тестирование завершено!")