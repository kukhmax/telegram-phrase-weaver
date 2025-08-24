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

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# ==================
#       Card
# ==================

class CardBase(BaseModel):
    phrase: str
    translation: str
    keyword: str
    examples: Optional[List[dict]] = None
    audio_path: Optional[str] = None
    image_path: Optional[str] = None

class CardCreate(BaseModel):
    deck_id: int
    front_text: str
    back_text: str
    difficulty: Optional[int] = 1
    next_review: Optional[str] = None
    image_path: Optional[str] = None

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
    name: str
    description: Optional[str] = None
    lang_from: str
    lang_to: str

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