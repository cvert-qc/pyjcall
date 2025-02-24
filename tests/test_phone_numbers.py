import pytest
from pyjcall import JustCallClient
from pyjcall.utils.exceptions import JustCallException

@pytest.mark.asyncio
async def test_list_phone_numbers(client, mock_api):
    """Test listing phone numbers with filters"""
    mock_api.get(
        "https://api.justcall.io/v2.1/phone-numbers?per_page=30",
        payload={
            "data": [
                {"id": 123, "phone_number": "+14155552671", "capabilities": ["call", "sms"]},
                {"id": 124, "phone_number": "+14155552672", "capabilities": ["call", "sms", "mms"]}
            ]
        }
    )
    
    response = await client.PhoneNumbers.list()
    assert len(response["data"]) == 2
    assert response["data"][0]["id"] == 123

@pytest.mark.asyncio
async def test_list_phone_numbers_with_filters(client, mock_api):
    """Test listing phone numbers with specific filters"""
    mock_api.get(
        "https://api.justcall.io/v2.1/phone-numbers?capabilities=sms&number_type=local&per_page=10",
        payload={
            "data": [
                {"id": 123, "phone_number": "+14155552671", "capabilities": ["call", "sms"]}
            ]
        }
    )
    
    response = await client.PhoneNumbers.list(
        capabilities="sms",
        number_type="local",
        per_page=10
    )
    assert len(response["data"]) == 1
    assert "sms" in response["data"][0]["capabilities"] 