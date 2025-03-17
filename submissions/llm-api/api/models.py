from sqlmodel import SQLModel, Field
from typing import Optional

class ChatSession(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    user_email: str
    has_ended: bool = Field(default=False)

class ChatRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model: Optional[str] = Field(default=None)
    content: str
    role: str # user | system | assistant 
    session_id: str 
    timestamp: float # utc timestamp of chat message
