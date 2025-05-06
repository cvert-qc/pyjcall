from typing import Optional, Any, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, field_serializer, ConfigDict

class ListCampaignCallsParams(BaseModel):
    """Parameters for listing calls from JustCall Sales Dialer using v2 API"""
    
    model_config = ConfigDict(populate_by_name=True)
    campaign_id: Optional[str] = Field(
        None,
        description="Campaign ID for which to fetch calls"
    )
    fetch_ai_data: Optional[bool] = Field(
        None,
        description="Set to true to fetch coaching data by Justcall AI. Default is false"
    )
    from_datetime: Optional[datetime] = Field(
        None,
        description="Datetime starting from when the calls are to be fetched in user's timezone"
    )
    
    @field_serializer('from_datetime')
    def serialize_from_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")
    
    to_datetime: Optional[datetime] = Field(
        None,
        description="Datetime till when the calls are to be fetched in user's timezone"
    )
    
    @field_serializer('to_datetime')
    def serialize_to_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")
    
    contact_number: Optional[str] = Field(
        None,
        description="Number of the contact for which calls are to be fetched (with country code)"
    )
    sales_dialer_number: Optional[str] = Field(
        None,
        description="Sales Dialer number for which the calls are to be fetched"
    )
    agent_id: Optional[str] = Field(
        None,
        description="ID of the agent for whom the calls are to be fetched"
    )
    call_type: Optional[Literal['answered', 'unanswered', 'abandoned']] = Field(
        None,
        description="Type of calls to be fetched (answered, unanswered, abandoned)"
    )
    page: Optional[int] = Field(
        None,
        description="Page number for which calls are to be fetched"
    )
    per_page: Optional[int] = Field(
        None,
        description="Number of calls to be fetched per page. Default is 20, max is 100"
    )
    sort: Optional[str] = Field(
        None,
        description="Parameter to sort the order of calls. Default is 'id'"
    )
    order: Optional[Literal['asc', 'desc']] = Field(
        None,
        description="Order in which the calls list should appear based on the 'sort' parameter. Default is 'desc'"
    )
    last_call_id_fetched: Optional[str] = Field(
        None,
        description="Id of the last call fetched in the previous query to avoid duplicates"
    )
