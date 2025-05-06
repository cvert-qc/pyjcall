from typing import Optional, Dict, Any, Iterator
from datetime import date
from ..models.campaign_calls import ListCampaignCallsParams
from ..utils.datetime import to_api_date, convert_dict_datetimes

class CampaignCalls:
    def __init__(self, client):
        self.client = client

    def list(
        self,
        campaign_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        order: Optional[str] = None,
        page: Optional[str] = None,
        per_page: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all calls made from JustCall Sales Dialer.
        
        Args:
            campaign_id (str, optional): Campaign ID from which to fetch calls
            start_date (date, optional): Start date from which to fetch calls
            end_date (date, optional): End date from which to fetch calls
            order (str, optional): Order of calls: 0 for ascending, 1 for descending
            page (str, optional): Page number to retrieve
            per_page (str, optional): Number of results per page (default: 100, max: 100)
            
        Returns:
            Dict[str, Any]: List of campaign calls with status, count, and total
            
        Note:
            If campaign_id is not provided, all calls from all campaigns will be fetched
        """
        params = ListCampaignCallsParams(
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date,
            order=order,
            page=page,
            per_page=per_page
        )

        response = self.client._make_request(
            method="POST",
            endpoint="/v1/autodialer/calls/list",
            json=params.model_dump(exclude_none=True)
        )
        
        # Convert date strings in response to Python date objects
        return convert_dict_datetimes(response)

    def iter_all(
        self,
        campaign_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        order: Optional[str] = None,
        max_items: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterate through all calls made from JustCall Sales Dialer.
        Automatically handles pagination.
        
        Args:
            campaign_id (str, optional): Campaign ID from which to fetch calls
            start_date (date, optional): Start date from which to fetch calls
            end_date (date, optional): End date from which to fetch calls
            order (str, optional): Order of calls: 0 for ascending, 1 for descending
            max_items (int, optional): Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual call records
            
        Note:
            If campaign_id is not provided, all calls from all campaigns will be fetched
        """
        json_data = ListCampaignCallsParams(
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date,
            order=order,
            per_page="100"  # Use maximum allowed per_page for efficiency
        ).model_dump(exclude_none=True)

        for item in self.client._paginate(
            method="POST",
            endpoint="/v1/autodialer/calls/list",
            json=json_data,
            page_key="page",
            per_page_key="per_page",
            items_key="data",
            max_items=max_items,
            start_page=1  # v1 API starts at page 1
        ):
            # Convert date strings in each item to Python date objects
            yield convert_dict_datetimes(item)
