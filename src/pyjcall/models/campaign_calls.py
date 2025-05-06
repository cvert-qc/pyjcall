from typing import Optional, Any
from datetime import date
from pydantic import BaseModel, Field, field_serializer, ConfigDict

class ListCampaignCallsParams(BaseModel):
    """Parameters for listing calls from JustCall Sales Dialer"""
    
    model_config = ConfigDict(populate_by_name=True)
    campaign_id: Optional[str] = Field(
        None,
        description="Campaign ID from which to fetch calls (optional, if not provided all campaign calls will be fetched)"
    )
    start_date: Optional[date] = Field(
        None,
        description="Start date from which to fetch calls"
    )
    
    @field_serializer('start_date')
    def serialize_start_date(self, value: Optional[date]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d")
    end_date: Optional[date] = Field(
        None,
        description="End date from which to fetch calls"
    )
    
    @field_serializer('end_date')
    def serialize_end_date(self, value: Optional[date]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d")
    order: Optional[str] = Field(
        None,
        description="Order of calls: 0 for ascending, 1 for descending. Default is ascending"
    )
    page: Optional[str] = Field(
        None,
        description="Page number to retrieve"
    )
    per_page: Optional[str] = Field(
        None,
        description="Number of results per page (default: 100, max: 100)"
    )
