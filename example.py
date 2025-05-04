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
    """Test Contacts API endpoints (read-only)"""
    print("\n=== CONTACTS API ===")
    
    # List contacts
    print("\nListing contacts...")
    contacts = await client.Contacts.list(page="1", per_page="20")
    print(f"Retrieved {len(contacts.get('contacts', []))} contacts")
    
    # Query contacts
    print("\nQuerying contacts...")
    try:
        # Example: search by first name
        query_results = await client.Contacts.query(firstname="John")
        print(f"Found {len(query_results.get('contacts', []))} contacts matching query")
        
        # Example: iterate through query results
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
    
    from datetime import datetime, timedelta, date
    today = datetime.now()
    
    # Test Calls iteration
    print("\nIterating through all calls from last month...")
    last_month = today - timedelta(days=30)
    from_date = last_month
    to_date = today
    
    call_count = 0
    async for call in client.Calls.iter_all(
        from_datetime=from_date,
        to_datetime=to_date,
        max_items=1000
    ):
        call_count += 1
        if call_count % 100 == 0:
            print(f"Processed {call_count} calls...")
    print(f"\nTotal calls processed: {call_count}")
    
    # Test Messages iteration
    print("\nIterating through all messages from last week...")
    last_week = today - timedelta(days=7)
    # Use datetime objects directly instead of string formatting
    from_date = last_week
    
    message_count = 0
    async for message in client.Messages.iter_all(
        from_datetime=from_date,
        to_datetime=to_date
    ):
        message_count += 1
        if message_count % 50 == 0:
            print(f"Processed {message_count} messages...")
    print(f"\nTotal messages processed: {message_count}")

    # Test Users iteration
    print("\nIterating through all users...")
    user_count = 0
    async for user in client.Users.iter_all():
        user_count += 1
        if user_count % 20 == 0:
            print(f"Processed {user_count} users...")
    print(f"\nTotal users processed: {user_count}")

    # Test Phone Numbers iteration
    print("\nIterating through all phone numbers...")
    number_count = 0
    async for number in client.PhoneNumbers.iter_all():
        number_count += 1
        if number_count % 20 == 0:
            print(f"Processed {number_count} phone numbers...")
    print(f"\nTotal phone numbers processed: {number_count}")

    # Test Contacts iteration (all contacts)
    print("\nIterating through all contacts...")
    contact_count = 0
    async for contact in client.Contacts.iter_all():
        contact_count += 1
        if contact_count % 50 == 0:
            print(f"Processed {contact_count} contacts...")
    print(f"\nTotal contacts processed: {contact_count}")

    # Test Contacts query iteration
    print("\nIterating through contacts matching query...")
    query_count = 0
    async for contact in client.Contacts.iter_query(
        firstname="John",
        company="Example Corp"
    ):
        query_count += 1
        if query_count % 20 == 0:
            print(f"Processed {query_count} matching contacts...")
    print(f"\nTotal matching contacts processed: {query_count}")

    # Print summary
    print("\n=== BULK ITERATION SUMMARY ===")
    print(f"Calls processed: {call_count}")
    print(f"Messages processed: {message_count}")
    print(f"Users processed: {user_count}")
    print(f"Phone numbers processed: {number_count}")
    print(f"All contacts processed: {contact_count}")
    print(f"Matching contacts processed: {query_count}")
    
    # Test Campaigns iteration
    print("\nIterating through all campaigns...")
    campaign_count = 0
    async for campaign in client.Campaigns.iter_all():
        campaign_count += 1
        if campaign_count % 10 == 0:
            print(f"Processed {campaign_count} campaigns...")
    print(f"\nTotal campaigns processed: {campaign_count}")
    
    # Update summary to include campaigns
    print("\n=== UPDATED BULK ITERATION SUMMARY ===")
    print(f"Calls processed: {call_count}")
    print(f"Messages processed: {message_count}")
    print(f"Users processed: {user_count}")
    print(f"Phone numbers processed: {number_count}")
    print(f"All contacts processed: {contact_count}")
    print(f"Matching contacts processed: {query_count}")
    print(f"Campaigns processed: {campaign_count}")

async def test_campaigns(client):
    """Test Campaigns API endpoints (read-only)"""
    print("\n=== CAMPAIGNS API ===")
    
    # List campaigns
    print("\nListing campaigns...")
    campaigns = await client.Campaigns.list(per_page="20")
    print(f"Retrieved {len(campaigns.get('data', []))} campaigns")
    
    # If we have campaigns, show some details
    if campaigns.get('data'):
        print("\nCampaign details:")
        for i, campaign in enumerate(campaigns['data'][:3]):  # Show first 3
            print(f"Campaign {i+1}: ID={campaign.get('id')}, Name={campaign.get('name')}")
    else:
        print("No campaigns found")
    
    # Test bulk iteration
    print("\nTesting bulk iteration of all campaigns...")
    campaign_count = 0
    async for campaign in client.Campaigns.iter_all(max_items=100):
        campaign_count += 1
        if campaign_count % 10 == 0:
            print(f"Processed {campaign_count} campaigns...")
    
    print(f"\nTotal campaigns processed: {campaign_count}")

