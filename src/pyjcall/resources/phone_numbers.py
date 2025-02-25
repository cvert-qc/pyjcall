from typing import Dict, Any, Optional, AsyncIterator
from ..models.phone_numbers import ListPhoneNumbersParams

class PhoneNumbers:
    def __init__(self, client):
        self.client = client

    async def list(
        self,
        justcall_line_name: Optional[str] = None,
        availability_setting: Optional[str] = None,
        number_type: Optional[str] = None,
        number_owner_id: Optional[int] = None,
        shared_agent_id: Optional[int] = None,
        shared_group_id: Optional[int] = None,
        capabilities: Optional[str] = None,
        per_page: Optional[int] = 30,
        page: Optional[int] = None,
        order: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List phone numbers with optional filtering parameters.
        
        Args:
            justcall_line_name: Search by JustCall phone line name
            availability_setting: Filter by business hours setting (Always Open, Always Closed, Custom Hours)
            number_type: Filter by number type (local, mobile, toll_free)
            number_owner_id: Filter by agent who owns the numbers
            shared_agent_id: Filter by agent with whom numbers are shared
            shared_group_id: Filter by group with whom numbers are shared
            capabilities: Filter by capabilities (call, sms, mms)
            per_page: Phone numbers per page (max: 100)
            page: Page number
            order: Sort order
            
        Returns:
            Dict[str, Any]: Paginated list of phone numbers
        """
        params = ListPhoneNumbersParams(
            justcall_line_name=justcall_line_name,
            availability_setting=availability_setting,
            number_type=number_type,
            number_owner_id=number_owner_id,
            shared_agent_id=shared_agent_id,
            shared_group_id=shared_group_id,
            capabilities=capabilities,
            per_page=per_page,
            page=page,
            order=order
        )

        return await self.client._make_request(
            method="GET",
            endpoint="/v2.1/phone-numbers",
            params=params.model_dump(exclude_none=True)
        )

    async def iter_all(
        self,
        justcall_line_name: Optional[str] = None,
        availability_setting: Optional[str] = None,
        number_type: Optional[str] = None,
        number_owner_id: Optional[int] = None,
        shared_agent_id: Optional[int] = None,
        shared_group_id: Optional[int] = None,
        capabilities: Optional[str] = None,
        order: Optional[str] = None,
        max_items: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Iterate through all phone numbers matching the filter criteria.
        Automatically handles pagination.
        
        Args:
            Same as list() method, except page and per_page are handled internally
            max_items: Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual phone number records
        """
        params = ListPhoneNumbersParams(
            justcall_line_name=justcall_line_name,
            availability_setting=availability_setting,
            number_type=number_type,
            number_owner_id=number_owner_id,
            shared_agent_id=shared_agent_id,
            shared_group_id=shared_group_id,
            capabilities=capabilities,
            order=order,
            per_page=100  # Use maximum allowed per_page for efficiency
        )

        async for item in self.client._paginate(
            method="GET",
            endpoint="/v2.1/phone-numbers",
            params=params.model_dump(exclude_none=True),
            max_items=max_items
        ):
            yield item 