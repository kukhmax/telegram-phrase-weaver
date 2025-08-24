# backend/app/schemas.py

"""
Pydantic схемы — это "контракт" вашего API. 
Они автоматически проверяют типы входящих данных 
(например, что name это строка, а deck_id — число)
и генерируют документацию для API.
Это делает код более надежным и предсказуемым.

    Объяснение:

`CardBase`, `DeckBase`: Содержат общие поля для создания и чтения.
`CardCreate`, `DeckCreate`: Схемы для получения данных 
        от клиента при создании сущности.
`Card`, `Deck`, `User`: Полные схемы для возврата данных клиенту, 
        включая поля, сгенерированные сервером (`id`, `user_id` и т.д.).
`ConfigDict(from_attributes=True)`: Очень важная настройка, 
        которая позволяет Pydantic автоматически считывать 
        данные из ваших SQLAlchemy моделей (`User`, `Deck`, `Card`).
"""

from pydantic import BaseModel, ConfigDict, validator, Field
from typing import Optional, List
from datetime import datetime

from .validators import (
    DeckValidators,
    CardValidators,
    LanguageValidators,
    FileValidators
)

# ==================
#       Card
# ==================

class CardBase(BaseModel):
    phrase: str = Field(..., min_length=1, max_length=500, description="Фраза на изучаемом языке")
    translation: str = Field(..., min_length=1, max_length=500, description="Перевод фразы")
    keyword: str = Field("", max_length=100, description="Ключевое слово")
    examples: Optional[List[dict]] = Field(None, description="Дополнительные примеры")
    audio_path: Optional[str] = Field(None, description="Путь к аудио файлу")
    image_path: Optional[str] = Field(None, description="Путь к изображению")
    
    @validator('phrase')
    def validate_phrase(cls, v):
        return CardValidators.validate_phrase(v)
    
    @validator('translation')
    def validate_translation(cls, v):
        return CardValidators.validate_translation(v)
    
    @validator('keyword')
    def validate_keyword(cls, v):
        return CardValidators.validate_keyword(v)
    
    @validator('audio_path')
    def validate_audio_path(cls, v):
        return FileValidators.validate_audio_path(v)
    
    @validator('image_path')
    def validate_image_path(cls, v):
        return FileValidators.validate_image_path(v)

class CardCreate(BaseModel):
    deck_id: int = Field(..., gt=0, description="ID колоды")
    front_text: str = Field(..., min_length=1, max_length=500, description="Текст на лицевой стороне")
    back_text: str = Field(..., min_length=1, max_length=500, description="Текст на обратной стороне")
    difficulty: Optional[int] = Field(1, ge=1, le=5, description="Уровень сложности")
    next_review: Optional[str] = Field(None, description="Дата следующего повторения")
    image_path: Optional[str] = Field(None, description="Путь к изображению")
    
    @validator('front_text')
    def validate_front_text(cls, v):
        return CardValidators.validate_phrase(v)
    
    @validator('back_text')
    def validate_back_text(cls, v):
        return CardValidators.validate_translation(v)
    
    @validator('image_path')
    def validate_image_path(cls, v):
        return FileValidators.validate_image_path(v)

class Card(CardBase):
    model_config = ConfigDict(from_attributes=True) # Позволяет создавать схему из модели SQLAlchemy

    id: int
    deck_id: int
    due_date: datetime
    interval: float
    ease_factor: float

# ==================
#       Deck
# ==================

class DeckBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название колоды")
    description: Optional[str] = Field(None, max_length=500, description="Описание колоды")
    lang_from: str = Field(..., description="Язык изучения")
    lang_to: str = Field(..., description="Язык перевода")
    
    @validator('name')
    def validate_name(cls, v):
        return DeckValidators.validate_deck_name(v)
    
    @validator('description')
    def validate_description(cls, v):
        return DeckValidators.validate_deck_description(v)
    
    @validator('lang_from')
    def validate_lang_from(cls, v):
        return LanguageValidators.validate_language_code(v, "lang_from")
    
    @validator('lang_to')
    def validate_lang_to(cls, v):
        return LanguageValidators.validate_language_code(v, "lang_to")
    
    @validator('lang_to')
    def validate_different_languages(cls, v, values):
        if 'lang_from' in values:
            LanguageValidators.validate_different_languages(values['lang_from'], v)
        return v

class DeckCreate(DeckBase):
    pass

class Deck(DeckBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    cards_count: int
    due_count: int

# ==================
#       User
# ==================

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    is_premium: bool
    last_active: datetime

# ==================
#   Auth & Tokens
# ==================

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User