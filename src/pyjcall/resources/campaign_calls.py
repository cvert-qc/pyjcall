from typing import Optional, Dict, Any, Iterator, Union, Literal
from datetime import date, datetime
from ..models.campaign_calls import ListCampaignCallsParams
from ..utils.datetime import to_api_date, convert_dict_datetimes

class CampaignCalls:
    def __init__(self, client):
        self.client = client

    def list(
        self,
        campaign_id: Optional[str] = None,
        from_datetime: Optional[Union[date, datetime]] = None,
        to_datetime: Optional[Union[date, datetime]] = None,
        fetch_ai_data: Optional[bool] = None,
        contact_number: Optional[str] = None,
        sales_dialer_number: Optional[str] = None,
        agent_id: Optional[str] = None,
        call_type: Optional[Literal["answered", "unanswered", "abandoned"]] = None,
        page: Optional[str] = None,
        per_page: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[Literal["asc", "desc"]] = None,
        last_call_id_fetched: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all calls made from JustCall Sales Dialer using v2.1 API.
        
        Args:
            campaign_id (str, optional): Campaign ID from which to fetch calls
            from_datetime (date/datetime, optional): Start date/time from which to fetch calls
            to_datetime (date/datetime, optional): End date/time from which to fetch calls
            fetch_ai_data (bool, optional): Set to true to fetch coaching data by Justcall AI
            contact_number (str, optional): Number of the contact for which calls are to be fetched
            sales_dialer_number (str, optional): Sales Dialer number for which calls are to be fetched
            agent_id (str, optional): ID of the agent for whom the calls are to be fetched
            call_type (str, optional): Type of calls (answered, unanswered, abandoned)
            page (str, optional): Page number to retrieve
            per_page (str, optional): Number of results per page (default: 20, max: 100)
            sort (str, optional): Parameter to sort the order of calls (default: 'id')
            order (str, optional): Order of calls: 'asc' or 'desc' (default: 'desc')
            last_call_id_fetched (str, optional): ID of the last call fetched in the previous query
            
        Returns:
            Dict[str, Any]: List of campaign calls with status, count, and total
        """
        params = ListCampaignCallsParams(
            campaign_id=campaign_id,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            fetch_ai_data=fetch_ai_data,
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

        response = self.client._make_request(
            method="GET",
            endpoint="/v2.1/sales_dialer/calls",
            params=params.model_dump(exclude_none=True)
        )
        
        # Convert date strings in response to Python date objects
        return convert_dict_datetimes(response)

    def iter_all(
        self,
        campaign_id: Optional[str] = None,
        from_datetime: Optional[Union[date, datetime]] = None,
        to_datetime: Optional[Union[date, datetime]] = None,
        fetch_ai_data: Optional[bool] = None,
        contact_number: Optional[str] = None,
        sales_dialer_number: Optional[str] = None,
        agent_id: Optional[str] = None,
        call_type: Optional[Literal["answered", "unanswered", "abandoned"]] = None,
        sort: Optional[str] = None,
        order: Optional[Literal["asc", "desc"]] = None,
        max_items: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterate through all calls made from JustCall Sales Dialer using v2.1 API.
        Automatically handles pagination.
        
        Args:
            campaign_id (str, optional): Campaign ID from which to fetch calls
            from_datetime (date/datetime, optional): Start date/time from which to fetch calls
            to_datetime (date/datetime, optional): End date/time from which to fetch calls
            fetch_ai_data (bool, optional): Set to true to fetch coaching data by Justcall AI
            contact_number (str, optional): Number of the contact for which calls are to be fetched
            sales_dialer_number (str, optional): Sales Dialer number for which calls are to be fetched
            agent_id (str, optional): ID of the agent for whom the calls are to be fetched
            call_type (str, optional): Type of calls (answered, unanswered, abandoned)
            sort (str, optional): Parameter to sort the order of calls (default: 'id')
            order (str, optional): Order of calls: 'asc' or 'desc' (default: 'desc')
            max_items (int, optional): Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual call records
        """
        params = ListCampaignCallsParams(
            campaign_id=campaign_id,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            fetch_ai_data=fetch_ai_data,
            contact_number=contact_number,
            sales_dialer_number=sales_dialer_number,
            agent_id=agent_id,
            call_type=call_type,
            sort=sort,
            order=order,
            per_page="100"  # Use maximum allowed per_page for efficiency
        ).model_dump(exclude_none=True)

        for item in self.client._paginate(
            method="GET",
            endpoint="/v2.1/sales_dialer/calls",
            params=params,
            page_key="page",
            per_page_key="per_page",
            items_key="data",
            max_items=max_items,
            start_page=1
        ):
            # Convert date strings in each item to Python date objects
            yield convert_dict_datetimes(item)
