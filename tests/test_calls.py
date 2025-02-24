import asyncio
import os
import dotenv
from pyjcall import JustCallClient
from pyjcall.utils.exceptions import JustCallException
import pytest
from aioresponses import aioresponses

@pytest.fixture
def mock_api():
    with aioresponses() as m:
        yield m

@pytest.fixture
async def client():
    return JustCallClient(api_key="test_key", api_secret="test_secret")

async def test_calls():
    """Test all calls endpoints in sequence"""
    api_key = os.getenv("JUSTCALL_API_KEY")
    api_secret = os.getenv("JUSTCALL_API_SECRET")
    if not api_key or not api_secret:
        raise ValueError("Please set JUSTCALL_API_KEY and JUSTCALL_API_SECRET environment variables")

    try:
        async with JustCallClient(api_key=api_key, api_secret=api_secret) as client:
            # 1. List calls to get an ID
            print("\nFetching calls...")
            calls = await client.Calls.list(
                per_page=20,
                call_direction="Incoming"
            )
            print(f"Retrieved {len(calls.get('data', []))} calls")

            # Get the first call ID for further operations
            if not calls.get('data'):
                print("No calls found to test with!")
                return
            
            call_id = calls['data'][0]['id']
            print(f"\nUsing call ID: {call_id} for further tests")

            # 2. Get specific call details
            print("\nFetching specific call details...")
            call_details = await client.Calls.get(
                call_id=call_id,
                fetch_queue_data=True
            )
            print("Retrieved call details")

            # 3. Update call
            print("\nUpdating call...")
            updated_call = await client.Calls.update(
                call_id=call_id,
                rating=4.5,
                notes="Test note from SDK"
            )
            print("Call updated successfully")

            # 4. Get call journey
            print("\nFetching call journey...")
            journey = await client.Calls.get_journey(call_id=call_id)
            print("Retrieved call journey")

            # 5. Get voice agent data
            print("\nFetching voice agent data...")
            try:
                voice_data = await client.Calls.get_voice_agent_data(call_id=call_id)
                print("Retrieved voice agent data")
            except JustCallException as e:
                if "Resource not found" in str(e):
                    print("Voice agent data not available for this call (feature might not be enabled)")
                else:
                    raise  # Re-raise if it's a different error

            # 6. Download recording
            print("\nDownloading call recording...")
            try:
                recording = await client.Calls.download_recording(call_id=call_id)
                print(f"Downloaded recording: {len(recording)} bytes")
            except Exception as e:
                print(f"Could not download recording: {str(e)}")

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

@pytest.mark.asyncio
async def test_list_calls(client, mock_api):
    mock_api.get(
        "https://api.justcall.io/v2.1/calls?fetch_ai_data=0&fetch_queue_data=0&order=desc&per_page=20&sort=id",
        payload={
            "data": [
                {"id": 123, "direction": "Incoming"},
                {"id": 124, "direction": "Outgoing"}
            ]
        }
    )
    
    response = await client.Calls.list(per_page=20)
    assert len(response["data"]) == 2
    assert response["data"][0]["id"] == 123

@pytest.mark.asyncio
async def test_get_call(client, mock_api):
    call_id = 123
    # Mock both with and without query parameters
    mock_api.get(
        f"https://api.justcall.io/v2.1/calls/{call_id}?fetch_ai_data=0&fetch_queue_data=0",
        payload={"id": call_id, "direction": "Incoming"}
    )
    mock_api.get(
        f"https://api.justcall.io/v2.1/calls/{call_id}",
        payload={"id": call_id, "direction": "Incoming"}
    )
    
    response = await client.Calls.get(call_id=call_id)
    assert response["id"] == call_id

async def test_update_call(client, mock_api):
    call_id = 123
    mock_api.put(
        f"https://api.justcall.io/v2.1/calls/{call_id}",
        payload={"id": call_id, "rating": 4.5}
    )
    
    response = await client.Calls.update(
        call_id=call_id,
        rating=4.5,
        notes="Test note"
    )
    assert response["rating"] == 4.5

async def test_get_voice_agent_data_not_found(client, mock_api):
    call_id = 123
    mock_api.get(
        f"https://api.justcall.io/v2.1/calls/{call_id}/voice-agent",
        status=404,
        payload={"message": "Resource not found"}
    )
    
    with pytest.raises(JustCallException) as exc:
        await client.Calls.get_voice_agent_data(call_id=call_id)
    assert "Resource not found" in str(exc.value)

async def test_download_recording(client, mock_api):
    call_id = 123
    mock_api.get(
        f"https://api.justcall.io/v2.1/calls/{call_id}/recording/download",
        body=b"fake audio data",
        content_type="audio/mpeg"
    )
    
    response = await client.Calls.download_recording(call_id=call_id)
    assert response == b"fake audio data"

if __name__ == "__main__":
    asyncio.run(test_calls()) 