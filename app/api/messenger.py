from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import hmac
import hashlib
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.messenger_service import MessengerService
from app.models.user import User
from app.models.chat import Chat, Message
from app.schemas.chat import ChatResponse, MessageResponse, SendMessageRequest
from app.core.config import settings

router = APIRouter()

# Your Facebook app secret from environment variables
FB_APP_SECRET = settings.FACEBOOK_APP_SECRET

def verify_facebook_signature(request: Request, payload: bytes) -> bool:
    """Verify that the webhook request came from Facebook"""
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature.startswith("sha256="):
        return False
    
    expected_signature = hmac.new(
        FB_APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature[7:], expected_signature)

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Handle the webhook verification from Facebook"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.FACEBOOK_VERIFY_TOKEN:
            return Response(content=challenge)
        return Response(status_code=403)

@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming webhook events from Facebook"""
    payload = await request.body()
    
    if not verify_facebook_signature(request, payload):
        raise HTTPException(status_code=403, detail="Invalid signature")
    print("Signature verified...")
    body = await request.json()
    print(f"body: {body}")
    if body.get("object") == "page":
        messenger_service = MessengerService(db)
        
        for entry in body.get("entry", []):
            page_id = entry.get("id")
            await messenger_service.handle_incoming_message(entry, page_id)
        
        return {"success": True}
    
    return Response(status_code=404)

@router.get("/chats", response_model=List[ChatResponse])
async def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chats for the current user"""
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).all()
    return chats

@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages for a specific chat"""
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    return messages

@router.post("/chats/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: int,
    message: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to a Facebook user"""
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messenger_service = MessengerService(db)
    message_id = messenger_service.send_message(chat_id, message.content)
    
    if not message_id:
        raise HTTPException(status_code=500, detail="Failed to send message")
    
    # Return the newly created message
    return db.query(Message).filter(Message.fb_message_id == message_id).first() 