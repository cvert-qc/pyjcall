from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ListMessagesParams(BaseModel):
    """Parameters for listing SMS messages"""
    from_datetime: Optional[datetime] = Field(
        None,
        description="Start datetime"
    )
    to_datetime: Optional[datetime] = Field(
        None,
        description="End datetime"
    )
    last_sms_id_fetched: Optional[int] = Field(
        None,
        description="ID of last SMS fetched in previous query"
    )
    contact_number: Optional[str] = Field(
        None,
        description="Contact number in E.164 format"
    )
    justcall_number: Optional[str] = Field(
        None,
        description="JustCall number in E.164 format"
    )
    sms_direction: Optional[str] = Field(
        None,
        description="Direction of SMS (Incoming/Outgoing)"
    )
    sms_content: Optional[str] = Field(
        None,
        description="Keywords in SMS content"
    )
    page: Optional[int] = Field(
        default=0,
        description="Page number (v2 API uses integer)"
    )
    per_page: int = Field(
        default=20,
        ge=1,
        le=100,
        description="SMS per page (max: 100)"
    )
    sort: str = Field(
        default="id",
        description="Field to sort by"
    )
    order: str = Field(
        default="desc",
        description="Sort order (asc/desc)"
    )

class SendMessageParams(BaseModel):
    """Parameters for sending an SMS message"""
    to: str = Field(
        ...,
        description="Recipient number in E.164 format"
    )
    from_number: str = Field(
        ...,
        description="Sender JustCall number in E.164 format"
    )
    body: str = Field(
        ...,
        description="SMS content"
    )
    media_url: Optional[str] = Field(
        None,
        description="URL of media to attach"
    )

class GetMessageParams(BaseModel):
    """Parameters for getting a single SMS message"""
    message_id: int = Field(
        ...,
        description="Unique ID of the SMS message"
    )

class CheckReplyParams(BaseModel):
    """Parameters for checking SMS replies"""
    contact_number: str = Field(
        ...,
        description="Contact number in E.164 format"
    )
    justcall_number: Optional[str] = Field(
        None,
        description="JustCall number in E.164 format"
    )

class SendNewMessageParams(BaseModel):
    """Parameters for sending a new SMS message"""
    justcall_number: str = Field(
        ...,
        description="JustCall number in E.164 format"
    )
    body: str = Field(
        ...,
        description="SMS content (max 1600 characters)"
    )
    contact_number: str = Field(
        ...,
        description="Recipient number in E.164 format"
    )
    media_url: Optional[str] = Field(
        None,
        description="Comma-separated URLs of media to attach (max 5)"
    )
    restrict_once: Optional[str] = Field(
        None,
        description="Set to 'Yes' to prevent duplicate SMS in 24 hours"
    ) 