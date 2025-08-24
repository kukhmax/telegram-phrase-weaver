# backend/app/validators.py
"""
Валидаторы для входных данных.
Содержит кастомные валидаторы для Pydantic схем.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import validator, Field
from fastapi import HTTPException, status


class ValidationError(HTTPException):
    """Кастомное исключение для ошибок валидации."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error{f' in field {field}' if field else ''}: {detail}"
        )


class TextValidators:
    """Валидаторы для текстовых полей."""
    
    @staticmethod
    def validate_non_empty_string(value: str, field_name: str = "field") -> str:
        """
        Проверяет, что строка не пустая и не состоит только из пробелов.
        
        Args:
            value: Значение для проверки
            field_name: Имя поля для сообщения об ошибке
            
        Returns:
            str: Очищенное значение
            
        Raises:
            ValidationError: Если строка пустая
        """
        if not value or not value.strip():
            raise ValidationError(f"{field_name} cannot be empty", field_name)
        
        return value.strip()
    
    @staticmethod
    def validate_text_length(
        value: str, 
        min_length: int = 1, 
        max_length: int = 1000,
        field_name: str = "field"
    ) -> str:
        """
        Проверяет длину текста.
        
        Args:
            value: Значение для проверки
            min_length: Минимальная длина
            max_length: Максимальная длина
            field_name: Имя поля
            
        Returns:
            str: Валидное значение
            
        Raises:
            ValidationError: Если длина не соответствует требованиям
        """
        if len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters long",
                field_name
            )
        
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} must be no more than {max_length} characters long",
                field_name
            )
        
        return value
    
    @staticmethod
    def validate_no_html_tags(value: str, field_name: str = "field") -> str:
        """
        Проверяет, что в тексте нет HTML тегов (кроме разрешенных).
        
        Args:
            value: Значение для проверки
            field_name: Имя поля
            
        Returns:
            str: Валидное значение
            
        Raises:
            ValidationError: Если найдены недопустимые HTML теги
        """
        # Разрешенные теги для выделения ключевых слов
        allowed_tags = ["<b>", "</b>", "<strong>", "</strong>"]
        
        # Удаляем разрешенные теги для проверки
        clean_value = value
        for tag in allowed_tags:
            clean_value = clean_value.replace(tag, "")
        
        # Проверяем на наличие других HTML тегов
        html_pattern = re.compile(r'<[^>]+>')
        if html_pattern.search(clean_value):
            raise ValidationError(
                f"{field_name} contains forbidden HTML tags",
                field_name
            )
        
        return value


class LanguageValidators:
    """Валидаторы для языковых кодов."""
    
    # Поддерживаемые языки
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "ru": "Русский",
        "fr": "Français",
        "de": "Deutsch",
        "es": "Español",
        "pl": "Polski",
        "pt": "Portuguese",
        "it": "Italiano",
        "ja": "日本語",
        "ko": "한국어",
        "zh": "中文"
    }
    
    @staticmethod
    def validate_language_code(value: str, field_name: str = "language") -> str:
        """
        Проверяет, что код языка поддерживается.
        
        Args:
            value: Код языка
            field_name: Имя поля
            
        Returns:
            str: Валидный код языка
            
        Raises:
            ValidationError: Если язык не поддерживается
        """
        if value not in LanguageValidators.SUPPORTED_LANGUAGES:
            supported = ", ".join(LanguageValidators.SUPPORTED_LANGUAGES.keys())
            raise ValidationError(
                f"Unsupported language code '{value}'. Supported: {supported}",
                field_name
            )
        
        return value
    
    @staticmethod
    def validate_different_languages(
        lang_from: str, 
        lang_to: str
    ) -> tuple[str, str]:
        """
        Проверяет, что языки изучения и перевода разные.
        
        Args:
            lang_from: Язык изучения
            lang_to: Язык перевода
            
        Returns:
            tuple: Валидные коды языков
            
        Raises:
            ValidationError: Если языки одинаковые
        """
        if lang_from == lang_to:
            raise ValidationError(
                "Source and target languages must be different"
            )
        
        return lang_from, lang_to


