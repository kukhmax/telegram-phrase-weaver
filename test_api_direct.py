#!/usr/bin/env python3
import requests
import json

def test_api():
    base_url = "http://localhost:8001"
    
    # Тест 1: Проверка health endpoint
    print("=== Тест 1: Health check ===")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест 2: Проверка API health endpoint
    print("\n=== Тест 2: API Health check ===")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест 3: Создание колоды
    print("\n=== Тест 3: Создание колоды ===")
    try:
        deck_data = {
            "name": "Test Deck",
            "description": "Test description",
            "source_language": "en",
            "target_language": "ru"
        }
        response = requests.post(
            f"{base_url}/api/decks/",
            params={"user_id": 1},
            json=deck_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест 4: Получение колод
    print("\n=== Тест 4: Получение колод ===")
    try:
        response = requests.get(
            f"{base_url}/api/decks/",
            params={"user_id": 1}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_api()