#!/usr/bin/env python3
"""
Example script demonstrating how to use the PyJCall SDK.
This script shows how to interact with all available endpoints.

Usage:
    1. Set your JustCall API credentials in a .env file:
       JUSTCALL_API_KEY=your_api_key
       JUSTCALL_API_SECRET=your_api_secret
    
    2. Run the script:
       python example.py
"""

import asyncio
import os
import dotenv
from pyjcall import JustCallClient
from pyjcall.utils.exceptions import JustCallException

# Load environment variables from .env file
dotenv.load_dotenv()

async def test_calls(client):
    """Test Calls API endpoints (read-only)"""
    print("\n=== CALLS API ===")
    
    # List calls
    print("\nListing calls...")
    calls = await client.Calls.list(per_page=20)
    print(f"Retrieved {len(calls.get('data', []))} calls")
    
    # If we have calls, test other endpoints
    if calls.get('data'):
        call_id = calls['data'][0]['id']
        print(f"Using call ID: {call_id} for further tests")
        
        # Get call details
        print("\nGetting call details...")
        call = await client.Calls.get(call_id=call_id)
        print(f"Call direction: {call.get('direction')}")
        
        if call.get('direction') == 'Incoming':
            print("\nGetting call journey (only for incoming calls)...")
            journey = await client.Calls.get_journey(call_id=call_id)
            print(f"Journey retrieved with {len(journey)} steps")
        else:
            print("\nSkipping call journey (not an incoming call)")
        
        # Try to get voice agent data
        print("\nTrying to get voice agent data...")
        try:
            voice_data = await client.Calls.get_voice_agent_data(call_id=call_id)
            print("Voice agent data retrieved successfully")
        except JustCallException as e:
            print(f"Could not get voice agent data: {e}")
        
        # Try to download recording
        print("\nTrying to download call recording...")
        try:
            recording = await client.Calls.download_recording(call_id=call_id)
            print(f"Recording downloaded: {len(recording)} bytes")
        except Exception as e:
            print(f"Could not download recording: {e}")
    else:
        print("No calls found to test with")

async def test_messages(client):
    """Test Messages API endpoints"""
    print("\n=== MESSAGES API ===")
    
    # List messages
    print("\nListing messages...")
    messages = await client.Messages.list(per_page=20)
    print(f"Retrieved {len(messages.get('data', []))} messages")
    
    # If we have messages, test other endpoints
    if messages.get('data'):
        message_id = messages['data'][0]['id']
        print(f"Using message ID: {message_id} for further tests")
        
        # Get message details
        print("\nGetting message details...")
        message = await client.Messages.get(message_id=message_id)
        print(f"Message body: {message.get('body', 'N/A')}")
        
        # Get a phone number to use for sending tests
        numbers = await client.PhoneNumbers.list(capabilities="sms")
        if numbers.get('data'):
            print(numbers['data'][0])
            justcall_number = numbers['data'][0]['justcall_number']
            
            # Check reply
            print("\nChecking for replies...")
            if message.get('contact_number'):
                try:
                    replies = await client.Messages.check_reply(
                        contact_number=message['contact_number'],
                        justcall_number=justcall_number
                    )
                    print(f"Has replies: {replies.get('has_reply', False)}")
                except Exception as e:
                    print(f"Could not check replies: {e}")
            
            # Note: We're not actually sending messages in this example
            # to avoid sending real SMS
            print("\nSending messages example (skipped to avoid real SMS)")
            """
            # Send message example
            response = await client.Messages.send(
                to="+1234567890",  # Replace with real number
                from_number=justcall_number,
                body="Test message from PyJCall SDK"
            )
            
            # Send new message example
            response = await client.Messages.send_new(
                justcall_number=justcall_number,
                contact_number="+1234567890",  # Replace with real number
                body="Test message from PyJCall SDK"
            )
            """
        else:
            print("No SMS-capable numbers found")
    else:
        print("No messages found to test with")

async def test_phone_numbers(client):
    """Test PhoneNumbers API endpoints"""
    print("\n=== PHONE NUMBERS API ===")
    
    # List phone numbers
    print("\nListing phone numbers...")
    numbers = await client.PhoneNumbers.list(per_page=20)
    print(f"Retrieved {len(numbers.get('data', []))} phone numbers")
    
    # Show capabilities
    if numbers.get('data'):
        for i, number in enumerate(numbers['data'][:3]):  # Show first 3
            capabilities = ", ".join(number.get('capabilities', []))
            print(f"Number {i+1}: {number.get('phone_number')} - Capabilities: {capabilities}")
    else:
        print("No phone numbers found")

