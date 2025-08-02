from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..core.database import get_db
from ..models.card import Card
from ..models.deck import Deck
from ..services.ai_service import ai_service

router = APIRouter()

# Pydantic модели для запросов и ответов

class CardCreate(BaseModel):
    """
    Модель для создания новой карточки
    """
    front_text: str = Field(..., min_length=1, max_length=1000, description="Текст на исходном языке")
    back_text: str = Field(..., min_length=1, max_length=1000, description="Перевод на целевой язык")
    audio_url: Optional[str] = Field(None, max_length=500, description="URL аудиофайла для произношения")
    image_url: Optional[str] = Field(None, max_length=500, description="URL изображения для визуального запоминания")
    difficulty: Optional[int] = Field(1, ge=1, le=5, description="Уровень сложности (1-5)")
    deck_id: int = Field(..., description="ID колоды, к которой принадлежит карточка")

class CardUpdate(BaseModel):
    """
    Модель для обновления существующей карточки
    """
    front_text: Optional[str] = Field(None, min_length=1, max_length=1000, description="Новый текст на исходном языке")
    back_text: Optional[str] = Field(None, min_length=1, max_length=1000, description="Новый перевод на целевой язык")
    audio_url: Optional[str] = Field(None, max_length=500, description="Новый URL аудиофайла")
    image_url: Optional[str] = Field(None, max_length=500, description="Новый URL изображения")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="Новый уровень сложности (1-5)")

class CardResponse(BaseModel):
    """
    Модель ответа с информацией о карточке
    """
    id: int
    front_text: str
    back_text: str
    audio_url: Optional[str]
    image_url: Optional[str]
    difficulty: int
    deck_id: int
    correct_streak: int = Field(description="Количество правильных ответов подряд")
    next_review_date: Optional[datetime] = Field(description="Дата следующего повторения")
    review_interval: float = Field(description="Интервал до следующего повторения (в днях)")
    has_audio: bool = Field(description="Есть ли у карточки аудио")
    has_image: bool = Field(description="Есть ли у карточки изображение")
    is_due_for_review: bool = Field(description="Готова ли карточка к повторению")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CardListResponse(BaseModel):
    """
    Модель ответа со списком карточек
    """
    cards: List[CardResponse]
    total: int = Field(description="Общее количество карточек")

class CardReviewResponse(BaseModel):
    """
    Модель ответа для отметки результата повторения карточки
    """
    is_correct: bool = Field(description="Правильно ли отвечен вопрос")

# API endpoints

@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: CardCreate,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Создание новой карточки
    
    - **front_text**: Текст на исходном языке (обязательно)
    - **back_text**: Перевод на целевой язык (обязательно)
    - **audio_url**: URL аудиофайла для произношения (опционально)
    - **image_url**: URL изображения для визуального запоминания (опционально)
    - **difficulty**: Уровень сложности от 1 до 5 (по умолчанию 1)
    - **deck_id**: ID колоды, к которой принадлежит карточка
    """
    # Проверяем, существует ли колода и принадлежит ли она пользователю
    deck = db.query(Deck).filter(
        Deck.id == card_data.deck_id,
        Deck.user_id == user_id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Колода с ID {card_data.deck_id} не найдена или не принадлежит пользователю"
        )
    
    # Создаем новую карточку
    db_card = Card(
        front_text=card_data.front_text,
        back_text=card_data.back_text,
        audio_url=card_data.audio_url,
        image_url=card_data.image_url,
        difficulty=card_data.difficulty or 1,
        deck_id=card_data.deck_id
    )
    
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    
    return db_card

@router.get("/deck/{deck_id}", response_model=CardListResponse)
async def get_deck_cards(
    deck_id: int,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получение списка карточек в колоде
    
    - **deck_id**: ID колоды
    - **skip**: Количество карточек для пропуска (для пагинации)
    - **limit**: Максимальное количество карточек в ответе
    """
    # Проверяем, существует ли колода и принадлежит ли она пользователю
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == user_id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Колода с ID {deck_id} не найдена или не принадлежит пользователю"
        )
    
    # Получаем карточки колоды
    cards_query = db.query(Card).filter(Card.deck_id == deck_id)
    total = cards_query.count()
    cards = cards_query.offset(skip).limit(limit).all()
    
    return CardListResponse(cards=cards, total=total)

