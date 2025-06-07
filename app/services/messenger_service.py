import requests
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pytz

from app.models.chat import Chat, Message
from app.models.user import User
from app.models.facebook_page import FacebookPage
from sqlalchemy.orm import joinedload

class MessengerService:
    def __init__(self, db: Session):
        self.db = db
        self.fb_api_version = "v18.0"
        self.fb_graph_url = f"https://graph.facebook.com/{self.fb_api_version}"

    async def handle_incoming_message(self, webhook_event: Dict[str, Any], page_id: str) -> Optional[Message]:
        """Handle incoming message from Facebook Messenger webhook"""
        messaging = webhook_event.get("messaging", [{}])[0]
        sender_id = messaging.get("sender", {}).get("id")
        recipient_id = messaging.get("recipient", {}).get("id")
        message = messaging.get("message", {})
        print("Extract relevant things from webhook data...")
        if not sender_id or not message:
            return None

        user = self.db.query(User).join(FacebookPage).filter(FacebookPage.id == page_id).first()
        
        if not user:
            return None
        # Get or create chat
        chat = self.get_or_create_chat(user.id, sender_id)
        
        # Convert UTC timestamp to IST
        utc_timestamp = datetime.fromtimestamp(messaging.get("timestamp", 0) / 1000)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_timestamp = utc_timestamp.astimezone(ist_timezone)
        
        # Create message
        new_message = Message(
            chat_id=chat.id,
            content=message.get("text", ""),
            message_type="incoming",
            fb_message_id=message.get("mid"),
            timestamp=ist_timestamp
        )
        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)
        
        return new_message

    def send_message(self, chat_id: int, message_text: str) -> Optional[str]:
        """Send message to Facebook user"""
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            return None

        user = self.db.query(User).filter(User.id == chat.user_id).first()
        if not user or not user.fb_page_token:
            return None

        url = f"{self.fb_graph_url}/me/messages"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "recipient": {"id": chat.fb_user_id},
            "message": {"text": message_text}
        }

        response = requests.post(
            url,
            headers=headers,
            json=data,
            params={"access_token": user.fb_page_token}
        )

        if response.status_code == 200:
            # Save the sent message with IST timestamp
            ist_timezone = pytz.timezone('Asia/Kolkata')
            ist_timestamp = datetime.now(ist_timezone)
            
            new_message = Message(
                chat_id=chat.id,
                content=message_text,
                message_type="outgoing",
                fb_message_id=response.json().get("message_id"),
                timestamp=ist_timestamp
            )
            self.db.add(new_message)
            self.db.commit()
            return response.json().get("message_id")
        
        return None

    def get_or_create_chat(self, user_id: int, fb_user_id: str) -> Chat:
        """Get existing chat or create new one"""
        # Get the most recent chat and its last message
        chat = (
            self.db.query(Chat)
            .filter(
                Chat.user_id == user_id,
                Chat.fb_user_id == fb_user_id
            )
            .order_by(Chat.created_at.desc())
            .first()
        )

        create_new_chat = False
        if not chat:
            create_new_chat = True
        else:
            # Get the last message from this chat
            last_message = (
                self.db.query(Message)
                .filter(Message.chat_id == chat.id)
                .order_by(Message.timestamp.desc())
                .first()
            )
            
            # Create new chat if last message is more than 24 hours old
            if last_message:
                time_since_last_message = datetime.utcnow() - last_message.timestamp
                if time_since_last_message > timedelta(hours=24):
                    create_new_chat = True
            else:
                # If chat exists but has no messages, use chat creation time
                time_since_chat_created = datetime.utcnow() - chat.created_at
                if time_since_chat_created > timedelta(hours=24):
                    create_new_chat = True

        if create_new_chat:
            # Get user info from Facebook
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.fb_page_token:
                user_info = self.get_fb_user_info(fb_user_id, user.fb_page_token)
                fb_user_name = user_info.get("name", "Unknown User")
            else:
                fb_user_name = "Unknown User"

            chat = Chat(
                user_id=user_id,
                fb_user_id=fb_user_id,
                fb_user_name=fb_user_name
            )
            self.db.add(chat)
            self.db.commit()

        return chat

    def get_fb_user_info(self, user_id: str, access_token: str) -> Dict[str, Any]:
        """Get Facebook user information"""
        url = f"{self.fb_graph_url}/{user_id}"
        response = requests.get(
            url,
            params={
                "access_token": access_token,
                "fields": "name,profile_pic"
            }
        )
        return response.json() if response.status_code == 200 else {} 