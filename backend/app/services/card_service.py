# backend/app/services/card_service.py
"""
Сервис для работы с карточками.
Содержит бизнес-логику для управления карточками и их статусами.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models.user import User
from ..models.deck import Deck
from ..models.card import Card
from ..schemas import CardCreate
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class CardService:
    """
    Сервис для управления карточками.
    """
    
    @staticmethod
    def get_deck_with_cards(deck_id: int, user: User, db: Session) -> Dict[str, Any]:
        """
        Получает колоду с карточками для указанного пользователя.
        
        Args:
            deck_id: ID колоды
            user: Пользователь
            db: Сессия базы данных
            
        Returns:
            Dict с информацией о колоде и карточках
            
        Raises:
            HTTPException: Если колода не найдена или нет доступа
        """
        # Проверяем существование колоды и права доступа
        deck = db.query(Deck).filter(Deck.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        if deck.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this deck"
            )
        
        # Получаем карточки колоды
        cards = db.query(Card).filter(Card.deck_id == deck_id).order_by(Card.id).all()
        
        return {
            "deck": {
                "id": deck.id,
                "name": deck.name,
                "lang_from": deck.lang_from,
                "lang_to": deck.lang_to,
                "cards_count": deck.cards_count
            },
            "cards": [
                {
                    "id": card.id,
                    "front_text": card.phrase,
                    "back_text": card.translation,
                    "keyword": card.keyword,
                    "difficulty": 1,  # Пока используем значение по умолчанию
                    "next_review": card.due_date.isoformat() if card.due_date else None,
                    "image_path": card.image_path
                }
                for card in cards
            ]
        }
    
    @staticmethod
    def create_card(card_data: CardCreate, user: User, db: Session) -> Dict[str, Any]:
        """
        Создает новую карточку в указанной колоде.
        
        Args:
            card_data: Данные для создания карточки
            user: Пользователь
            db: Сессия базы данных
            
        Returns:
            Dict с информацией о созданной карточке
            
        Raises:
            HTTPException: При ошибках валидации или доступа
        """
        try:
            # Проверяем существование колоды и права доступа
            deck = db.query(Deck).filter(Deck.id == card_data.deck_id).first()
            if not deck:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Deck not found"
                )
            
            if deck.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to add card to this deck"
                )
            
            # Создаем карточку
            due_date = CardService._parse_due_date(card_data.next_review)
            
            new_card = Card(
                deck_id=card_data.deck_id,
                phrase=card_data.front_text,
                translation=card_data.back_text,
                keyword="",  # Пока оставляем пустым
                audio_path=None,
                image_path=card_data.image_path,
                examples=None,
                due_date=due_date,
                interval=1.0,
                ease_factor=2.5
            )
            
            # Сохраняем карточку и обновляем счетчик
            db.add(new_card)
            deck.cards_count += 1
            db.commit()
            db.refresh(new_card)
            
            logger.info(f"Created card {new_card.id} in deck {deck.id} for user {user.id}")
            
            return {
                "id": new_card.id,
                "deck_id": new_card.deck_id,
                "front_text": new_card.phrase,
                "back_text": new_card.translation,
                "message": "Card saved successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating card: {str(e)}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save card: {str(e)}"
            )
    
    @staticmethod
    def update_card_status(
        card_id: int, 
        rating: str, 
        user: User, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Обновляет статус карточки после тренировки с использованием алгоритма SRS.
        
        Args:
            card_id: ID карточки
            rating: Рейтинг ("again", "good", "easy")
            user: Пользователь
            db: Сессия базы данных
            
        Returns:
            Dict с информацией об обновленной карточке
            
        Raises:
            HTTPException: При ошибках доступа или валидации
        """
        try:
            # Получаем карточку и проверяем права доступа
            card = db.query(Card).filter(Card.id == card_id).first()
            if not card:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Card not found"
                )
            
            deck = db.query(Deck).filter(Deck.id == card.deck_id).first()
            if not deck or deck.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized"
                )
            
            # Применяем алгоритм SRS
            old_due_date = card.due_date
            CardService._apply_srs_algorithm(card, rating)
            
            # Обновляем счетчик повторений колоды
            CardService._update_deck_due_count(deck, rating, old_due_date, card.due_date)
            
            db.commit()
            
            logger.info(f"Updated card {card_id} status to {rating} for user {user.id}")
            
            return {
                "message": "Card status updated successfully",
                "card_id": card.id,
                "rating": rating,
                "due_date": card.due_date.isoformat() if card.due_date else None,
                "deck_due_count": deck.due_count
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating card status: {str(e)}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update card status: {str(e)}"
            )
    
    @staticmethod
    def delete_card(card_id: int, user: User, db: Session) -> Dict[str, Any]:
        """
        Удаляет карточку из базы данных.
        
        Args:
            card_id: ID карточки
            user: Пользователь
            db: Сессия базы данных
            
        Returns:
            Dict с информацией об удаленной карточке
            
        Raises:
            HTTPException: При ошибках доступа или валидации
        """
        try:
            # Получаем карточку и проверяем права доступа
            card = db.query(Card).filter(Card.id == card_id).first()
            if not card:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Card not found"
                )
            
            deck = db.query(Deck).filter(Deck.id == card.deck_id).first()
            if not deck or deck.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized"
                )
            
            # Удаляем карточку и обновляем счетчики
            db.delete(card)
            deck.cards_count = max(0, (deck.cards_count or 1) - 1)
            
            db.commit()
            
            logger.info(f"Deleted card {card_id} for user {user.id}")
            
            return {
                "message": "Card deleted successfully",
                "card_id": card_id,
                "deck_cards_count": deck.cards_count
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting card: {str(e)}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete card: {str(e)}"
            )
    
    @staticmethod
    def _parse_due_date(next_review: Optional[str]) -> datetime:
        """
        Парсит дату следующего повторения.
        
        Args:
            next_review: Строка с датой в ISO формате
            
        Returns:
            datetime объект
        """
        if next_review:
            try:
                parsed_date = datetime.fromisoformat(next_review.replace('Z', '+00:00'))
                return parsed_date.replace(tzinfo=None)
            except Exception:
                pass
        
        # По умолчанию - завтра
        return datetime.utcnow() + timedelta(days=1)
    
    @staticmethod
    def _apply_srs_algorithm(card: Card, rating: str) -> None:
        """
        Применяет алгоритм интервального повторения (SRS) к карточке.
        
        Args:
            card: Карточка для обновления
            rating: Рейтинг ("again", "good", "easy")
        """
        current_time = datetime.utcnow()
        
        if rating == "again":
            # Карточка для повторения в ближайшее время
            card.due_date = current_time + timedelta(minutes=10)
            card.interval = 1
            card.ease_factor = max(1.3, card.ease_factor - 0.2)
            
        elif rating == "good":
            # Карточка для повторения позже
            card.due_date = current_time + timedelta(days=card.interval)
            card.interval = max(1, int(card.interval * card.ease_factor))
            
        elif rating == "easy":
            # Карточка изучена хорошо
            card.due_date = current_time + timedelta(days=card.interval * 2)
            card.interval = max(1, int(card.interval * card.ease_factor * 1.3))
            card.ease_factor = min(2.5, card.ease_factor + 0.15)
    
    @staticmethod
    def _update_deck_due_count(
        deck: Deck, 
        rating: str, 
        old_due_date: datetime, 
        new_due_date: datetime
    ) -> None:
        """
        Обновляет счетчик карточек для повторения в колоде.
        
        Args:
            deck: Колода
            rating: Рейтинг карточки
            old_due_date: Старая дата повторения
            new_due_date: Новая дата повторения
        """
        current_time = datetime.utcnow()
        
        # Логика обновления счетчика в зависимости от рейтинга
        if rating in ["again", "good"]:
            # Проверяем, была ли карточка просрочена
            if old_due_date and old_due_date <= current_time:
                # Карточка была просрочена, не увеличиваем счетчик
                pass
            else:
                # Карточка добавляется в повторения
                deck.due_count = (deck.due_count or 0) + 1
        
        # Для "easy" карточка считается изученной и не добавляется в повторения


# Создаем экземпляр сервиса для использования в роутерах
card_service = CardService()