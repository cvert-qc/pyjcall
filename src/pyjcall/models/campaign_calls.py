from typing import Optional, Any, Union, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, field_serializer, ConfigDict

class ListCampaignCallsParams(BaseModel):
    """Parameters for listing calls from JustCall Sales Dialer using v2.1 API"""
    
    model_config = ConfigDict(populate_by_name=True)
    campaign_id: Optional[str] = Field(
        None,
        description="Campaign ID of the Campaign for which you wish to fetch the calls"
    )
    fetch_ai_data: Optional[bool] = Field(
        None,
        description="Set to true to fetch coaching data by Justcall AI. Default is false"
    )
    from_datetime: Optional[Union[date, datetime]] = Field(
        None,
        description="Datetime starting from when the calls are to be fetched in user's timezone"
    )
    
    @field_serializer('from_datetime')
    def serialize_from_datetime(self, value: Optional[Union[date, datetime]]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value.strftime("%Y-%m-%d")
        
    to_datetime: Optional[Union[date, datetime]] = Field(
        None,
        description="Datetime till when the calls are to be fetched in user's timezone"
    )
    
    @field_serializer('to_datetime')
    def serialize_to_datetime(self, value: Optional[Union[date, datetime]]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value.strftime("%Y-%m-%d")
        
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
    call_type: Optional[Literal["answered", "unanswered", "abandoned"]] = Field(
        None,
        description="Type of calls (answered, unanswered, abandoned) that need to be fetched"
    )
    page: Optional[str] = Field(
        None,
        description="Page number for which calls are to be fetched"
    )
    per_page: Optional[str] = Field(
        None,
        description="Number of calls to be fetched per page (default: 20, max: 100)"
    )
    sort: Optional[str] = Field(
        None,
        description="Parameter to sort the order of calls. Default is 'id'"
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        None,
        description="Order in which the calls list should appear. Default is 'desc'"
    )
    last_call_id_fetched: Optional[str] = Field(
        None,
        description="ID of the last call fetched in the previous query"
    )
