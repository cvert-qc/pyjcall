# PyJCall API Documentation

This document provides a condensed overview of all methods available in the PyJCall library, organized by module.

## Table of Contents

- [Campaigns](#campaigns)
- [Campaign Calls](#campaign-calls)
- [Campaign Contacts](#campaign-contacts)
- [Calls](#calls)
- [Contacts](#contacts)

## Campaigns

### `list(page=None, per_page=None)`

List all Sales Dialer campaigns.

**Input:**
- `page` (optional): The page number to read
- `per_page` (optional): The number of results per page (default: 50, max: 100)

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `data`: List of campaign objects with details like id, name, type, etc.
  - `count`: Total number of campaigns

**Example:**
```python
campaigns = await client.campaigns.list(page="1", per_page="50")
```

### `create(name, type, default_number=None, country_code=None)`

Create a campaign in Sales Dialer.

**Input:**
- `name`: The name of the campaign to create
- `type`: The type of campaign (autodial, predictive, or dynamic)
- `default_number` (optional): Default number to dial from for the campaign
- `country_code` (optional): Country code in ISO-2 format (ISO 3166-1 alpha-2)

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `campaign_id`: ID of the created campaign
  - `message`: Success or error message

**Example:**
```python
result = await client.campaigns.create(
    name="My Campaign", 
    type="autodial", 
    default_number="+15551234567"
)
```

### `iter_all(max_items=None)`

Iterate through all campaigns. Automatically handles pagination.

**Input:**
- `max_items` (optional): Maximum number of items to return (None for all)

**Output:**
- Async iterator yielding individual campaign records

**Example:**
```python
async for campaign in client.campaigns.iter_all(max_items=100):
    print(campaign["id"], campaign["name"])
```

## Campaign Calls

### `list(campaign_id=None, start_date=None, end_date=None, order=None, page=None, per_page=None)`

List all calls made from JustCall Sales Dialer.

**Input:**
- `campaign_id` (optional): Campaign ID from which to fetch calls
- `start_date` (optional): Start date from which to fetch calls (Python date object)
- `end_date` (optional): End date from which to fetch calls (Python date object)
- `order` (optional): Order of calls: "0" for ascending, "1" for descending
- `page` (optional): Page number to retrieve
- `per_page` (optional): Number of results per page (default: 100, max: 100)

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `data`: List of call objects with details like id, campaign_id, agent_id, etc.
  - `count`: Number of calls on current page
  - `total`: Total number of calls matching the criteria

**Note:**
- If campaign_id is not provided, all calls from all campaigns will be fetched

**Example:**
```python
from datetime import date

calls = await client.campaign_calls.list(
    campaign_id="12345",
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 31),
    order="0"
)
```

### `iter_all(campaign_id=None, start_date=None, end_date=None, order=None, max_items=None)`

Iterate through all calls made from JustCall Sales Dialer. Automatically handles pagination.

**Input:**
- `campaign_id` (optional): Campaign ID from which to fetch calls
- `start_date` (optional): Start date from which to fetch calls (Python date object)
- `end_date` (optional): End date from which to fetch calls (Python date object)
- `order` (optional): Order of calls: "0" for ascending, "1" for descending
- `max_items` (optional): Maximum number of items to return (None for all)

**Output:**
- Async iterator yielding individual call records

**Note:**
- If campaign_id is not provided, all calls from all campaigns will be fetched

**Example:**
```python
from datetime import date

async for call in client.campaign_calls.iter_all(
    campaign_id="12345",
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 31)
):
    print(call["id"], call["phone"], call["duration"])
```

## Campaign Contacts

### `get_custom_fields()`

Get custom fields for campaign contacts.

**Input:**
- No parameters needed

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `data`: List of custom field objects with details like id, label, key, type, etc.

**Example:**
```python
custom_fields = await client.campaign_contacts.get_custom_fields()
```

### `list(campaign_id)`

List all contacts in a campaign.

**Input:**
- `campaign_id`: Campaign ID for which to list contacts

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `data`: List of contact objects with details like id, first_name, last_name, phone, etc.

**Example:**
```python
contacts = await client.campaign_contacts.list(campaign_id="12345")
```

### `add(campaign_id, phone, first_name=None, last_name=None, custom_props=None)`

Add a contact to a campaign.

**Input:**
- `campaign_id`: Campaign ID to which the contact will be added
- `phone`: Formatted phone number of the contact with country code
- `first_name` (optional): Contact's first name
- `last_name` (optional): Contact's last name
- `custom_props` (optional): Custom properties for the contact as a dictionary

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `data`: Added contact details
  - `message`: Success or error message

**Example:**
```python
result = await client.campaign_contacts.add(
    campaign_id="12345",
    phone="+15551234567",
    first_name="John",
    last_name="Doe",
    custom_props={"custom_field_1": "value1", "custom_field_2": "value2"}
)
```

### `remove(campaign_id=None, phone=None, all=None)`

Remove a contact from a campaign.

**Input:**
- `campaign_id` (optional): Campaign ID from which to remove the contact
- `phone` (optional): Phone number of the contact to remove
- `all` (optional): If true, removes all contacts from the campaign

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `message`: Success or error message

**Note:**
- If only phone is provided, the contact will be removed from all campaigns
- If all=True, all contacts will be removed from the specified campaign

**Example:**
```python
# Remove a specific contact from a campaign
result = await client.campaign_contacts.remove(
    campaign_id="12345",
    phone="+15551234567"
)

# Remove all contacts from a campaign
result = await client.campaign_contacts.remove(
    campaign_id="12345",
    all=True
)
```

### `iter_all(campaign_id, max_items=None)`

Iterate through all contacts in a campaign.

**Input:**
- `campaign_id`: Campaign ID for which to list contacts
- `max_items` (optional): Maximum number of items to return (None for all)

**Output:**
- Async iterator yielding individual contact records

**Example:**
```python
async for contact in client.campaign_contacts.iter_all(campaign_id="12345"):
    print(contact["first_name"], contact["last_name"], contact["phone"])
```

## Calls

### `list(fetch_queue_data=False, fetch_ai_data=False, from_datetime=None, to_datetime=None, contact_number=None, justcall_number=None, agent_id=None, ivr_digit=None, call_direction=None, call_type=None, call_traits=None, page=None, per_page=20, sort="id", order="desc", last_call_id_fetched=None)`

List all calls with optional filtering parameters.

**Input:**
- `fetch_queue_data` (optional): Fetch queue data like callback time, status, wait duration
- `fetch_ai_data` (optional): Fetch coaching data by Justcall AI
- `from_datetime` (optional): Start datetime (Python datetime object)
- `to_datetime` (optional): End datetime (Python datetime object)
- `contact_number` (optional): Contact number with country code
- `justcall_number` (optional): JustCall number
- `agent_id` (optional): ID of the agent
- `ivr_digit` (optional): IVR digit for call routing filter
- `call_direction` (optional): Call direction ("Incoming"/"Outgoing" - case sensitive)
- `call_type` (optional): Call type (answered/unanswered/missed/voicemail/abandoned)
- `call_traits` (optional): List of traits associated with calls
- `page` (optional): Page number
- `per_page` (optional): Calls per page (min: 20, max: 100)
- `sort` (optional): Parameter to sort calls by (default: "id")
- `order` (optional): Sort order ("asc"/"desc", default: "desc")
- `last_call_id_fetched` (optional): ID of last fetched call

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `data`: List of call objects with details
  - `count`: Number of calls on current page
  - `total`: Total number of calls matching the criteria

**Example:**
```python
from datetime import datetime

calls = await client.calls.list(
    from_datetime=datetime(2025, 1, 1),
    to_datetime=datetime(2025, 1, 31),
    call_direction="Outgoing",
    per_page=50
)
```

### `get(call_id, fetch_queue_data=False, fetch_ai_data=False)`

Get details of a specific call by ID.

**Input:**
- `call_id`: Unique ID of the call generated by JustCall
- `fetch_queue_data` (optional): Set to true to fetch queue data like callback time, status, etc.
- `fetch_ai_data` (optional): Set to true to fetch coaching data by JustCall AI

**Output:**
- Dictionary containing call details

**Example:**
```python
call = await client.calls.get(call_id=12345, fetch_queue_data=True)
```

### `update(call_id, notes=None, disposition_code=None, rating=None)`

Update a call's details.

**Input:**
- `call_id`: Unique ID of the call
- `notes` (optional): New notes for the call (replaces existing)
- `disposition_code` (optional): New disposition code
- `rating` (optional): New rating (0-5, allows .5 increments)

**Output:**
- Dictionary containing updated call details

**Example:**
```python
result = await client.calls.update(
    call_id=12345,
    notes="Customer requested follow-up next week",
    rating=4.5
)
```

### `get_journey(call_id)`

Get the journey/timeline of a specific call.

**Input:**
- `call_id`: Unique ID of the call generated by JustCall

**Output:**
- Dictionary containing call journey details

**Example:**
```python
journey = await client.calls.get_journey(call_id=12345)
```

### `get_voice_agent_data(call_id)`

Get voice agent data for a specific call.

**Input:**
- `call_id`: Unique ID of the call generated by JustCall

**Output:**
- Dictionary containing voice agent data for the call

**Example:**
```python
voice_data = await client.calls.get_voice_agent_data(call_id=12345)
```

### `download_recording(call_id)`

Download the recording for a specific call.

**Input:**
- `call_id`: Unique ID of the call generated by JustCall

**Output:**
- Bytes object containing the recording file data

**Example:**
```python
recording_data = await client.calls.download_recording(call_id=12345)

# Save to file
with open("recording.mp3", "wb") as f:
    f.write(recording_data)
```

### `iter_all(fetch_queue_data=False, fetch_ai_data=False, from_datetime=None, to_datetime=None, contact_number=None, justcall_number=None, agent_id=None, ivr_digit=None, call_direction=None, call_type=None, call_traits=None, sort="id", order="desc", max_items=None)`

Iterate through all calls matching the filter criteria. Automatically handles pagination.

**Input:**
- Same as list() method, except page and per_page are handled internally
- `max_items` (optional): Maximum number of items to return (None for all)

**Output:**
- Async iterator yielding individual call records

**Example:**
```python
from datetime import datetime

async for call in client.calls.iter_all(
    from_datetime=datetime(2025, 1, 1),
    to_datetime=datetime(2025, 1, 31),
    call_direction="Outgoing"
):
    print(call["id"], call["phone"], call["duration"])
```

## Contacts

### `list(page="1", per_page="50")`

List contacts with optional filtering parameters.

**Input:**
- `page` (optional): Page number (v1 API uses string)
- `per_page` (optional): Results per page (max: 100)

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `data`: List of contact objects with details
  - `count`: Number of contacts on current page

**Example:**
```python
contacts = await client.contacts.list(page="1", per_page="50")
```

### `iter_all(max_items=None)`

Iterate through all contacts. Automatically handles pagination.

**Input:**
- `max_items` (optional): Maximum number of items to return (None for all)

**Output:**
- Async iterator yielding individual contact records

**Example:**
```python
async for contact in client.contacts.iter_all(max_items=100):
    print(contact["id"], contact["firstname"], contact["phone"])
```

### `query(id=None, firstname=None, lastname=None, phone=None, email=None, company=None, notes=None, page="1", per_page="100")`

Query contacts based on search parameters. At least one search parameter is required.

**Input:**
- `id` (optional): Unique id of the contact
- `firstname` (optional): First name of the contact
- `lastname` (optional): Last name of the contact
- `phone` (optional): Phone number of the contact
- `email` (optional): Email address associated with the contact
- `company` (optional): Company associated with the contact
- `notes` (optional): Custom information associated with the contact
- `page` (optional): The page number to read
- `per_page` (optional): Number of results per page (max: 100)

**Output:**
- Dictionary containing:
  - `status`: Status of the request ("success" or "error")
  - `data`: List of matching contact objects
  - `count`: Number of contacts on current page

**Example:**
```python
results = await client.contacts.query(
    firstname="John",
    lastname="Doe",
    per_page="50"
)
```

### `iter_query(id=None, firstname=None, lastname=None, phone=None, email=None, company=None, notes=None, max_items=None)`

Iterate through all contacts matching the query parameters. Automatically handles pagination. At least one search parameter is required.

**Input:**
- Same as query() method, except page and per_page are handled internally
- `max_items` (optional): Maximum number of items to return (None for all)

**Output:**
- Async iterator yielding individual contact records

**Example:**
```python
async for contact in client.contacts.iter_query(firstname="John"):
    print(contact["id"], contact["firstname"], contact["phone"])
```

### `update(id, firstname, phone, lastname=None, email=None, company=None, notes=None, other_phones=None)`

Update a contact's information.

**Input:**
- `id`: Unique id of the contact
- `firstname`: First name of the contact
- `phone`: Phone number of the contact
- `lastname` (optional): Last name of the contact
- `email` (optional): Email address associated with the contact
- `company` (optional): Company associated with the contact
- `notes` (optional): Custom information to associate with the contact
- `other_phones` (optional): Additional phone numbers as {label: number}

**Output:**
- Dictionary containing updated contact information

**Example:**
```python
result = await client.contacts.update(
    id=12345,
    firstname="John",
    lastname="Doe",
    phone="+15551234567",
    email="john.doe@example.com",
    other_phones={"Work": "+15559876543"}
)
```

### `create(firstname, phone, lastname=None, email=None, company=None, notes=None, acrossteam=None, agentid=None)`

Create a new contact.

**Input:**
- `firstname`: First name of the contact
- `phone`: Phone number of the contact
- `lastname` (optional): Last name of the contact
- `email` (optional): Email address associated with the contact
- `company` (optional): Company associated with the contact
- `notes` (optional): Custom information to associate with the contact
- `acrossteam` (optional): 1 to create contact for all team members, 0 or None for account owner only
- `agentid` (optional): Create contact only for specific agent ID

**Output:**
- Dictionary containing created contact information

**Example:**
```python
result = await client.contacts.create(
    firstname="Jane",
    lastname="Smith",
    phone="+15551234567",
    email="jane.smith@example.com",
    company="Acme Inc",
    acrossteam=1
)
```

### `delete(id)`

Delete a contact.

**Input:**
- `id`: Unique id of the contact to delete

**Output:**
- Dictionary containing response indicating success/failure

**Example:**
```python
result = await client.contacts.delete(id=12345)
```

### `action(number, type, action, acrossteam="1")`

Perform actions on a contact number (add/remove to/from DND, blacklist, etc).

**Input:**
- `number`: Phone number to act on
- `type`: Type of action:
  - "0" - Blacklist number
  - "1" - Add to DND list
  - "2" - Add to DNM list
- `action`: Action to perform:
  - "0" - Remove from list
  - "1" - Add to list
- `acrossteam` (optional): Apply across team ("1") or individual ("0"), defaults to "1"

**Output:**
- Dictionary containing response indicating success/failure

**Example:**
```python
# Add a number to the blacklist
result = await client.contacts.action(
    number="+15551234567",
    type="0",  # Blacklist
    action="1"  # Add
)

# Remove a number from the DND list
result = await client.contacts.action(
    number="+15551234567",
    type="1",  # DND
    action="0",  # Remove
    acrossteam="0"  # Only for current user
)
```
