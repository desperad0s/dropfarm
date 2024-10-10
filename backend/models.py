from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

# Define your models here
class User(BaseModel):
    id: str  # Changed from uuid.UUID to str
    email: str

class UserStats(BaseModel):
    id: str  # Changed from uuid.UUID to str
    user_id: str  # Changed from uuid.UUID to str
    routine_runs: int
    total_earnings: float
    last_run: Optional[datetime]

class Routine(BaseModel):
    id: str  # Changed from uuid.UUID to str
    user_id: str  # Changed from uuid.UUID to str
    name: str
    steps: List[str]
    tokens_per_run: int

class BotStatus(BaseModel):
    id: str  # Changed from uuid.UUID to str
    user_id: str  # Changed from uuid.UUID to str
    is_initialized: bool
    is_running: bool
    current_mode: str
    updated_at: datetime