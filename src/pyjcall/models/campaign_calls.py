from typing import Optional
from pydantic import BaseModel, Field

class ListCampaignCallsParams(BaseModel):
    """Parameters for listing calls from JustCall Sales Dialer"""
    campaign_id: Optional[str] = Field(
        None,
        description="Campaign ID from which to fetch calls (optional, if not provided all campaign calls will be fetched)"
    )
    start_date: Optional[str] = Field(
        None,
        description="Start date from which to fetch calls (format: YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        None,
        description="End date from which to fetch calls (format: YYYY-MM-DD)"
    )
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
