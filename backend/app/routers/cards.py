from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import Optional
from app.services.enrichment import enrich_phrase

router = APIRouter(prefix="/cards", tags=["cards"])

class EnrichRequest(BaseModel):
    phrase: str
    keyword: str
    lang_code: str
    target_lang: str

@router.post("/enrich")
async def enrich(request: EnrichRequest = Body(...)):
    """
    Роут для обогащения: POST body с данными → вызов enrich_phrase.
    """
    return await enrich_phrase(
        request.phrase, 
        request.keyword, 
        request.lang_code, 
        request.target_lang
    )

# TODO: Добавь /save later (POST selected examples → save to DB)