class DeckValidators:
    """Валидаторы для колод."""
    
    @staticmethod
    def validate_deck_name(value: str) -> str:
        """
        Валидирует название колоды.
        
        Args:
            value: Название колоды
            
        Returns:
            str: Валидное название
        """
        value = TextValidators.validate_non_empty_string(value, "deck name")
        value = TextValidators.validate_text_length(value, 1, 100, "deck name")
        value = TextValidators.validate_no_html_tags(value, "deck name")
        
        return value
    
    @staticmethod
    def validate_deck_description(value: Optional[str]) -> Optional[str]:
        """
        Валидирует описание колоды.
        
        Args:
            value: Описание колоды
            
        Returns:
            Optional[str]: Валидное описание или None
        """
        if value is None or value.strip() == "":
            return None
        
        value = value.strip()
        value = TextValidators.validate_text_length(value, 0, 500, "deck description")
        value = TextValidators.validate_no_html_tags(value, "deck description")
        
        return value


class CardValidators:
    """Валидаторы для карточек."""
    
    @staticmethod
    def validate_phrase(value: str) -> str:
        """
        Валидирует фразу на карточке.
        
        Args:
            value: Фраза
            
        Returns:
            str: Валидная фраза
        """
        value = TextValidators.validate_non_empty_string(value, "phrase")
        value = TextValidators.validate_text_length(value, 1, 500, "phrase")
        # Для фраз разрешаем HTML теги для выделения
        
        return value
    
    @staticmethod
    def validate_translation(value: str) -> str:
        """
        Валидирует перевод карточки.
        
        Args:
            value: Перевод
            
        Returns:
            str: Валидный перевод
        """
        value = TextValidators.validate_non_empty_string(value, "translation")
        value = TextValidators.validate_text_length(value, 1, 500, "translation")
        # Для переводов разрешаем HTML теги для выделения
        
        return value
    
    @staticmethod
    def validate_keyword(value: str) -> str:
        """
        Валидирует ключевое слово.
        
        Args:
            value: Ключевое слово
            
        Returns:
            str: Валидное ключевое слово
        """
        if not value:
            return ""
        
        value = value.strip()
        value = TextValidators.validate_text_length(value, 0, 100, "keyword")
        value = TextValidators.validate_no_html_tags(value, "keyword")
        
        return value
    
    @staticmethod
    def validate_rating(value: str) -> str:
        """
        Валидирует рейтинг карточки для SRS.
        
        Args:
            value: Рейтинг
            
        Returns:
            str: Валидный рейтинг
            
        Raises:
            ValidationError: Если рейтинг недопустимый
        """
        allowed_ratings = ["again", "good", "easy"]
        
        if value not in allowed_ratings:
            raise ValidationError(
                f"Invalid rating '{value}'. Allowed: {', '.join(allowed_ratings)}",
                "rating"
            )
        
        return value


class FileValidators:
    """Валидаторы для файлов."""
    
    @staticmethod
    def validate_image_path(value: Optional[str]) -> Optional[str]:
        """
        Валидирует путь к изображению.
        
        Args:
            value: Путь к изображению
            
        Returns:
            Optional[str]: Валидный путь или None
        """
        if not value:
            return None
        
        # Проверяем формат пути
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        
        if not any(value.lower().endswith(ext) for ext in allowed_extensions):
            raise ValidationError(
                f"Invalid image format. Allowed: {', '.join(allowed_extensions)}",
                "image_path"
            )
        
        return value
    
    @staticmethod
    def validate_audio_path(value: Optional[str]) -> Optional[str]:
        """
        Валидирует путь к аудио файлу.
        
        Args:
            value: Путь к аудио
            
        Returns:
            Optional[str]: Валидный путь или None
        """
        if not value:
            return None
        
        # Проверяем формат пути
        allowed_extensions = [".mp3", ".wav", ".ogg", ".m4a"]
        
        if not any(value.lower().endswith(ext) for ext in allowed_extensions):
            raise ValidationError(
                f"Invalid audio format. Allowed: {', '.join(allowed_extensions)}",
                "audio_path"
            )
        
        return value


def validate_request_data(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Общая функция для валидации данных запроса.
    
    Args:
        data: Данные для валидации
        required_fields: Список обязательных полей
        
    Returns:
        Dict: Валидные данные
        
    Raises:
        ValidationError: При ошибках валидации
    """
    # Проверяем наличие обязательных полей
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    return data