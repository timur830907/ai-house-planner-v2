from pydantic import BaseModel, Field
from typing import Optional

class GenerationRequest(BaseModel):
    building_width: float = Field(default=12.0, ge=3.0, le=50.0)
    building_length: float = Field(default=14.0, ge=3.0, le=50.0)
    num_rooms: int = Field(default=3, ge=1, le=10)
    shape_type: str = Field(default="rectangle")
    seed: Optional[int] = 0