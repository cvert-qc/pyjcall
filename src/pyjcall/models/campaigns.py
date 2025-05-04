from typing import Optional, List
from pydantic import BaseModel, Field

class ListCampaignsParams(BaseModel):
    """Parameters for listing campaigns"""
    page: Optional[str] = Field(
        None,
        description="The page number to read"
    )
    per_page: Optional[str] = Field(
        None,
        description="The number of results per page (default: 50, max: 100)"
    )

class CreateCampaignParams(BaseModel):
    """Parameters for creating a campaign"""
    name: str = Field(
        ...,
        description="The name of the campaign to create"
    )
    type: str = Field(
        ...,
        description="The type of campaign (autodial, predictive, or dynamic)"
    )
    default_number: Optional[str] = Field(
        None,
        description="Default number to dial from for the campaign"
    )
    country_code: Optional[str] = Field(
        None,
        description="Country code in ISO-2 format (ISO 3166-1 alpha-2)"
    )
