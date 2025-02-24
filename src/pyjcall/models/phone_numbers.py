from typing import Optional, List
from pydantic import BaseModel, Field

class ListPhoneNumbersParams(BaseModel):
    """Parameters for listing phone numbers"""
    justcall_line_name: Optional[str] = Field(
        None,
        description="Search by JustCall phone line name"
    )
    availability_setting: Optional[str] = Field(
        None,
        description="Filter by business hours setting (Always Open, Always Closed, Custom Hours)"
    )
    number_type: Optional[str] = Field(
        None,
        description="Filter by number type (local, mobile, toll_free)"
    )
    number_owner_id: Optional[int] = Field(
        None,
        description="Filter by agent who owns the numbers"
    )
    shared_agent_id: Optional[int] = Field(
        None,
        description="Filter by agent with whom numbers are shared"
    )
    shared_group_id: Optional[int] = Field(
        None,
        description="Filter by group with whom numbers are shared"
    )
    capabilities: Optional[str] = Field(
        None,
        description="Filter by capabilities (call, sms, mms)"
    )
    per_page: Optional[int] = Field(
        default=30,
        ge=1,
        le=100,
        description="Phone numbers per page (max: 100)"
    )
    page: Optional[int] = Field(
        None,
        description="Page number"
    )
    order: Optional[str] = Field(
        None,
        description="Sort order"
    ) 