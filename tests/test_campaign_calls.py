import pytest
from pyjcall import JustCallClient
from pyjcall.utils.exceptions import JustCallException

@pytest.mark.asyncio
async def test_list_campaign_calls(client, mock_api):
    """Test listing calls from JustCall Sales Dialer"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/calls/list",
        payload={
            "status": "success",
            "count": 1,
            "data": [
                {
                    "call_id": 1939963,
                    "user": "Prabhat Ranjan",
                    "campaign": {
                        "id": 1731647,
                        "name": "2019-07-18_09:06"
                    },
                    "contact_id": 2367512,
                    "from": "(989) 334-5741",
                    "to": "094307 18941",
                    "duration": "0s",
                    "time": "2019-07-18 14:37:22",
                    "direction": "Outgoing",
                    "disposition": "",
                    "notes": ""
                }
            ],
            "total": 11
        }
    )
    
    response = await client.CampaignCalls.list(campaign_id="1749984")
    assert response["status"] == "success"
    assert response["count"] == 1
    assert len(response["data"]) == 1
    assert response["data"][0]["call_id"] == 1939963
    assert response["data"][0]["user"] == "Prabhat Ranjan"
    assert response["data"][0]["campaign"]["id"] == 1731647
    assert response["total"] == 11

@pytest.mark.asyncio
async def test_list_campaign_calls_with_date_range(client, mock_api):
    """Test listing calls with date range"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/calls/list",
        payload={
            "status": "success",
            "count": 1,
            "data": [
                {
                    "call_id": 1939963,
                    "user": "Prabhat Ranjan",
                    "campaign": {
                        "id": 1731647,
                        "name": "2019-07-18_09:06"
                    },
                    "time": "2019-07-18 14:37:22"
                }
            ],
            "total": 1
        }
    )
    
    response = await client.CampaignCalls.list(
        campaign_id="1749984",
        start_date="2020-12-14",
        end_date="2020-12-15"
    )
    assert response["status"] == "success"
    assert response["count"] == 1
    assert len(response["data"]) == 1
    assert response["total"] == 1

@pytest.mark.asyncio
async def test_list_all_campaign_calls(client, mock_api):
    """Test listing calls from all campaigns"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/calls/list",
        payload={
            "status": "success",
            "count": 2,
            "data": [
                {
                    "call_id": 1939963,
                    "campaign": {
                        "id": 1731647,
                        "name": "Campaign 1"
                    }
                },
                {
                    "call_id": 1939964,
                    "campaign": {
                        "id": 1731648,
                        "name": "Campaign 2"
                    }
                }
            ],
            "total": 2
        }
    )
    
    # No campaign_id means all campaigns
    response = await client.CampaignCalls.list()
    assert response["status"] == "success"
    assert response["count"] == 2
    assert len(response["data"]) == 2
    assert response["data"][0]["campaign"]["name"] == "Campaign 1"
    assert response["data"][1]["campaign"]["name"] == "Campaign 2"

@pytest.mark.asyncio
async def test_list_campaign_calls_with_pagination(client, mock_api):
    """Test listing calls with pagination"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/calls/list",
        payload={
            "status": "success",
            "count": 1,
            "data": [
                {
                    "call_id": 1939965,
                    "user": "John Doe"
                }
            ],
            "total": 11
        }
    )
    
    response = await client.CampaignCalls.list(
        campaign_id="1749984",
        page="2",
        per_page="10"
    )
    assert response["status"] == "success"
    assert response["count"] == 1
    assert len(response["data"]) == 1
    assert response["data"][0]["call_id"] == 1939965

@pytest.mark.asyncio
async def test_iter_all_campaign_calls(client, mock_api):
    """Test iterating through all campaign calls"""
    # First page
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/calls/list",
        payload={
            "status": "success",
            "count": 2,
            "data": [
                {"call_id": 1939963, "user": "User 1"},
                {"call_id": 1939964, "user": "User 2"}
            ],
            "total": 3
        }
    )
    
    # Second page
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/calls/list",
        payload={
            "status": "success",
            "count": 1,
            "data": [
                {"call_id": 1939965, "user": "User 3"}
            ],
            "total": 3
        }
    )
    
    # Empty third page to end pagination
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/calls/list",
        payload={
            "status": "success",
            "count": 0,
            "data": [],
            "total": 3
        }
    )
    
    # Test iteration
    calls = []
    async for call in client.CampaignCalls.iter_all(campaign_id="1749984"):
        calls.append(call)
    
    assert len(calls) == 3
    assert calls[0]["call_id"] == 1939963
    assert calls[1]["call_id"] == 1939964
    assert calls[2]["call_id"] == 1939965

@pytest.mark.asyncio
async def test_iter_all_campaign_calls_with_max_items(client, mock_api):
    """Test iterating through campaign calls with max_items limit"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/calls/list",
        payload={
            "status": "success",
            "count": 3,
            "data": [
                {"call_id": 1939963, "user": "User 1"},
                {"call_id": 1939964, "user": "User 2"},
                {"call_id": 1939965, "user": "User 3"}
            ],
            "total": 3
        }
    )
    
    # Test iteration with max_items=2
    calls = []
    async for call in client.CampaignCalls.iter_all(
        campaign_id="1749984",
        max_items=2
    ):
        calls.append(call)
    
    assert len(calls) == 2
    assert calls[0]["call_id"] == 1939963
    assert calls[1]["call_id"] == 1939964
