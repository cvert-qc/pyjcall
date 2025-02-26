from typing import Optional
from pydantic import BaseModel, Field

class ListUsersParams(BaseModel):
    """Parameters for listing users/agents"""
    available: Optional[bool] = Field(
        False,
        description="Filter by agent availability (true for only available agents)"
    )
    group_id: Optional[int] = Field(
        None,
        description="Filter agents by User Group"
    )
    role: Optional[str] = Field(
        None,
        description="Filter agents by role"
    )
    page: Optional[int] = Field(
        default=0,
        description="Page number (v2 API uses integer)"
    )
    per_page: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Users per page (max: 100)"
    )
    order: Optional[str] = Field(
        "desc",
        description="Sort order (asc/desc)"
    )

class GetUserParams(BaseModel):
    """Parameters for getting a single user"""
    user_id: int = Field(
        ...,
        description="Unique ID of the user/agent"
    ) 