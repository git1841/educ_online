from fastapi import WebSocket
from typing import Dict, List, Set
import json

class ConnectionManager:
    def __init__(self):
        # Store active connections: {user_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store call connections: {call_id: {user_id: websocket}}
        self.call_connections: Dict[int, Dict[int, WebSocket]] = {}
        # Store conversation participants: {conversation_id: set(user_ids)}
        self.conversation_participants: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user's websocket"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a user's websocket"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].remove(conn)
    
    async def broadcast_to_conversation(self, message: dict, conversation_id: int, exclude_user: int = None):
        """Broadcast message to all users in a conversation"""
        if conversation_id in self.conversation_participants:
            for user_id in self.conversation_participants[conversation_id]:
                if exclude_user and user_id == exclude_user:
                    continue
                await self.send_personal_message(message, user_id)
    
    async def broadcast_to_multiple(self, message: dict, user_ids: List[int]):
        """Broadcast message to multiple users"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def add_to_conversation(self, conversation_id: int, user_id: int):
        """Add user to conversation participants"""
        if conversation_id not in self.conversation_participants:
            self.conversation_participants[conversation_id] = set()
        self.conversation_participants[conversation_id].add(user_id)
    
    def remove_from_conversation(self, conversation_id: int, user_id: int):
        """Remove user from conversation participants"""
        if conversation_id in self.conversation_participants:
            self.conversation_participants[conversation_id].discard(user_id)
    
    # Call-specific methods
    async def connect_call(self, websocket: WebSocket, call_id: int, user_id: int):
        """Connect user to a call"""
        await websocket.accept()
        if call_id not in self.call_connections:
            self.call_connections[call_id] = {}
        self.call_connections[call_id][user_id] = websocket
    
    def disconnect_call(self, call_id: int, user_id: int):
        """Disconnect user from a call"""
        if call_id in self.call_connections:
            if user_id in self.call_connections[call_id]:
                del self.call_connections[call_id][user_id]
            if not self.call_connections[call_id]:
                del self.call_connections[call_id]
    
    async def broadcast_to_call(self, message: dict, call_id: int, exclude_user: int = None):
        """Broadcast WebRTC signaling to call participants"""
        if call_id in self.call_connections:
            disconnected = []
            for user_id, connection in self.call_connections[call_id].items():
                if exclude_user and user_id == exclude_user:
                    continue
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(user_id)
            
            # Clean up disconnected
            for user_id in disconnected:
                self.disconnect_call(call_id, user_id)
    
    def get_call_participants(self, call_id: int) -> List[int]:
        """Get list of participants in a call"""
        if call_id in self.call_connections:
            return list(self.call_connections[call_id].keys())
        return []

# Global manager instance
manager = ConnectionManager()