from typing import Dict, Any, Optional, Iterator
from ..models.users import ListUsersParams

class Users:
    def __init__(self, client):
        self.client = client

    def list(
        self,
        available: Optional[bool] = None,
        group_id: Optional[int] = None,
        role: Optional[str] = None,
        page: Optional[int] = 0,
        per_page: Optional[int] = 50,
        order: Optional[str] = "desc"
    ) -> Dict[str, Any]:
        """
        List users/agents with optional filtering parameters.
        
        Args:
            available: Filter by agent availability (true for only available agents)
            group_id: Filter agents by User Group
            role: Filter agents by role
            page: Page number
            per_page: Users per page (max: 100)
            order: Sort order (asc/desc)
            
        Returns:
            Dict[str, Any]: Paginated list of users/agents
        """
        params = ListUsersParams(
            available=available,
            group_id=group_id,
            role=role,
            page=page,
            per_page=per_page,
            order=order
        )

        return self.client._make_request(
            method="GET",
            endpoint="/v2.1/users",
            params=params.model_dump(exclude_none=True)
        )

    def get(self, user_id: int) -> Dict[str, Any]:
        """
        Get details of a specific user/agent by ID.
        
        Args:
            user_id: Unique ID of the user/agent
            
        Returns:
            Dict[str, Any]: User details
        """
        return self.client._make_request(
            method="GET",
            endpoint=f"/v2.1/users/{user_id}"
        )

    def iter_all(
        self,
        available: Optional[bool] = None,
        group_id: Optional[int] = None,
        role: Optional[str] = None,
        order: Optional[str] = "desc",
        max_items: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterate through all users matching the filter criteria.
        Automatically handles pagination.
        
        Args:
            Same as list() method, except page and per_page are handled internally
            max_items: Maximum number of items to return (None for all)
            
        Yields:
            Dict[str, Any]: Individual user records
        """
        params = ListUsersParams(
            available=available,
            group_id=group_id,
            role=role,
            order=order,
            per_page=100  # Use maximum allowed per_page for efficiency
        )

        for item in self.client._paginate(
            method="GET",
            endpoint="/v2.1/users",
            params=params.model_dump(exclude_none=True),
            max_items=max_items
        ):
            yield item 