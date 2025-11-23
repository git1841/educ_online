from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class UserType(str, Enum):
    FREE = "free"
    PRO = "pro"
    ADMIN = "admin"

class ContentType(str, Enum):
    PDF = "pdf"
    VIDEO = "video"
    IMAGE = "image"
    BOOK = "book"
    AUDIO = "audio"

class AccessType(str, Enum):
    FREE = "free"
    PRO = "pro"

class ConversationType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"

class UserRegister(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    phone: str
    password: str
    class_level: Optional[str] = None
    filiere: Optional[str] = None

class UserLogin(BaseModel):
    phone: str
    password: str

class AdminLogin(BaseModel):
    nom: str
    mot_de_passe: str

class ContentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    access_type: AccessType = AccessType.FREE
    class_level: Optional[str] = None
    subject: Optional[str] = None

class ConversationCreate(BaseModel):
    name: Optional[str] = None
    conversation_type: ConversationType
    participant_ids: Optional[List[int]] = None
    description: Optional[str] = None

class MessageCreate(BaseModel):
    conversation_id: int
    message_type: MessageType = MessageType.TEXT
    content: Optional[str] = None

class GroupRequest(BaseModel):
    group_name: str
    description: Optional[str] = None

class PublicationCreate(BaseModel):
    title: str
    content: str
    target_audience: str = "all"

class WarningCreate(BaseModel):
    user_id: int
    reason: str
    warning_type: str = "minor"

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    class_level: Optional[str] = None
    filiere: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class CallNotification(BaseModel):
    conversation_id: int
    call_type: str
    participant_ids: List[int]
    
    
# AJOUTER CES NOUVEAUX MODÈLES À LA FIN DE models.py

class ProUpgradeRequest(BaseModel):
    operator: str
    phone_number: str
    amount: float
    transaction_id: str

class GroupInviteRequest(BaseModel):
    group_id: int
    user_ids: List[int]