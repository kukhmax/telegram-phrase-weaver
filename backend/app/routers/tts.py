# backend/app/routers/tts.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging
from pathlib import Path

from app.services.tts_service import tts_service
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tts", tags=["tts"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic модели для запросов
class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Текст для озвучки")
    language_id: str = Field(..., description="Код языка (ISO 639-1)")
    use_chatterbox: bool = Field(True, description="Использовать Chatterbox TTS")
    exaggeration: float = Field(0.5, ge=0.0, le=1.0, description="Уровень выразительности")
    cfg_weight: float = Field(0.5, ge=0.0, le=1.0, description="Вес конфигурации")
    audio_prompt_path: Optional[str] = Field(None, description="Путь к аудио-промпту для клонирования голоса")

class BatchTTSRequest(BaseModel):
    texts_and_langs: List[tuple[str, str]] = Field(..., description="Список кортежей (text, language_id)")
    use_chatterbox: bool = Field(True, description="Использовать Chatterbox TTS")
    exaggeration: float = Field(0.5, ge=0.0, le=1.0, description="Уровень выразительности")
    cfg_weight: float = Field(0.5, ge=0.0, le=1.0, description="Вес конфигурации")

class TTSResponse(BaseModel):
    success: bool
    audio_path: Optional[str] = None
    message: Optional[str] = None
    language_id: str
    text_preview: str

class BatchTTSResponse(BaseModel):
    success: bool
    results: Dict[str, Optional[str]]
    total_processed: int
    successful_count: int
    message: Optional[str] = None

class SupportedLanguagesResponse(BaseModel):
    languages: Dict[str, str]
    chatterbox_available: bool
    total_languages: int


@router.post("/generate", response_model=TTSResponse)
async def generate_tts(
    request: TTSRequest = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Генерирует аудиофайл для заданного текста
    
    - **text**: Текст для озвучки (1-1000 символов)
    - **language_id**: Код языка (например: 'en', 'ru', 'es')
    - **use_chatterbox**: Использовать Chatterbox TTS (по умолчанию True)
    - **exaggeration**: Уровень выразительности (0.0-1.0)
    - **cfg_weight**: Вес конфигурации (0.0-1.0)
    - **audio_prompt_path**: Путь к аудио для клонирования голоса (опционально)
    """
    try:
        logger.info(f"TTS запрос от пользователя {current_user.id}: '{request.text[:50]}...' ({request.language_id})")
        
        # Проверяем поддержку языка
        supported_languages = tts_service.get_supported_languages()
        if request.language_id not in supported_languages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Язык '{request.language_id}' не поддерживается. Доступные языки: {list(supported_languages.keys())}"
            )
        
        # Генерируем аудио
        audio_path = await tts_service.generate_audio(
            text=request.text,
            language_id=request.language_id,
            use_chatterbox=request.use_chatterbox,
            audio_prompt_path=request.audio_prompt_path,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight
        )
        
        if not audio_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось сгенерировать аудиофайл"
            )
        
        logger.info(f"TTS успешно: {audio_path}")
        
        return TTSResponse(
            success=True,
            audio_path=audio_path,
            language_id=request.language_id,
            text_preview=request.text[:50] + ("..." if len(request.text) > 50 else ""),
            message="Аудио успешно сгенерировано"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка TTS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post("/generate-batch", response_model=BatchTTSResponse)
async def generate_batch_tts(
    request: BatchTTSRequest = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Генерирует аудиофайлы для нескольких текстов параллельно
    
    - **texts_and_langs**: Список кортежей (text, language_id)
    - **use_chatterbox**: Использовать Chatterbox TTS
    - **exaggeration**: Уровень выразительности
    - **cfg_weight**: Вес конфигурации
    """
    try:
        logger.info(f"Batch TTS запрос от пользователя {current_user.id}: {len(request.texts_and_langs)} элементов")
        
        if len(request.texts_and_langs) > 20:  # Ограничение на количество
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Максимальное количество элементов в batch запросе: 20"
            )
        
        # Проверяем поддержку языков
        supported_languages = tts_service.get_supported_languages()
        for text, lang_id in request.texts_and_langs:
            if lang_id not in supported_languages:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Язык '{lang_id}' не поддерживается"
                )
        
        # Генерируем аудио параллельно
        results = await tts_service.generate_batch_audio(
            request.texts_and_langs,
            use_chatterbox=request.use_chatterbox,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight
        )
        
        successful_count = sum(1 for path in results.values() if path is not None)
        
        logger.info(f"Batch TTS завершен: {successful_count}/{len(request.texts_and_langs)} успешно")
        
        return BatchTTSResponse(
            success=True,
            results=results,
            total_processed=len(request.texts_and_langs),
            successful_count=successful_count,
            message=f"Обработано {successful_count} из {len(request.texts_and_langs)} элементов"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка Batch TTS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """
    Возвращает список поддерживаемых языков
    """
    try:
        languages = tts_service.get_supported_languages()
        
        return SupportedLanguagesResponse(
            languages=languages,
            chatterbox_available=hasattr(tts_service, 'english_model') or hasattr(tts_service, 'multilingual_model'),
            total_languages=len(languages)
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения языков: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить список языков"
        )


@router.get("/audio/{filename}")
async def get_audio_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Возвращает аудиофайл по имени
    
    - **filename**: Имя аудиофайла (например: 'tts_en_abc123.wav')
    """
    try:
        # Базовая проверка безопасности
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недопустимое имя файла"
            )
        
        # Путь к файлу
        base_dir = Path(__file__).parent.parent.parent
        audio_dir = base_dir / "frontend" / "assets" / "audio"
        file_path = audio_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Аудиофайл не найден"
            )
        
        return FileResponse(
            path=str(file_path),
            media_type="audio/wav",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения аудиофайла: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить аудиофайл"
        )


@router.delete("/cleanup")
async def cleanup_old_audio_files(
    max_age_days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """
    Очищает старые аудиофайлы (только для администраторов)
    
    - **max_age_days**: Максимальный возраст файлов в днях (по умолчанию 7)
    """
    try:
        # Проверяем права администратора (если есть такая логика)
        # if not current_user.is_admin:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Недостаточно прав для выполнения операции"
        #     )
        
        tts_service.cleanup_old_files(max_age_days)
        
        return {
            "success": True,
            "message": f"Очистка файлов старше {max_age_days} дней выполнена"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка очистки файлов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось выполнить очистку файлов"
        )


@router.get("/health")
async def tts_health_check():
    """
    Проверка состояния TTS сервиса
    """
    try:
        supported_languages = tts_service.get_supported_languages()
        
        return {
            "status": "healthy",
            "device": tts_service.device,
            "chatterbox_available": len(supported_languages) > 12,  # Chatterbox поддерживает 23 языка
            "supported_languages_count": len(supported_languages),
            "service": "TTS Service"
        }
        
    except Exception as e:
        logger.error(f"Ошибка health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "TTS Service"
        }