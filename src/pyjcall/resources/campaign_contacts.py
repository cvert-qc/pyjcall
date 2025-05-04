from typing import Optional, Dict, Any, AsyncIterator, List
from ..models.campaign_contacts import (
    GetCustomFieldsParams,
    ListCampaignContactsParams,
    AddCampaignContactParams,
    RemoveCampaignContactParams
)

class CampaignContacts:
    def __init__(self, client):
        self.client = client

    async def get_custom_fields(self) -> Dict[str, Any]:
        """
        Get custom fields for campaign contacts.
        
        Returns:
            Dict[str, Any]: List of custom fields with their labels, keys, and types
        """
        params = GetCustomFieldsParams()

        return await self.client._make_request(
            method="POST",
            endpoint="/v1/autodialer/contacts/customfields",
            json=params.model_dump(exclude_none=True)
        )

    async def list(
        self,
        campaign_id: str
    ) -> Dict[str, Any]:
        """
        List all contacts in a campaign.
        
        Args:
            campaign_id (str): Campaign ID for which to list contacts
            
        Returns:
            Dict[str, Any]: List of contacts in the campaign
        """
        params = ListCampaignContactsParams(
            campaign_id=campaign_id
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v1/autodialer/campaigns/campaign-contacts",
            json=params.model_dump(exclude_none=True)
        )

    async def add(
        self,
        campaign_id: str,
        phone: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        custom_props: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a contact to a campaign.
        
        Args:
            campaign_id (str): Campaign ID to which the contact will be added
            phone (str): Formatted phone number of the contact with country code
            first_name (str, optional): Contact's first name
            last_name (str, optional): Contact's last name
            custom_props (Dict[str, Any], optional): Custom properties for the contact
            
        Returns:
            Dict[str, Any]: Added contact details
        """
        params = AddCampaignContactParams(
            campaign_id=campaign_id,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            custom_props=custom_props
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v1/autodialer/campaigns/add",
            json=params.model_dump(exclude_none=True)
        )

    async def remove(
        self,
        campaign_id: Optional[str] = None,
        phone: Optional[str] = None,
        all: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Remove a contact from a campaign.
        
        Args:
            campaign_id (str, optional): Campaign ID from which to remove the contact
            phone (str, optional): Phone number of the contact to remove
            all (bool, optional): If true, removes all contacts from the campaign
            
        Returns:
            Dict[str, Any]: Response with status and message
            
        Note:
            - If only phone is provided, the contact will be removed from all campaigns
            - If all=True, all contacts will be removed from the specified campaign
        """
        params = RemoveCampaignContactParams(
            campaign_id=campaign_id,
            phone=phone,
            all=all
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v1/autodialer/contacts/remove",
            json=params.model_dump(exclude_none=True)
        )

    async def iter_all(
        self,
        campaign_id: str,
        max_items: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Iterate through all contacts in a campaign.
        
        Args:
            campaign_id (str): Campaign ID for which to list contacts
            max_items (int, optional): Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual contact records
        """
        # For this endpoint, there doesn't seem to be pagination in the API
        # So we'll just get all contacts at once and yield them one by one
        response = await self.list(campaign_id=campaign_id)
        
        count = 0
        for item in response.get("data", []):
            if max_items and count >= max_items:
                return
            yield item
            count += 1