# Новые модели для AI обогащения карточек

class CardEnrichRequest(BaseModel):
    """
    Модель запроса для обогащения карточек через AI
    """
    original_phrase: str = Field(..., min_length=1, max_length=1000, description="Исходная фраза на изучаемом языке")
    keyword: str = Field(..., min_length=1, max_length=100, description="Ключевое слово для генерации вариаций")
    deck_id: int = Field(..., description="ID колоды для добавления карточек")

class GeneratedPhrase(BaseModel):
    """
    Модель сгенерированной фразы
    """
    original: str = Field(..., description="Фраза на исходном языке")
    translation: str = Field(..., description="Перевод на целевой язык")
    selected: bool = Field(True, description="Выбрана ли фраза для добавления")

class CardEnrichResponse(BaseModel):
    """
    Ответ с сгенерированными фразами
    """
    phrases: List[GeneratedPhrase] = Field(..., description="Список сгенерированных фраз")
    image_query: Optional[str] = Field(None, description="Запрос для поиска изображения")
    deck_id: int = Field(..., description="ID колоды")
    source_language: str = Field(..., description="Исходный язык")
    target_language: str = Field(..., description="Целевой язык")

class CardBatchCreate(BaseModel):
    """
    Модель для массового создания карточек
    """
    phrases: List[GeneratedPhrase] = Field(..., description="Список фраз для создания карточек")
    deck_id: int = Field(..., description="ID колоды")
    difficulty: Optional[int] = Field(1, ge=1, le=5, description="Уровень сложности для всех карточек")

class CardBatchResponse(BaseModel):
    """
    Модель ответа массового создания карточек
    """
    created_cards: List[CardResponse] = Field(..., description="Список созданных карточек")
    total_created: int = Field(..., description="Общее количество созданных карточек")
    skipped: int = Field(0, description="Количество пропущенных карточек")

# Новые API endpoints

@router.post("/enrich", response_model=CardEnrichResponse)
async def enrich_cards(
    enrich_data: CardEnrichRequest,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Генерирует фразы с ключевым словом через AI для создания карточек
    """
    try:
        # Проверяем существование колоды и права доступа
        deck = db.query(Deck).filter(
            Deck.id == enrich_data.deck_id,
            Deck.user_id == user_id
        ).first()
        
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Колода не найдена или у вас нет прав доступа"
            )
        
        # Генерируем фразы через AI
        ai_result = await ai_service.generate_phrases(
            original_phrase=enrich_data.original_phrase,
            keyword=enrich_data.keyword,
            source_language=deck.source_language,
            target_language=deck.target_language
        )
        
        # Преобразуем в модель ответа
        phrases = [
            GeneratedPhrase(
                original=phrase["original"],
                translation=phrase["translation"],
                selected=True
            )
            for phrase in ai_result.get("examples", [])
        ]
        
        return CardEnrichResponse(
            phrases=phrases,
            image_query=ai_result.get("image_query"),
            deck_id=deck.id,
            source_language=deck.source_language,
            target_language=deck.target_language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации фраз: {str(e)}"
        )

@router.post("/batch", response_model=CardBatchResponse)
async def create_cards_batch(
    batch_data: CardBatchCreate,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Массовое создание карточек из сгенерированных фраз
    """
    try:
        # Проверяем существование колоды и права доступа
        deck = db.query(Deck).filter(
            Deck.id == batch_data.deck_id,
            Deck.user_id == user_id
        ).first()
        
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Колода не найдена или у вас нет прав доступа"
            )
        
        created_cards = []
        skipped = 0
        
        # Создаем карточки только для выбранных фраз
        for phrase in batch_data.phrases:
            if not phrase.selected:
                skipped += 1
                continue
                
            # Проверяем, не существует ли уже такая карточка
            existing_card = db.query(Card).filter(
                Card.deck_id == batch_data.deck_id,
                Card.front_text == phrase.original.strip()
            ).first()
            
            if existing_card:
                skipped += 1
                continue
            
            # Создаем новую карточку
            new_card = Card(
                front_text=phrase.original.strip(),
                back_text=phrase.translation.strip(),
                difficulty=batch_data.difficulty or 1,
                deck_id=batch_data.deck_id,
                correct_streak=0,
                review_interval=1.0,
                next_review_date=datetime.utcnow()
            )
            
            db.add(new_card)
            db.flush()  # Получаем ID без коммита
            
            created_cards.append(new_card)
        
        # Сохраняем все изменения
        db.commit()
        
        # Обновляем счетчик карточек в колоде
        deck.card_count = db.query(Card).filter(Card.deck_id == deck.id).count()
        db.commit()
        
        # Преобразуем в модель ответа
        card_responses = []
        for card in created_cards:
            db.refresh(card)  # Обновляем объект из БД
            card_responses.append(CardResponse.from_orm(card))
        
        return CardBatchResponse(
            created_cards=card_responses,
            total_created=len(created_cards),
            skipped=skipped
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании карточек: {str(e)}"
        )

