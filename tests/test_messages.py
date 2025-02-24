import pytest
from pyjcall import JustCallClient
from pyjcall.utils.exceptions import JustCallException

@pytest.mark.asyncio
async def test_list_messages(client, mock_api):
    """Test listing SMS messages with pagination and filters"""
    mock_api.get(
        "https://api.justcall.io/v2.1/texts?order=desc&per_page=20&sort=id",
        payload={
            "data": [
                {"id": 123, "body": "Test message 1"},
                {"id": 124, "body": "Test message 2"}
            ]
        }
    )
    
    response = await client.Messages.list(per_page=20)
    assert len(response["data"]) == 2
    assert response["data"][0]["id"] == 123

@pytest.mark.asyncio
async def test_get_message(client, mock_api):
    """Test getting a specific SMS message by ID"""
    message_id = 123
    mock_api.get(
        f"https://api.justcall.io/v2.1/texts/{message_id}",
        payload={"id": message_id, "body": "Test message"}
    )
    
    response = await client.Messages.get(message_id=message_id)
    assert response["id"] == message_id
    assert response["body"] == "Test message"

@pytest.mark.asyncio
async def test_send_message(client, mock_api):
    """Test sending an SMS message"""
    mock_api.post(
        "https://api.justcall.io/v2.1/texts",
        payload={"id": 123, "status": "sent"}
    )
    
    response = await client.Messages.send(
        to="+14155552671",
        from_number="+14155552672",
        body="Test message"
    )
    assert response["status"] == "sent"

@pytest.mark.asyncio
async def test_send_new_message(client, mock_api):
    """Test sending a new SMS message"""
    mock_api.post(
        "https://api.justcall.io/v2.1/texts/new",
        payload={"id": 123, "status": "sent"}
    )
    
    response = await client.Messages.send_new(
        justcall_number="+14155552672",
        contact_number="+14155552671",
        body="Test message"
    )
    assert response["status"] == "sent"

@pytest.mark.asyncio
async def test_check_reply(client, mock_api):
    """Test checking for SMS replies"""
    mock_api.post(
        "https://api.justcall.io/v2.1/texts/checkreply",
        payload={
            "has_reply": True,
            "replies": [
                {"id": 123, "body": "Test reply"}
            ]
        }
    )
    
    response = await client.Messages.check_reply(
        contact_number="+14155552671",
        justcall_number="+14155552672"
    )
    assert response["has_reply"] == True
    assert len(response["replies"]) == 1

@pytest.mark.asyncio
async def test_error_handling(client, mock_api):
    """Test error handling for SMS endpoints"""
    mock_api.get(
        "https://api.justcall.io/v2.1/texts/999",
        status=404,
        payload={"message": "SMS not found"}
    )
    
    with pytest.raises(JustCallException) as exc:
        await client.Messages.get(message_id=999)
    assert "SMS not found" in str(exc.value) 