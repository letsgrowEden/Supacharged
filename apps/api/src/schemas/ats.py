from pydantic import BaseModel
from typing import List, Dict

# --- Pydantic Models for ATS Data Structure ---
# These models define the shape of the data returned by the ATSCreator agent.
# They act as a contract, ensuring the data is structured and validated.

class PropDetail(BaseModel):
    """Details for a single component prop."""
    type: str
    isOptional: bool
    options: List[str] | None

class ATSModel(BaseModel):
    """The Abstract Technical Specification for a component."""
    componentName: str
    description: str
    dependencies: List[str]
    internalDependencies: List[str]
    propsInterface: Dict[str, PropDetail]
    tags: List[str]
    rawCode: str
