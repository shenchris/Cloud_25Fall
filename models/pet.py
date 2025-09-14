from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field


class PetBase(BaseModel):
    name: str = Field(
        ...,
        description="Name of the pet.",
        json_schema_extra={"example": "Rex"},
    )
    species: str = Field(
        ...,
        description="Species of the pet (e.g., dog, cat).",
        json_schema_extra={"example": "Dog"},
    )
    age: Optional[int] = Field(
        None,
        description="Age of the pet in years.",
        json_schema_extra={"example": 5},
    )
    weight: Optional[float] = Field(
        None,
        description="Weight of the pet in kilograms.",
        json_schema_extra={"example": 30.5},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Rex",
                    "species": "Dog",
                    "age": 5,
                    "weight": 30.5,
                }
            ]
        }
    }


class PetCreate(PetBase):
    """Creation payload; ID is generated server-side but present in the base model."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Buddy",
                    "species": "Dog",
                    "age": 3,
                    "weight": 25.0,
                }
            ]
        }
    }


class PetUpdate(BaseModel):
    """Partial update; pet ID is taken from the path, not the body."""
    name: Optional[str] = Field(None, description="Name of the pet.", json_schema_extra={"example": "Rex"})
    species: Optional[str] = Field(None, description="Species of the pet.", json_schema_extra={"example": "Dog"})
    age: Optional[int] = Field(None, description="Age of the pet in years.", json_schema_extra={"example": 5})
    weight: Optional[float] = Field(None, description="Weight of the pet in kilograms.", json_schema_extra={"example": 30.5})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Rex", "age": 6},
                {"weight": 32.0},
            ]
        }
    }



class PetRead(PetBase):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )
    name: str = Field(
        ...,
        description="Name of the pet.",
        json_schema_extra={"example": "Rex"},
    )  
    species: str = Field(
        ...,
        description="Species of the pet.",
        json_schema_extra={"example": "Dog"},
    )
    age: Optional[int] = Field(
        None,
        description="Age of the pet in years.",
        json_schema_extra={"example": 5},
    )
    weight: Optional[float] = Field(
        None,
        description="Weight of the pet in kilograms.",
        json_schema_extra={"example": 30.5},
    )
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Pet ID.",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )   
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Rex",
                    "species": "Dog",
                    "age": 5,
                    "weight": 30.5,
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }

    }   

class PetDelete(PetBase):
    """Request model for deleting a Pet."""
    id: UUID = Field(..., description="Pet ID to delete.")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                }
            ]
        }
    }     