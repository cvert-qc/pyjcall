import pytest
from pyjcall import JustCallClient
from pyjcall.utils.exceptions import JustCallException

@pytest.mark.asyncio
async def test_list_campaigns(client, mock_api):
    """Test listing campaigns"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/list",
        payload={
            "status": "success",
            "count": "2",
            "data": [
                {
                    "id": 123452,
                    "name": "Outbound Sales"
                },
                {
                    "id": 123454,
                    "name": "Marketing"
                }
            ]
        }
    )
    
    response = await client.Campaigns.list()
    assert response["status"] == "success"
    assert response["count"] == "2"
    assert len(response["data"]) == 2
    assert response["data"][0]["id"] == 123452
    assert response["data"][0]["name"] == "Outbound Sales"

@pytest.mark.asyncio
async def test_list_campaigns_with_pagination(client, mock_api):
    """Test listing campaigns with pagination parameters"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/list",
        payload={
            "status": "success",
            "count": "1",
            "data": [
                {
                    "id": 123452,
                    "name": "Outbound Sales"
                }
            ]
        }
    )
    
    response = await client.Campaigns.list(page="2", per_page="10")
    assert response["status"] == "success"
    assert len(response["data"]) == 1
    assert response["data"][0]["id"] == 123452

@pytest.mark.asyncio
async def test_iter_all_campaigns(client, mock_api):
    """Test iterating through all campaigns"""
    # First page with page=1 in JSON body
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/list",
        payload={
            "status": "success",
            "count": "3",
            "data": [
                {"id": 123452, "name": "Outbound Sales"},
                {"id": 123454, "name": "Marketing"}
            ]
        }
    )
    
    # Second page with page=2 in JSON body
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/list",
        payload={
            "status": "success",
            "count": "1",
            "data": [
                {"id": 123456, "name": "Customer Success"}
            ]
        }
    )
    
    # Empty third page to end pagination with page=3 in JSON body
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/list",
        payload={
            "status": "success",
            "count": "0",
            "data": []
        }
    )
    
    # Test iteration
    campaigns = []
    async for campaign in client.Campaigns.iter_all():
        campaigns.append(campaign)
    
    assert len(campaigns) == 3
    assert campaigns[0]["id"] == 123452
    assert campaigns[1]["id"] == 123454
    assert campaigns[2]["id"] == 123456

@pytest.mark.asyncio
async def test_iter_all_campaigns_with_max_items(client, mock_api):
    """Test iterating through campaigns with max_items limit"""
    # First page with multiple items
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/list",
        payload={
            "status": "success",
            "count": "3",
            "data": [
                {"id": 123452, "name": "Outbound Sales"},
                {"id": 123454, "name": "Marketing"},
                {"id": 123456, "name": "Customer Success"}
            ]
        }
    )
    
    # Test iteration with max_items=2
    campaigns = []
    async for campaign in client.Campaigns.iter_all(max_items=2):
        campaigns.append(campaign)
    
    assert len(campaigns) == 2
    assert campaigns[0]["id"] == 123452
    assert campaigns[1]["id"] == 123454

@pytest.mark.asyncio
async def test_create_campaign(client, mock_api):
    """Test creating a campaign"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/create",
        payload={
            "status": "success",
            "campaign_id": "18273803"
        }
    )
    
    response = await client.Campaigns.create(
        name="November Lead Campaign",
        type="autodial",
        default_number="4387290927"
    )
    
    assert response["status"] == "success"
    assert response["campaign_id"] == "18273803"

@pytest.mark.asyncio
async def test_create_campaign_with_country_code(client, mock_api):
    """Test creating a campaign with country code"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/create",
        payload={
            "status": "success",
            "campaign_id": "18273804"
        }
    )
    
    response = await client.Campaigns.create(
        name="International Campaign",
        type="predictive",
        default_number="4387290928",
        country_code="CA"
    )
    
    assert response["status"] == "success"
    assert response["campaign_id"] == "18273804"
