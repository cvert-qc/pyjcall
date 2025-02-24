import pytest
from pyjcall import JustCallClient
from pyjcall.utils.exceptions import JustCallException

@pytest.mark.asyncio
async def test_list_users(client, mock_api):
    """Test listing users/agents"""
    mock_api.get(
        "https://api.justcall.io/v2.1/users?available=0&order=desc&page=0&per_page=50",
        payload={
            "data": [
                {"id": 123, "name": "John Doe", "email": "john@example.com"},
                {"id": 124, "name": "Jane Smith", "email": "jane@example.com"}
            ]
        }
    )
    
    response = await client.Users.list()
    assert len(response["data"]) == 2
    assert response["data"][0]["id"] == 123

@pytest.mark.asyncio
async def test_list_users_with_filters(client, mock_api):
    """Test listing users with specific filters"""
    mock_api.get(
        "https://api.justcall.io/v2.1/users?available=1&group_id=5&order=asc&page=0&per_page=10",
        payload={
            "data": [
                {"id": 123, "name": "John Doe", "email": "john@example.com", "group_id": 5}
            ]
        }
    )
    
    response = await client.Users.list(
        available=True,
        group_id=5,
        order="asc",
        per_page=10
    )
    assert len(response["data"]) == 1
    assert response["data"][0]["group_id"] == 5

@pytest.mark.asyncio
async def test_get_user(client, mock_api):
    """Test getting a specific user by ID"""
    user_id = 123
    mock_api.get(
        f"https://api.justcall.io/v2.1/users/{user_id}",
        payload={"id": user_id, "name": "John Doe", "email": "john@example.com"}
    )
    
    response = await client.Users.get(user_id=user_id)
    assert response["id"] == user_id
    assert response["name"] == "John Doe" 