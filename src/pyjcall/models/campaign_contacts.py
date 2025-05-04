from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class GetCustomFieldsParams(BaseModel):
    """Parameters for getting custom fields for campaign contacts"""
    pass  # No parameters needed for this endpoint

class ListCampaignContactsParams(BaseModel):
    """Parameters for listing contacts in a campaign"""
    campaign_id: str = Field(
        ...,
        description="Campaign ID for which to list contacts"
    )

class AddCampaignContactParams(BaseModel):
    """Parameters for adding a contact to a campaign"""
    campaign_id: str = Field(
        ...,
        description="Campaign ID to which the contact will be added"
    )
    first_name: Optional[str] = Field(
        None,
        description="Contact's first name"
    )
    last_name: Optional[str] = Field(
        None,
        description="Contact's last name"
    )
    phone: str = Field(
        ...,
        description="Formatted phone number of the contact with country code"
    )
    custom_props: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom properties for the contact (key is the ID of the custom field)"
    )

class RemoveCampaignContactParams(BaseModel):
    """Parameters for removing a contact from a campaign"""
    campaign_id: Optional[str] = Field(
        None,
        description="Campaign ID from which to remove the contact"
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number of the contact to remove"
    )
    all: Optional[bool] = Field(
        None,
        description="If true, removes all contacts from the campaign"
    )
