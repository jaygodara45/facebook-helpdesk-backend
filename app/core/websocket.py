from typing import Dict, Set
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        # Store connections by chat_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = set()
        self.active_connections[chat_id].add(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: int):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].discard(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast_to_chat(self, chat_id: int, message: dict):
        if chat_id in self.active_connections:
            disconnected_ws = set()
            for websocket in self.active_connections[chat_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected_ws.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected_ws:
                self.disconnect(ws, chat_id)

# Create a global instance
manager = WebSocketManager() 