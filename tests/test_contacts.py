import pytest
from unittest.mock import AsyncMock, patch
from pyjcall import JustCallClient
from pyjcall.models.contacts import CreateContactParams, UpdateContactParams, QueryContactsParams
from aioresponses import aioresponses

@pytest.fixture
def mock_api():
    with aioresponses() as m:
        yield m

@pytest.fixture
async def client():
    """Create a test client with mocked credentials"""
    async with JustCallClient("test_key", "test_secret") as client:
        yield client

@pytest.mark.asyncio
class TestContacts:
    """Test suite for Contacts module"""

    async def test_create_contact(self, client):
        """Test creating a new contact"""
        # Mock response data
        mock_response = {
            "status": "success",
            "id": 123456,
            "message": "Contact created successfully"
        }

        # Mock the _make_request method
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test creating a contact with minimum required fields
            result = await client.Contacts.create(
                firstname="John",
                phone="+15147290123"
            )
            
            # Verify the request was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['method'] == "POST"
            assert call_args[1]['endpoint'] == "/v1/contacts/new"
            
            # Verify response
            assert result == mock_response
            assert result['id'] == 123456

    async def test_create_contact_full(self, client):
        """Test creating a contact with all fields"""
        mock_response = {"status": "success", "id": 123456}

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.Contacts.create(
                firstname="John",
                phone="+15147290123",
                lastname="Doe",
                email="john@example.com",
                company="Test Corp",
                notes="Test notes",
                acrossteam=1
            )

            # Verify all fields were sent
            call_args = mock_request.call_args
            sent_data = call_args[1]['json']
            assert sent_data['firstname'] == "John"
            assert sent_data['phone'] == "+15147290123"
            assert sent_data['lastname'] == "Doe"
            assert sent_data['email'] == "john@example.com"
            assert sent_data['company'] == "Test Corp"
            assert sent_data['notes'] == "Test notes"
            assert sent_data['acrossteam'] == 1

    async def test_update_contact(self, client):
        """Test updating a contact"""
        mock_response = {"status": "success", "message": "Contact updated"}

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.Contacts.update(
                id=123456,
                firstname="John",
                phone="+15147290123",
                notes="Updated notes",
                other_phones={"Home": "+10987654321"}
            )

            # Verify request
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['method'] == "POST"
            assert call_args[1]['endpoint'] == "/v1/contacts/update"
            
            # Verify other_phones format
            sent_data = call_args[1]['json']
            assert sent_data['other_phones']['label'] == "Home"
            assert sent_data['other_phones']['number'] == "+10987654321"

    async def test_query_contacts(self, client):
        """Test querying contacts"""
        mock_response = {
            "contacts": [
                {"id": 1, "firstname": "John"},
                {"id": 2, "firstname": "John"}
            ]
        }

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.Contacts.query(firstname="John")
            
            # Verify request
            mock_request.assert_called_once()
            assert len(result['contacts']) == 2

    async def test_list_contacts(self, client, mock_api):
        """Test listing contacts"""
        mock_response = {
            "contacts": [
                {"id": 1, "firstname": "John"},
                {"id": 2, "firstname": "Jane"}
            ]
        }

        mock_api.post(
            "https://api.justcall.io/v1/contacts/list",
            payload=mock_response
        )

        result = await client.Contacts.list(per_page="20")
        assert len(result['contacts']) == 2

    async def test_iter_all_contacts(self, client):
        """Test iterating through all contacts"""
        mock_responses = [
            {
                "data": [
                    {"id": 1, "firstname": "John"},
                    {"id": 2, "firstname": "Jane"}
                ]
            },
            {
                "data": [
                    {"id": 3, "firstname": "Bob"}
                ]
            },
            {
                "data": []
            }
        ]

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = mock_responses

            contacts = []
            async for contact in client.Contacts.iter_all():
                contacts.append(contact)

            assert len(contacts) == 3
            assert contacts[0]['firstname'] == "John"
            assert contacts[2]['firstname'] == "Bob"

    async def test_create_contact_validation_missing_phone(self, client):
        """Test validation when creating contact without phone"""
        with pytest.raises(TypeError):
            await client.Contacts.create(
                firstname="John"
                # phone field omitted entirely
            )

    async def test_create_contact_validation_missing_firstname(self, client):
        """Test validation when creating contact without firstname"""
        with pytest.raises(TypeError):
            await client.Contacts.create(
                phone="+1234567890"
                # firstname field omitted entirely
            )

    @pytest.mark.parametrize("test_input", [
        {"firstname": "John"},  # omit phone
        {"phone": "+1234567890"},  # omit firstname
    ])
    async def test_create_contact_validation_parametrized(self, client, test_input):
        """Test validation when creating contacts with missing required fields"""
        with pytest.raises(TypeError):
            await client.Contacts.create(**test_input)

    async def test_update_contact_validation(self, client):
        """Test validation when updating contacts"""
        with pytest.raises(ValueError):
            await client.Contacts.update(
                id=123456,
                firstname="John",
                phone="+15147290123",
                other_phones={"Home": "+1234", "Work": "+5678"}  # Multiple other_phones not allowed
            )

    async def test_delete_contact(self, client):
        """Test deleting a contact"""
        mock_response = {
            "status": "success",
            "message": "Contact deleted successfully"
        }

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test deleting a contact
            result = await client.Contacts.delete(id=123456)
            
            # Verify the request was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['method'] == "POST"
            assert call_args[1]['endpoint'] == "/v1/contacts/delete"
            assert call_args[1]['json'] == {"id": 123456}
            
            # Verify response
            assert result == mock_response

    async def test_contact_action_dnd(self, client):
        """Test adding/removing contact to/from DND"""
        mock_response = {
            "status": "success",
            "message": "Number added to DND list successfully"
        }

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test adding to DND
            result = await client.Contacts.action(
                number="+15147290123",
                type="1",  # DND
                action="1"  # Add
            )
            
            # Verify request
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['method'] == "POST"
            assert call_args[1]['endpoint'] == "/v1/contacts/action"
            assert call_args[1]['json'] == {
                "number": "+15147290123",
                "type": "1",
                "action": "1",
                "acrossteam": "1"
            }
            
            # Verify response
            assert result == mock_response

    async def test_contact_action_blacklist(self, client):
        """Test adding/removing contact to/from blacklist"""
        mock_response = {
            "status": "success",
            "message": "Number added to blacklist successfully"
        }

        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test adding to blacklist for individual only
            result = await client.Contacts.action(
                number="+15147290123",
                type="0",  # Blacklist
                action="1",  # Add
                acrossteam="0"  # Individual only
            )
            
            # Verify request
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['json'] == {
                "number": "+15147290123",
                "type": "0",
                "action": "1",
                "acrossteam": "0"
            } 