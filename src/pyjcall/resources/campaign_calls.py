from typing import Optional, Dict, Any, AsyncIterator, Literal
from datetime import date, datetime
from ..models.campaign_calls import ListCampaignCallsParams
from ..utils.datetime import to_api_date, convert_dict_datetimes

class CampaignCalls:
    def __init__(self, client):
        self.client = client

    async def list(
        self,
        campaign_id: Optional[str] = None,
        fetch_ai_data: Optional[bool] = None,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
        contact_number: Optional[str] = None,
        sales_dialer_number: Optional[str] = None,
        agent_id: Optional[str] = None,
        call_type: Optional[Literal['answered', 'unanswered', 'abandoned']] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[Literal['asc', 'desc']] = None,
        last_call_id_fetched: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all calls made from JustCall Sales Dialer using v2 API.
        
        Args:
            campaign_id (str, optional): Campaign ID for which to fetch calls
            fetch_ai_data (bool, optional): Set to true to fetch coaching data by Justcall AI
            from_datetime (datetime, optional): Datetime starting from when the calls are to be fetched
            to_datetime (datetime, optional): Datetime till when the calls are to be fetched
            contact_number (str, optional): Number of the contact for which calls are to be fetched
            sales_dialer_number (str, optional): Sales Dialer number for which the calls are to be fetched
            agent_id (str, optional): ID of the agent for whom the calls are to be fetched
            call_type (str, optional): Type of calls to be fetched ('answered', 'unanswered', 'abandoned')
            page (int, optional): Page number for which calls are to be fetched
            per_page (int, optional): Number of calls per page (default: 20, max: 100)
            sort (str, optional): Parameter to sort the order of calls (default: 'id')
            order (str, optional): Order of results ('asc' or 'desc', default: 'desc')
            last_call_id_fetched (str, optional): Id of the last call fetched in the previous query
            
        Returns:
            Dict[str, Any]: List of campaign calls with status, count, and data
        """
        params = ListCampaignCallsParams(
            campaign_id=campaign_id,
            fetch_ai_data=fetch_ai_data,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            contact_number=contact_number,
            sales_dialer_number=sales_dialer_number,
            agent_id=agent_id,
            call_type=call_type,
            page=page,
            per_page=per_page,
            sort=sort,
            order=order,
            last_call_id_fetched=last_call_id_fetched
        )

        response = await self.client._make_request(
            method="GET",
            endpoint="/v2.1/sales_dialer/calls",
            params=params.model_dump(exclude_none=True)
        )
        
        # Convert date strings in response to Python date objects
        return convert_dict_datetimes(response)

    async def iter_all(
        self,
        campaign_id: Optional[str] = None,
        fetch_ai_data: Optional[bool] = None,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
        contact_number: Optional[str] = None,
        sales_dialer_number: Optional[str] = None,
        agent_id: Optional[str] = None,
        call_type: Optional[Literal['answered', 'unanswered', 'abandoned']] = None,
        sort: Optional[str] = None,
        order: Optional[Literal['asc', 'desc']] = None,
        max_items: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Iterate through all calls made from JustCall Sales Dialer using v2 API.
        Automatically handles pagination.
        
        Args:
            campaign_id (str, optional): Campaign ID for which to fetch calls
            fetch_ai_data (bool, optional): Set to true to fetch coaching data by Justcall AI
            from_datetime (datetime, optional): Datetime starting from when the calls are to be fetched
            to_datetime (datetime, optional): Datetime till when the calls are to be fetched
            contact_number (str, optional): Number of the contact for which calls are to be fetched
            sales_dialer_number (str, optional): Sales Dialer number for which the calls are to be fetched
            agent_id (str, optional): ID of the agent for whom the calls are to be fetched
            call_type (str, optional): Type of calls to be fetched ('answered', 'unanswered', 'abandoned')
            sort (str, optional): Parameter to sort the order of calls (default: 'id')
            order (str, optional): Order of results ('asc' or 'desc', default: 'desc')
            max_items (int, optional): Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual call records
        """
        params = ListCampaignCallsParams(
            campaign_id=campaign_id,
            fetch_ai_data=fetch_ai_data,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            contact_number=contact_number,
            sales_dialer_number=sales_dialer_number,
            agent_id=agent_id,
            call_type=call_type,
            sort=sort,
            order=order,
            per_page=100  # Use maximum allowed per_page for efficiency
        ).model_dump(exclude_none=True)

        async for item in self.client._paginate(
            method="GET",
            endpoint="/v2.1/sales_dialer/calls",
            params=params,
            page_key="page",
            per_page_key="per_page",
            items_key="data",
            max_items=max_items,
            start_page=0  # v2 API starts at page 0
        ):
            # Convert date strings in each item to Python date objects
            yield convert_dict_datetimes(item)
