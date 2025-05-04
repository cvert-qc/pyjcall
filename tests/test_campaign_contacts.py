import pytest
from pyjcall import JustCallClient
from pyjcall.utils.exceptions import JustCallException

@pytest.mark.asyncio
async def test_get_custom_fields(client, mock_api):
    """Test getting custom fields for campaign contacts"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/contacts/customfields",
        payload={
            "status": "success",
            "data": [
                {
                    "label": "membership_status",
                    "key": 1090960,
                    "type": "string"
                },
                {
                    "label": "Zip Code",
                    "key": 1091095,
                    "type": "string"
                }
            ]
        }
    )
    
    response = await client.CampaignContacts.get_custom_fields()
    assert response["status"] == "success"
    assert len(response["data"]) == 2
    assert response["data"][0]["label"] == "membership_status"
    assert response["data"][0]["key"] == 1090960
    assert response["data"][0]["type"] == "string"

@pytest.mark.asyncio
async def test_list_campaign_contacts(client, mock_api):
    """Test listing contacts in a campaign"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/campaign-contacts",
        payload={
            "status": "success",
            "count": 2,
            "data": [
                {
                    "id": 26341595,
                    "name": "John Doe",
                    "email": "",
                    "address": "",
                    "phone": "xxx-xxx-0101",
                    "1739461": "46872",
                    "1739462": None
                },
                {
                    "id": 26341596,
                    "name": "Jane Doe",
                    "email": "",
                    "address": "",
                    "phone": "xxx-xxx-8692",
                    "1739461": "7973",
                    "1739462": None
                }
            ]
        }
    )
    
    response = await client.CampaignContacts.list(campaign_id="181449")
    assert response["status"] == "success"
    assert response["count"] == 2
    assert len(response["data"]) == 2
    assert response["data"][0]["id"] == 26341595
    assert response["data"][0]["name"] == "John Doe"
    assert response["data"][1]["id"] == 26341596
    assert response["data"][1]["name"] == "Jane Doe"

@pytest.mark.asyncio
async def test_add_campaign_contact(client, mock_api):
    """Test adding a contact to a campaign"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/add",
        payload={
            "id": 21001,
            "name": "John Smith",
            "phone": "1256256256"
        }
    )
    
    response = await client.CampaignContacts.add(
        campaign_id="1234213",
        first_name="John",
        last_name="Smith",
        phone="+1 256 256 256",
        custom_props={
            "10909": "true",
            "10910": "Bathilda Collins",
            "10911": "Subscribed"
        }
    )
    
    assert response["id"] == 21001
    assert response["name"] == "John Smith"
    assert response["phone"] == "1256256256"

@pytest.mark.asyncio
async def test_remove_campaign_contact(client, mock_api):
    """Test removing a contact from a campaign"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/contacts/remove",
        payload={
            "status": "success",
            "message": "The contact has been removed successfully."
        }
    )
    
    response = await client.CampaignContacts.remove(
        campaign_id="1234213",
        phone="+1 256 256 256"
    )
    
    assert response["status"] == "success"
    assert response["message"] == "The contact has been removed successfully."

@pytest.mark.asyncio
async def test_remove_all_campaign_contacts(client, mock_api):
    """Test removing all contacts from a campaign"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/contacts/remove",
        payload={
            "status": "success",
            "message": "All contacts have been removed successfully."
        }
    )
    
    response = await client.CampaignContacts.remove(
        campaign_id="1234213",
        all=True
    )
    
    assert response["status"] == "success"
    assert response["message"] == "All contacts have been removed successfully."

@pytest.mark.asyncio
async def test_iter_all_campaign_contacts(client, mock_api):
    """Test iterating through all contacts in a campaign"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/campaign-contacts",
        payload={
            "status": "success",
            "count": 2,
            "data": [
                {
                    "id": 26341595,
                    "name": "John Doe",
                    "phone": "xxx-xxx-0101"
                },
                {
                    "id": 26341596,
                    "name": "Jane Doe",
                    "phone": "xxx-xxx-8692"
                }
            ]
        }
    )
    
    contacts = []
    async for contact in client.CampaignContacts.iter_all(campaign_id="181449"):
        contacts.append(contact)
    
    assert len(contacts) == 2
    assert contacts[0]["id"] == 26341595
    assert contacts[1]["id"] == 26341596

@pytest.mark.asyncio
async def test_iter_all_campaign_contacts_with_max_items(client, mock_api):
    """Test iterating through campaign contacts with max_items limit"""
    mock_api.post(
        "https://api.justcall.io/v1/autodialer/campaigns/campaign-contacts",
        payload={
            "status": "success",
            "count": 2,
            "data": [
                {
                    "id": 26341595,
                    "name": "John Doe",
                    "phone": "xxx-xxx-0101"
                },
                {
                    "id": 26341596,
                    "name": "Jane Doe",
                    "phone": "xxx-xxx-8692"
                }
            ]
        }
    )
    
    contacts = []
    async for contact in client.CampaignContacts.iter_all(
        campaign_id="181449",
        max_items=1
    ):
        contacts.append(contact)
    
    assert len(contacts) == 1
    assert contacts[0]["id"] == 26341595
