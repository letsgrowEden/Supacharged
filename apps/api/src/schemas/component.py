from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

# --- Design Kit Schemas ---

# Data required to create a new Design Kit
class DesignKitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    personality_tags: Optional[List[str]] = None

# Data returned to the user when fetching a Design Kit
class DesignKitPublic(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True # Formerly orm_mode = True

# --- Component Schemas ---

# Data required to create a new Component (for our internal pipeline)
class ComponentCreate(BaseModel):
    kit_id: UUID
    name: str
    category: Optional[str] = None
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

# Data returned to the user when fetching a Component
class ComponentPublic(BaseModel):
    id: UUID
    name: str
    category: Optional[str] = None
    metadata: Dict[str, Any] # For now, we expose all metadata

    class Config:
        from_attributes = True