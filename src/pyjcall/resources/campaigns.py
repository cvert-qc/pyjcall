from typing import Optional, Dict, Any, Iterator
from ..models.campaigns import ListCampaignsParams, CreateCampaignParams

class Campaigns:
    def __init__(self, client):
        self.client = client

    def list(
        self,
        page: Optional[str] = None,
        per_page: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all Sales Dialer campaigns.
        
        Args:
            page (str, optional): The page number to read
            per_page (str, optional): The number of results per page (default: 50, max: 100)
            
        Returns:
            Dict[str, Any]: List of campaigns with status and count
        """
        params = ListCampaignsParams(
            page=page,
            per_page=per_page
        )

        return self.client._make_request(
            method="POST",
            endpoint="/v1/autodialer/campaigns/list",
            json=params.model_dump(exclude_none=True)
        )

    def create(
        self,
        name: str,
        type: str,
        default_number: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a campaign in Sales Dialer.
        
        Args:
            name (str): The name of the campaign to create
            type (str): The type of campaign (autodial, predictive, or dynamic)
            default_number (str, optional): Default number to dial from for the campaign
            country_code (str, optional): Country code in ISO-2 format (ISO 3166-1 alpha-2)
            
        Returns:
            Dict[str, Any]: Response containing campaign_id and status
        """
        params = CreateCampaignParams(
            name=name,
            type=type,
            default_number=default_number,
            country_code=country_code
        )

        return self.client._make_request(
            method="POST",
            endpoint="/v1/autodialer/campaigns/create",
            json=params.model_dump(exclude_none=True)
        )

    def iter_all(
        self,
        max_items: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterate through all campaigns.
        Automatically handles pagination.
        
        Args:
            max_items (int, optional): Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual campaign records
        """
        json_data = ListCampaignsParams(
            per_page="100"  # Use maximum allowed per_page for efficiency
        ).model_dump(exclude_none=True)

        for item in self.client._paginate(
            method="POST",
            endpoint="/v1/autodialer/campaigns/list",
            json=json_data,
            page_key="page",
            per_page_key="per_page",
            items_key="data",
            max_items=max_items,
            start_page=1  # v1 API starts at page 1
        ):
            yield item
