from typing import Optional, Dict
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class ListContactsParams(BaseModel):
    """Parameters for listing contacts"""
    page: str = Field(
        default="1",
        description="Page number (v1 API uses string)"
    )
    per_page: str = Field(
        default="50",
        description="Results per page (max: 100)"
    )

    @field_validator('per_page')
    def validate_per_page(cls, v):
        try:
            val = int(v)
            if not 1 <= val <= 100:
                raise ValueError("per_page must be between 1 and 100")
        except ValueError:
            raise ValueError("per_page must be a valid number")
        return v

class QueryContactsParams(BaseModel):
    """Parameters for querying contacts"""
    id: Optional[int] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    page: Optional[str] = "1"
    per_page: Optional[str] = "100"

    class Config:
        validate_assignment = True

    def model_dump(self, *args, **kwargs):
        # Ensure at least one search parameter is provided
        search_fields = ['id', 'firstname', 'lastname', 'phone', 'email', 'company', 'notes']
        if not any(getattr(self, field) for field in search_fields):
            raise ValueError("At least one search parameter is required")
        return super().model_dump(*args, **kwargs)

class OtherPhone(BaseModel):
    """Model for additional phone numbers"""
    label: str
    number: str

class UpdateContactParams(BaseModel):
    """Parameters for updating a contact"""
    id: int
    firstname: str
    phone: str
    lastname: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    other_phones: Optional[OtherPhone] = None

    class Config:
        validate_assignment = True

class CreateContactParams(BaseModel):
    """Parameters for creating a new contact"""
    firstname: str = Field(..., description="First name of the contact")
    phone: str = Field(..., description="Phone number of the contact")
    lastname: Optional[str] = Field(default=None, description="Last name of the contact")
    email: Optional[str] = Field(default=None, description="Email address of the contact")
    company: Optional[str] = Field(default=None, description="Company name")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    acrossteam: Optional[int] = Field(default=None, description="Create for all team members (1) or owner only (0)")
    agentid: Optional[int] = Field(default=None, description="Specific agent ID to create contact for")

    class Config:
        validate_assignment = True

class DeleteContactParams(BaseModel):
    """Parameters for deleting a contact"""
    id: int = Field(..., description="Unique id of the contact")

    class Config:
        validate_assignment = True

class ContactActionType(str, Enum):
    """Type of contact action"""
    BLACKLIST = "0"
    DND = "1"
    DNM = "2"

class ContactActionOperation(str, Enum):
    """Operation to perform"""
    REMOVE = "0"
    ADD = "1"

class ContactActionParams(BaseModel):
    """Parameters for contact actions (DND, blacklist, etc)"""
    number: str = Field(..., description="Phone number to act on")
    type: ContactActionType = Field(..., description="Type of action (blacklist, DND, DNM)")
    action: ContactActionOperation = Field(..., description="Action to perform (add/remove)")
    acrossteam: Optional[str] = Field(default="1", description="Apply across team (1) or individual (0)")

    class Config:
        validate_assignment = True 