async def test_campaign_contacts(client):
    """Test Campaign Contacts API endpoints (read-only)"""
    print("\n=== CAMPAIGN CONTACTS API ===")
    
    # Get custom fields
    print("\nGetting custom fields for campaign contacts...")
    try:
        custom_fields = await client.CampaignContacts.get_custom_fields()
        print(f"Retrieved {len(custom_fields.get('data', []))} custom fields")
        
        # Show custom fields details if available
        if custom_fields.get('data'):
            print("\nCustom fields details:")
            for i, field in enumerate(custom_fields['data'][:3]):  # Show first 3
                print(f"Field {i+1}: Label={field.get('label')}, Key={field.get('key')}, Type={field.get('type')}")
        else:
            print("No custom fields found")
    except Exception as e:
        print(f"Error getting custom fields: {e}")
    
    # List campaign contacts (if we have campaigns)
    print("\nListing campaigns to find one with contacts...")
    campaigns = await client.Campaigns.list()
    
    if campaigns.get('data'):
        campaign_id = campaigns['data'][0]['id']
        print(f"\nListing contacts for campaign ID: {campaign_id}")
        
        try:
            contacts = await client.CampaignContacts.list(campaign_id=str(campaign_id))
            print(f"Retrieved {len(contacts.get('data', []))} contacts")
            
            # Show contact details if available
            if contacts.get('data'):
                print("\nContact details:")
                for i, contact in enumerate(contacts['data'][:3]):  # Show first 3
                    print(f"Contact {i+1}: ID={contact.get('id')}, Name={contact.get('name')}, Phone={contact.get('phone')}")
                
                # Test bulk iteration
                print("\nTesting bulk iteration of campaign contacts...")
                contact_count = 0
                async for contact in client.CampaignContacts.iter_all(
                    campaign_id=str(campaign_id),
                    max_items=100
                ):
                    contact_count += 1
                    if contact_count % 10 == 0:
                        print(f"Processed {contact_count} contacts...")
                
                print(f"\nTotal campaign contacts processed: {contact_count}")
            else:
                print("No contacts found in this campaign")
        except Exception as e:
            print(f"Error listing campaign contacts: {e}")
    else:
        print("No campaigns found to list contacts")

async def test_campaign_calls(client):
    """Test Campaign Calls API endpoints (read-only)"""
    print("\n=== CAMPAIGN CALLS API ===")
    
    # List campaign calls
    print("\nListing campaigns to find one for calls...")
    campaigns = await client.Campaigns.list()
    
    if campaigns.get('data'):
        campaign_id = campaigns['data'][0]['id']
        print(f"\nListing calls for campaign ID: {campaign_id}")
        
        try:
            # Get calls for a specific campaign
            from datetime import datetime, timedelta, date
            today = datetime.now()
            one_month_ago = today - timedelta(days=30)
            # Use date objects directly instead of string formatting
            start_date = one_month_ago.date()
            end_date = today.date()
            
            calls = await client.CampaignCalls.list(
                campaign_id=str(campaign_id),
                start_date=start_date,
                end_date=end_date
            )
            print(f"Retrieved {len(calls.get('data', []))} calls out of {calls.get('total', 0)} total")
            
            # Show call details if available
            if calls.get('data'):
                print("\nCall details:")
                for i, call in enumerate(calls['data'][:3]):  # Show first 3
                    print(f"Call {i+1}: ID={call.get('call_id')}, From={call.get('from')}, To={call.get('to')}, Duration={call.get('duration')}")
                
                # Test bulk iteration
                print("\nTesting bulk iteration of campaign calls...")
                call_count = 0
                async for call in client.CampaignCalls.iter_all(
                    campaign_id=str(campaign_id),
                    start_date=start_date,
                    end_date=end_date,
                    max_items=100
                ):
                    call_count += 1
                    if call_count % 10 == 0:
                        print(f"Processed {call_count} calls...")
                
                print(f"\nTotal campaign calls processed: {call_count}")
            else:
                print("No calls found for this campaign in the last 30 days")
        except Exception as e:
            print(f"Error listing campaign calls: {e}")
    else:
        print("No campaigns found to list calls")
    
    # List calls from all campaigns
    print("\nListing calls from all campaigns in the last 7 days...")
    try:
        from datetime import datetime, timedelta, date
        today = datetime.now()
        one_week_ago = today - timedelta(days=7)
        # Use date objects directly instead of string formatting
        start_date = one_week_ago.date()
        end_date = today.date()
        
        all_calls = await client.CampaignCalls.list(
            start_date=start_date,
            end_date=end_date
        )
        print(f"Retrieved {len(all_calls.get('data', []))} calls from all campaigns")
    except Exception as e:
        print(f"Error listing all campaign calls: {e}")

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
        await test_campaigns(client)
        await test_campaign_contacts(client)
        await test_campaign_calls(client)
        await test_bulk_iterations(client)
    
    print("\nExample script completed!")

if __name__ == "__main__":
    asyncio.run(main()) 