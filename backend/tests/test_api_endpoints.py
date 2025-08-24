# backend/tests/test_api_endpoints.py
"""
Тесты для API эндпоинтов.
"""

import pytest
from fastapi import status


class TestAuthEndpoints:
    """Тесты для эндпоинтов аутентификации."""
    
    def test_get_current_user_info_success(self, client, auth_headers, test_user):
        """Тест успешного получения информации о пользователе."""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["telegram_id"] == test_user.telegram_id
        assert data["username"] == test_user.username
        assert data["first_name"] == test_user.first_name
    
    def test_get_current_user_info_unauthorized(self, client):
        """Тест получения информации без авторизации."""
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_info_invalid_token(self, client):
        """Тест с невалидным токеном."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_telegram_auth_debug(self, client):
        """Тест debug эндпоинта для аутентификации."""
        response = client.post("/auth/telegram/debug")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"


class TestDeckEndpoints:
    """Тесты для эндпоинтов колод."""
    
    def test_create_deck_success(self, client, auth_headers):
        """Тест успешного создания колоды."""
        deck_data = {
            "name": "Test Deck",
            "description": "Test deck description",
            "lang_from": "en",
            "lang_to": "ru"
        }
        
        response = client.post("/decks/", json=deck_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["name"] == deck_data["name"]
        assert data["description"] == deck_data["description"]
        assert data["lang_from"] == deck_data["lang_from"]
        assert data["lang_to"] == deck_data["lang_to"]
        assert "id" in data
        assert "user_id" in data
    
    def test_create_deck_unauthorized(self, client):
        """Тест создания колоды без авторизации."""
        deck_data = {
            "name": "Test Deck",
            "description": "Test deck description",
            "lang_from": "en",
            "lang_to": "ru"
        }
        
        response = client.post("/decks/", json=deck_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_deck_invalid_data(self, client, auth_headers):
        """Тест создания колоды с невалидными данными."""
        deck_data = {
            "name": "",  # Пустое имя
            "lang_from": "en"
            # Отсутствует обязательное поле lang_to
        }
        
        response = client.post("/decks/", json=deck_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_decks_success(self, client, auth_headers, test_deck):
        """Тест успешного получения списка колод."""
        response = client.get("/decks/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Проверяем, что наша тестовая колода в списке
        deck_ids = [deck["id"] for deck in data]
        assert test_deck.id in deck_ids
    
    def test_get_decks_unauthorized(self, client):
        """Тест получения колод без авторизации."""
        response = client.get("/decks/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_deck_success(self, client, auth_headers, test_deck):
        """Тест успешного удаления колоды."""
        response = client.delete(f"/decks/{test_deck.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что колода действительно удалена
        get_response = client.get("/decks/", headers=auth_headers)
        decks = get_response.json()
        deck_ids = [deck["id"] for deck in decks]
        assert test_deck.id not in deck_ids
    
    def test_delete_deck_not_found(self, client, auth_headers):
        """Тест удаления несуществующей колоды."""
        response = client.delete("/decks/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_deck_unauthorized(self, client, test_deck):
        """Тест удаления колоды без авторизации."""
        response = client.delete(f"/decks/{test_deck.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCardEndpoints:
    """Тесты для эндпоинтов карточек."""
    
    def test_get_deck_cards_success(self, client, auth_headers, test_deck, test_card):
        """Тест успешного получения карточек колоды."""
        response = client.get(f"/cards/deck/{test_deck.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "deck" in data
        assert "cards" in data
        assert data["deck"]["id"] == test_deck.id
        assert isinstance(data["cards"], list)
        assert len(data["cards"]) >= 1
    
    def test_get_deck_cards_not_found(self, client, auth_headers):
        """Тест получения карточек несуществующей колоды."""
        response = client.get("/cards/deck/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_deck_cards_unauthorized(self, client, test_deck):
        """Тест получения карточек без авторизации."""
        response = client.get(f"/cards/deck/{test_deck.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_save_card_success(self, client, auth_headers, test_deck):
        """Тест успешного сохранения карточки."""
        card_data = {
            "deck_id": test_deck.id,
            "front_text": "Hello",
            "back_text": "Привет",
            "difficulty": 1,
            "image_path": None
        }
        
        response = client.post("/cards/save", json=card_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["deck_id"] == test_deck.id
        assert data["front_text"] == card_data["front_text"]
        assert data["back_text"] == card_data["back_text"]
        assert "id" in data
    
    def test_save_card_invalid_deck(self, client, auth_headers):
        """Тест сохранения карточки в несуществующую колоду."""
        card_data = {
            "deck_id": 99999,
            "front_text": "Hello",
            "back_text": "Привет",
            "difficulty": 1
        }
        
        response = client.post("/cards/save", json=card_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_save_card_unauthorized(self, client, test_deck):
        """Тест сохранения карточки без авторизации."""
        card_data = {
            "deck_id": test_deck.id,
            "front_text": "Hello",
            "back_text": "Привет",
            "difficulty": 1
        }
        
        response = client.post("/cards/save", json=card_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_card_status_success(self, client, auth_headers, test_card):
        """Тест успешного обновления статуса карточки."""
        status_data = {
            "card_id": test_card.id,
            "rating": "good"
        }
        
        response = client.post("/cards/update-status", json=status_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["card_id"] == test_card.id
        assert data["rating"] == "good"
        assert "due_date" in data
    
    def test_update_card_status_invalid_rating(self, client, auth_headers, test_card):
        """Тест обновления статуса с невалидным рейтингом."""
        status_data = {
            "card_id": test_card.id,
            "rating": "invalid_rating"
        }
        
        response = client.post("/cards/update-status", json=status_data, headers=auth_headers)
        
        # Сервер должен обработать это корректно или вернуть ошибку
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    def test_delete_card_success(self, client, auth_headers, test_card):
        """Тест успешного удаления карточки."""
        response = client.delete(f"/cards/delete/{test_card.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["card_id"] == test_card.id
        assert "message" in data
    
    def test_delete_card_not_found(self, client, auth_headers):
        """Тест удаления несуществующей карточки."""
        response = client.delete("/cards/delete/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_card_unauthorized(self, client, test_card):
        """Тест удаления карточки без авторизации."""
        response = client.delete(f"/cards/delete/{test_card.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestHealthEndpoints:
    """Тесты для служебных эндпоинтов."""
    
    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check(self, client):
        """Тест health check эндпоинта."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == "healthy"