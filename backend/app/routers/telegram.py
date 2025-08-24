from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import logging
from typing import Dict, Any

router = APIRouter(prefix="/telegram", tags=["telegram"])

logger = logging.getLogger(__name__)

class WebhookUpdate(BaseModel):
    """Telegram webhook update model"""
    update_id: int
    message: Dict[str, Any] = None
    callback_query: Dict[str, Any] = None
    inline_query: Dict[str, Any] = None

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram webhook endpoint.
    Receives updates from Telegram Bot API.
    """
    try:
        # Get raw request body
        body = await request.body()
        
        # Log the webhook request
        logger.info(f"Received Telegram webhook: {body.decode('utf-8')[:200]}...")
        
        # Parse JSON
        import json
        update_data = json.loads(body)
        
        # Process the update (for now just log it)
        logger.info(f"Telegram update received: {update_data.get('update_id')}")
        
        # Here you can add your bot logic:
        # - Handle /start command
        # - Handle button clicks
        # - Send responses back to users
        
        # For now, just return OK to acknowledge receipt
        return {"ok": True}
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/webhook")
async def webhook_info():
    """
    GET endpoint for webhook info (for debugging)
    """
    return {
        "message": "Telegram webhook endpoint",
        "method": "POST",
        "description": "This endpoint receives updates from Telegram Bot API"
    }