@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: int,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Получение информации о конкретной карточке
    
    - **card_id**: ID карточки
    """
    # Получаем карточку и проверяем права доступа через колоду
    card = db.query(Card).join(Deck).filter(
        Card.id == card_id,
        Deck.user_id == user_id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Карточка с ID {card_id} не найдена или не принадлежит пользователю"
        )
    
    return card

@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: int,
    card_data: CardUpdate,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Обновление существующей карточки
    
    - **card_id**: ID карточки для обновления
    - Все поля опциональны, обновляются только переданные поля
    """
    # Получаем карточку и проверяем права доступа
    card = db.query(Card).join(Deck).filter(
        Card.id == card_id,
        Deck.user_id == user_id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Карточка с ID {card_id} не найдена или не принадлежит пользователю"
        )
    
    # Обновляем только переданные поля
    update_data = card_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(card, field, value)
    
    db.commit()
    db.refresh(card)
    
    return card

@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Удаление карточки
    
    - **card_id**: ID карточки для удаления
    """
    # Получаем карточку и проверяем права доступа
    card = db.query(Card).join(Deck).filter(
        Card.id == card_id,
        Deck.user_id == user_id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Карточка с ID {card_id} не найдена или не принадлежит пользователю"
        )
    
    db.delete(card)
    db.commit()
    
    return None

@router.post("/{card_id}/review", response_model=CardResponse)
async def review_card(
    card_id: int,
    review_data: CardReviewResponse,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    db: Session = Depends(get_db)
):
    """
    Отметка результата повторения карточки
    
    - **card_id**: ID карточки
    - **is_correct**: True если ответ правильный, False если неправильный
    
    Обновляет статистику карточки и планирует следующее повторение
    """
    # Получаем карточку и проверяем права доступа
    card = db.query(Card).join(Deck).filter(
        Card.id == card_id,
        Deck.user_id == user_id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Карточка с ID {card_id} не найдена или не принадлежит пользователю"
        )
    
    # Обновляем статистику в зависимости от результата
    if review_data.is_correct:
        card.mark_as_correct()
    else:
        card.mark_as_incorrect()
    
    db.commit()
    db.refresh(card)
    
    return card

@router.get("/deck/{deck_id}/due", response_model=CardListResponse)
async def get_due_cards(
    deck_id: int,
    user_id: int,  # Пока передаем как параметр, позже добавим JWT аутентификацию
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Получение карточек, готовых к повторению
    
    - **deck_id**: ID колоды
    - **limit**: Максимальное количество карточек для повторения
    """
    # Проверяем, существует ли колода и принадлежит ли она пользователю
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == user_id
    ).first()
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Колода с ID {deck_id} не найдена или не принадлежит пользователю"
        )
    
    # Получаем карточки, готовые к повторению
    from sqlalchemy import or_, func
    from datetime import datetime
    
    cards_query = db.query(Card).filter(
        Card.deck_id == deck_id,
        or_(
            Card.next_review_date.is_(None),
            Card.next_review_date <= datetime.utcnow()
        )
    ).order_by(Card.next_review_date.asc().nullsfirst())
    
    total = cards_query.count()
    cards = cards_query.limit(limit).all()
    
    return CardListResponse(cards=cards, total=total)