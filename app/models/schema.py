from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TextCorrectionRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Arabic text to be corrected",
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class TextCorrectionResponse(BaseModel):
    id: Optional[int] = None
    original_text: str
    corrected_text: str
    timestamp: str

    class Config:
        from_attributes = True


class CorrectionCreate(BaseModel):
    original_text: str
    corrected_text: str


class CorrectionInDB(BaseModel):
    id: int
    original_text: str
    corrected_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    model_loaded: bool


class ErrorResponse(BaseModel):
    error: str
    message: str