async def test_users(client):
    """Test Users API endpoints"""
    print("\n=== USERS API ===")
    
    # List users
    print("\nListing users...")
    users = await client.Users.list(per_page=20)
    print(f"Retrieved {len(users.get('data', []))} users")
    
    # If we have users, test other endpoints
    if users.get('data'):
        user_id = users['data'][0]['id']
        print(f"Using user ID: {user_id} for further tests")
        
        # Get user details
        print("\nGetting user details...")
        user = await client.Users.get(user_id=user_id)
        print(f"User name: {user.get('name', 'N/A')}")
        print(f"User email: {user.get('email', 'N/A')}")
    else:
        print("No users found")

async def test_contacts(client):
    """Test Contacts API endpoints"""
    print("\n=== CONTACTS API ===")
    
    # Create a new contact
    print("\nCreating new contact...")
    try:
        new_contact = await client.Contacts.create(
            firstname="John",
            phone="+15147290123",
            lastname="Doe",
            email="john.doe@example.com",
            company="Example Corp",
            notes="Created via PyJCall SDK",
            acrossteam=True
        )
        print("Contact created successfully")
        #print contact id
        print(f"Contact ID: {new_contact['id']}")
        
        # If creation successful, try to update it
        if new_contact:
            print("\nUpdating newly created contact...")
            try:
                updated = await client.Contacts.update(
                    id=new_contact['id'],  # Assuming the response includes the contact ID
                    firstname="John",
                    phone="+15147290123",
                    notes="Updated via PyJCall SDK",
                    other_phones={"Home": "+0987654321"}
                )
                print("Contact updated successfully")
            except Exception as e:
                print(f"Failed to update contact: {e}")
    except Exception as e:
        print(f"Failed to create contact: {e}")
    
    # List contacts
    print("\nListing contacts...")
    contacts = await client.Contacts.list(per_page="20")
    print(f"Retrieved {len(contacts.get('contacts', []))} contacts")
    
    # Query contacts
    print("\nQuerying contacts...")
    try:
        # Example: search by first name
        query_results = await client.Contacts.query(firstname="John")
        print(f"Found {len(query_results.get('contacts', []))} contacts matching query")
        
        # Example: iterate through all contacts matching query
        print("\nIterating through query results...")
        count = 0
        async for contact in client.Contacts.iter_query(firstname="John", max_items=50):
            count += 1
            if count % 10 == 0:
                print(f"Processed {count} matching contacts...")
        print(f"Total matching contacts processed: {count}")
        
    except ValueError as e:
        print(f"Query error: {e}")
    
    # Test bulk iteration
    print("\nTesting bulk iteration of all contacts...")
    contact_count = 0
    async for contact in client.Contacts.iter_all(max_items=100):
        contact_count += 1
        if contact_count % 20 == 0:
            print(f"Processed {contact_count} contacts...")
    
    print(f"\nTotal contacts processed: {contact_count}")

async def test_bulk_iterations(client):
    """Test bulk iteration capabilities"""
    print("\n=== BULK ITERATIONS ===")
    
    # Iterate through all calls from last month
    print("\nIterating through all calls from last month...")
    from datetime import datetime, timedelta
    
    # Calculate date range for last month
    today = datetime.now()
    last_month = today - timedelta(days=30)
    from_date = last_month.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    call_count = 0
    async for call in client.Calls.iter_all(
        from_datetime=from_date,
        to_datetime=to_date,
        max_items=1000  # Optional: limit total items
    ):
        call_count += 1
        if call_count % 100 == 0:  # Progress update every 100 calls
            print(f"Processed {call_count} calls...")
    
    print(f"\nTotal calls processed: {call_count}")
    
    # Iterate through all messages
    print("\nIterating through all messages from last week...")
    last_week = today - timedelta(days=7)
    from_date = last_week.strftime("%Y-%m-%d")
    
    message_count = 0
    async for message in client.Messages.iter_all(
        from_datetime=from_date,
        to_datetime=to_date
    ):
        message_count += 1
        if message_count % 50 == 0:  # Progress update every 50 messages
            print(f"Processed {message_count} messages...")
    
    print(f"\nTotal messages processed: {message_count}")

async def main():
    """Main function to run all examples"""
    # Get API credentials from environment
    api_key = os.getenv("JUSTCALL_API_KEY")
    api_secret = os.getenv("JUSTCALL_API_SECRET")
    
    if not api_key or not api_secret:
        print("Error: Please set JUSTCALL_API_KEY and JUSTCALL_API_SECRET environment variables")
        return
    
    print("PyJCall SDK Example Script")
    print("=========================")
    print("NOTE: This script performs READ-ONLY operations to avoid modifying production data.")
    
    # Create client
    async with JustCallClient(api_key=api_key, api_secret=api_secret) as client:
        # Test all API endpoints
        await test_calls(client)
        await test_messages(client)
        await test_phone_numbers(client)
        await test_users(client)
        await test_contacts(client)
        await test_bulk_iterations(client)
    
    print("\nExample script completed!")

if __name__ == "__main__":
    asyncio.run(main()) 