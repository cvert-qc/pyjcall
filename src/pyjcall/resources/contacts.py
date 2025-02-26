from typing import Dict, Any, Optional, AsyncIterator, Union
from ..models.contacts import (
    ListContactsParams, 
    QueryContactsParams, 
    UpdateContactParams,
    CreateContactParams,
    OtherPhone,
    DeleteContactParams,
    ContactActionType,
    ContactActionOperation,
    ContactActionParams
)

class Contacts:
    def __init__(self, client):
        self.client = client

    async def list(
        self,
        page: Optional[str] = "1",
        per_page: Optional[str] = "50"
    ) -> Dict[str, Any]:
        """List contacts with optional filtering parameters"""
        params = ListContactsParams(
            page=page,
            per_page=per_page
        )
        
        return await self.client._make_request(
            method="POST",
            endpoint="/v1/contacts/list",
            json=params.model_dump(exclude_none=True)
        )

    async def iter_all(
        self,
        max_items: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Iterate through all contacts.
        Automatically handles pagination.
        
        Args:
            max_items: Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual contact records
        """
        params = ListContactsParams(
            page="1",  # Explicitly set page 1 for v1 API
            per_page="100"  # Use maximum allowed per_page for efficiency
        )

        async for item in self.client._paginate(
            method="POST",
            endpoint="/v1/contacts/list",
            json=params.model_dump(exclude_none=True),
            page_key="page",
            items_key="data",
            max_items=max_items,
            start_page=1  # Ensure pagination starts at page 1
        ):
            yield item

    async def query(
        self,
        id: Optional[int] = None,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        company: Optional[str] = None,
        notes: Optional[str] = None,
        page: Optional[str] = "1",
        per_page: Optional[str] = "100"
    ) -> Dict[str, Any]:
        """
        Query contacts based on search parameters.
        At least one search parameter is required.
        
        Args:
            id: Unique id of the contact
            firstname: First name of the contact
            lastname: Last name of the contact
            phone: Phone number of the contact
            email: Email address associated with the contact
            company: Company associated with the contact
            notes: Custom information associated with the contact
            page: The page number to read
            per_page: Number of results per page (max: 100)
            
        Returns:
            Dict[str, Any]: Matching contacts
            
        Raises:
            ValueError: If no search parameters are provided
        """
        params = QueryContactsParams(
            id=id,
            firstname=firstname,
            lastname=lastname,
            phone=phone,
            email=email,
            company=company,
            notes=notes,
            page=page,
            per_page=per_page
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v1/contacts/query",
            json=params.model_dump(exclude_none=True)
        )

    async def iter_query(
        self,
        id: Optional[int] = None,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        company: Optional[str] = None,
        notes: Optional[str] = None,
        max_items: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Iterate through all contacts matching the query parameters.
        Automatically handles pagination.
        At least one search parameter is required.
        
        Args:
            Same as query() method, except page and per_page are handled internally
            max_items: Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual contact records
            
        Raises:
            ValueError: If no search parameters are provided
        """
        params = QueryContactsParams(
            id=id,
            firstname=firstname,
            lastname=lastname,
            phone=phone,
            email=email,
            company=company,
            notes=notes,
            per_page="100"  # Use maximum allowed per_page for efficiency
        )

        async for item in self.client._paginate(
            method="POST",
            endpoint="/v1/contacts/query",
            json=params.model_dump(exclude_none=True),
            page_key="page",
            items_key="contacts",
            max_items=max_items,
            start_page=1  # Specify v1 API starts at page 1
        ):
            yield item 

    async def update(
        self,
        id: int,
        firstname: str,
        phone: str,
        lastname: Optional[str] = None,
        email: Optional[str] = None,
        company: Optional[str] = None,
        notes: Optional[str] = None,
        other_phones: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Update a contact's information.
        
        Args:
            id: Unique id of the contact
            firstname: First name of the contact
            phone: Phone number of the contact
            lastname: Last name of the contact
            email: Email address associated with the contact
            company: Company associated with the contact
            notes: Custom information to associate with the contact
            other_phones: Additional phone numbers as {label: number}
            
        Returns:
            Dict[str, Any]: Updated contact information
            
        Raises:
            ValueError: If required fields are missing
        """
        # Convert other_phones dict to OtherPhone model if provided
        other_phones_model = None
        if other_phones:
            if len(other_phones) != 1:
                raise ValueError("other_phones should contain exactly one phone number")
            label, number = next(iter(other_phones.items()))
            other_phones_model = OtherPhone(label=label, number=number)

        params = UpdateContactParams(
            id=id,
            firstname=firstname,
            phone=phone,
            lastname=lastname,
            email=email,
            company=company,
            notes=notes,
            other_phones=other_phones_model
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v1/contacts/update",
            json=params.model_dump(exclude_none=True)
        )

    async def create(
        self,
        firstname: str,
        phone: str,
        lastname: Optional[str] = None,
        email: Optional[str] = None,
        company: Optional[str] = None,
        notes: Optional[str] = None,
        acrossteam: Optional[int] = None,
        agentid: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new contact.
        
        Args:
            firstname: First name of the contact
            phone: Phone number of the contact
            lastname: Last name of the contact
            email: Email address associated with the contact
            company: Company associated with the contact
            notes: Custom information to associate with the contact
            acrossteam: 1 to create contact for all team members, 0 or None for account owner only
            agentid: Create contact only for specific agent ID
            
        Returns:
            Dict[str, Any]: Created contact information
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        params = CreateContactParams(
            firstname=firstname,
            phone=phone,
            lastname=lastname,
            email=email,
            company=company,
            notes=notes,
            acrossteam=acrossteam,
            agentid=agentid
        )

        res = await self.client._make_request(
            method="POST",
            endpoint="/v1/contacts/new",
            json=params.model_dump(exclude_none=True)
        ) 
        return res

    async def delete(self, id: int) -> Dict[str, Any]:
        """
        Delete a contact.
        
        Args:
            id: Unique id of the contact to delete
            
        Returns:
            Dict[str, Any]: Response indicating success/failure
            
        Raises:
            JustCallException: If deletion fails or contact doesn't exist
        """
        params = DeleteContactParams(id=id)

        return await self.client._make_request(
            method="POST",
            endpoint="/v1/contacts/delete",
            json=params.model_dump(exclude_none=True)
        )

    async def action(
        self,
        number: str,
        type: Union[str, ContactActionType],
        action: Union[str, ContactActionOperation],
        acrossteam: Optional[str] = "1"
    ) -> Dict[str, Any]:
        """
        Perform actions on a contact number (add/remove to/from DND, blacklist, etc).
        
        Args:
            number: Phone number to act on
            type: Type of action:
                "0" - Blacklist number
                "1" - Add to DND list
                "2" - Add to DNM list
            action: Action to perform:
                "0" - Remove from list
                "1" - Add to list
            acrossteam: Apply across team ("1") or individual ("0"), defaults to "1"
            
        Returns:
            Dict[str, Any]: Response indicating success/failure
            
        Raises:
            JustCallException: If the action fails
            ValueError: If parameters are invalid
        """
        params = ContactActionParams(
            number=number,
            type=type,
            action=action,
            acrossteam=acrossteam
        )

        return await self.client._make_request(
            method="POST",
            endpoint="/v1/contacts/action",
            json=params.model_dump(exclude_none=True)
        )