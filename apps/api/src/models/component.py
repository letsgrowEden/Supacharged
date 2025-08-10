from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
import datetime

# Pydantic model for the 'design_kits' table
class DesignKit(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    personality_tags: Optional[List[str]] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# Pydantic model for the 'components' table
class Component(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kit_id: UUID
    name: str
    category: Optional[str] = None
    metadata: Dict[str, Any]  # This will hold the rich JSONB data from our AST analysis
    embedding: Optional[List[float]] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# Pydantic model for the 'user_themes' table
class UserTheme(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    config: Dict[str, Any] # This will hold the theme's CSS variables etc.
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)