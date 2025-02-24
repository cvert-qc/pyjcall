from typing import Optional, List
from pydantic import BaseModel, Field, constr, field_validator
from enum import Enum
from decimal import Decimal

class CallDirection(str, Enum):
    """Enum for call direction to enforce correct casing"""
    INCOMING = "Incoming"
    OUTGOING = "Outgoing"

class ListCallsParams(BaseModel):
    """Parameters for listing calls"""
    fetch_queue_data: bool = Field(
        default=False,
        description="Fetch queue data like callback time, status, wait duration",
        serialization_alias="fetch_queue_data",
    )
    fetch_ai_data: bool = Field(
        default=False,
        description="Fetch coaching data by Justcall AI",
        serialization_alias="fetch_ai_data",
    )
    from_datetime: Optional[str] = Field(
        None,
        description="Start datetime (yyyy-mm-dd hh:mm:ss or yyyy-mm-dd)"
    )
    to_datetime: Optional[str] = Field(
        None,
        description="End datetime (yyyy-mm-dd hh:mm:ss or yyyy-mm-dd)"
    )
    contact_number: Optional[str] = Field(
        None,
        description="Contact number with country code"
    )
    justcall_number: Optional[str] = Field(
        None,
        description="JustCall number"
    )
    agent_id: Optional[int] = Field(
        None,
        description="ID of the agent"
    )
    ivr_digit: Optional[int] = Field(
        None,
        description="IVR digit for call routing filter"
    )
    call_direction: Optional[str] = Field(
        None,
        description="Call direction (Incoming/Outgoing - case sensitive)"
    )
    call_type: Optional[str] = Field(
        None,
        description="Call type (answered/unanswered/missed/voicemail/abandoned)"
    )
    call_traits: Optional[List[str]] = Field(
        None,
        description="Traits associated with calls"
    )
    page: Optional[int] = Field(
        None,
        description="Page number"
    )
    per_page: Optional[int] = Field(
        default=20,
        ge=20,
        le=100,
        description="Calls per page (min: 20, max: 100)"
    )
    sort: str = Field(
        default="id",
        description="Parameter to sort calls by"
    )
    order: str = Field(
        default="desc",
        description="Sort order (asc/desc)"
    )
    last_call_id_fetched: Optional[int] = Field(
        None,
        description="ID of last fetched call"
    )

class GetCallParams(BaseModel):
    """Parameters for getting a single call"""
    fetch_queue_data: bool = Field(
        default=False,
        description="Fetch queue data like callback time, status, wait duration",
        serialization_alias="fetch_queue_data"
    )
    fetch_ai_data: bool = Field(
        default=False,
        description="Fetch coaching data by Justcall AI",
        serialization_alias="fetch_ai_data"
    )

class UpdateCallParams(BaseModel):
    """Parameters for updating a call"""
    notes: Optional[str] = Field(
        None,
        description="Updated notes for the call (replaces existing notes)"
    )
    disposition_code: Optional[str] = Field(
        None,
        description="New/updated disposition code (must be from admin-created options)"
    )
    rating: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Rating from 0 to 5 (allows .5 decimals)",
        json_schema_extra={
            "examples": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
        }
    )

    @field_validator('rating')
    def validate_rating_decimal(cls, v):
        if v is not None:
            decimal_part = v % 1
            if decimal_part != 0 and decimal_part != 0.5:
                raise ValueError("Rating must be a whole number or end in .5")
        return v