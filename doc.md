# PyJCall API Documentation

This document provides a condensed overview of all methods available in the PyJCall library, organized by module.

## Table of Contents

- [Models](#models)
  - [Campaigns](#campaigns-models)
  - [Campaign Calls](#campaign-calls-models)
  - [Campaign Contacts](#campaign-contacts-models)
  - [Calls](#calls-models)
  - [Contacts](#contacts-models)
- [Resources](#resources)
  - [Campaigns](#campaigns-resources)
  - [Campaign Calls](#campaign-calls-resources)
  - [Campaign Contacts](#campaign-contacts-resources)
  - [Calls](#calls-resources)
  - [Contacts](#contacts-resources)

## Models

### Campaigns Models

#### `ListCampaignsParams`

Parameters for listing campaigns.

**Fields:**
- `page` (Optional[str]): The page number to read
- `per_page` (Optional[str]): The number of results per page (default: 50, max: 100)

#### `CreateCampaignParams`

Parameters for creating a campaign.

**Fields:**
- `name` (str): The name of the campaign to create
- `type` (str): The type of campaign (autodial, predictive, or dynamic)
- `default_number` (Optional[str]): Default number to dial from for the campaign
- `country_code` (Optional[str]): Country code in ISO-2 format (ISO 3166-1 alpha-2)

### Campaign Calls Models

#### `ListCampaignCallsParams`

Parameters for listing calls from JustCall Sales Dialer.

**Fields:**
- `campaign_id` (Optional[str]): Campaign ID from which to fetch calls (optional, if not provided all campaign calls will be fetched)
- `start_date` (Optional[date]): Start date from which to fetch calls
- `end_date` (Optional[date]): End date from which to fetch calls
- `order` (Optional[str]): Order of calls: 0 for ascending, 1 for descending. Default is ascending
- `page` (Optional[str]): Page number to retrieve
- `per_page` (Optional[str]): Number of results per page (default: 100, max: 100)

### Campaign Contacts Models

#### `GetCustomFieldsParams`

Parameters for getting custom fields for campaign contacts.

**Fields:**
- No parameters needed for this endpoint

#### `ListCampaignContactsParams`

Parameters for listing contacts in a campaign.

**Fields:**
- `campaign_id` (str): Campaign ID for which to list contacts

#### `AddCampaignContactParams`

Parameters for adding a contact to a campaign.

**Fields:**
- `campaign_id` (str): Campaign ID to which the contact will be added
- `first_name` (Optional[str]): Contact's first name
- `last_name` (Optional[str]): Contact's last name
- `phone` (str): Formatted phone number of the contact with country code
- `custom_props` (Optional[Dict[str, Any]]): Custom properties for the contact (key is the ID of the custom field)

#### `RemoveCampaignContactParams`

Parameters for removing a contact from a campaign.

**Fields:**
- `campaign_id` (Optional[str]): Campaign ID from which to remove the contact
- `phone` (Optional[str]): Phone number of the contact to remove
- `all` (Optional[bool]): If true, removes all contacts from the campaign

### Calls Models

#### `CallDirection`

Enum for call direction to enforce correct casing.

**Values:**
- `INCOMING`: "Incoming"
- `OUTGOING`: "Outgoing"

#### `ListCallsParams`

Parameters for listing calls.

**Fields:**
- `fetch_queue_data` (bool): Fetch queue data like callback time, status, wait duration
- `fetch_ai_data` (bool): Fetch coaching data by Justcall AI
- `from_datetime` (Optional[datetime]): Start datetime
- `to_datetime` (Optional[datetime]): End datetime
- `contact_number` (Optional[str]): Contact number with country code
- `justcall_number` (Optional[str]): JustCall number
- `agent_id` (Optional[int]): ID of the agent
- `ivr_digit` (Optional[int]): IVR digit for call routing filter
- `call_direction` (Optional[str]): Call direction (Incoming/Outgoing - case sensitive)
- `call_type` (Optional[str]): Call type (answered/unanswered/missed/voicemail/abandoned)
- `call_traits` (Optional[List[str]]): Traits associated with calls
- `page` (Optional[int]): Page number
- `per_page` (Optional[int]): Calls per page (min: 20, max: 100)
- `sort` (str): Parameter to sort calls by (default: "id")
- `order` (str): Sort order (asc/desc) (default: "desc")
- `last_call_id_fetched` (Optional[int]): ID of last fetched call

#### `GetCallParams`

Parameters for getting a single call.

**Fields:**
- `fetch_queue_data` (bool): Fetch queue data like callback time, status, wait duration
- `fetch_ai_data` (bool): Fetch coaching data by Justcall AI

#### `UpdateCallParams`

Parameters for updating a call.

**Fields:**
- `notes` (Optional[str]): Updated notes for the call (replaces existing notes)
- `disposition_code` (Optional[str]): New/updated disposition code (must be from admin-created options)
- `rating` (Optional[float]): Rating from 0 to 5 (allows .5 decimals)

### Contacts Models

#### `ListContactsParams`

Parameters for listing contacts.

**Fields:**
- `page` (str): Page number (v1 API uses string) (default: "1")
- `per_page` (str): Results per page (max: 100) (default: "50")

#### `QueryContactsParams`

Parameters for querying contacts.

**Fields:**
- `id` (Optional[int]): Unique id of the contact
- `firstname` (Optional[str]): First name of the contact
- `lastname` (Optional[str]): Last name of the contact
- `phone` (Optional[str]): Phone number of the contact
- `email` (Optional[str]): Email address associated with the contact
- `company` (Optional[str]): Company associated with the contact
- `notes` (Optional[str]): Custom information associated with the contact
- `page` (Optional[str]): The page number to read (default: "1")
- `per_page` (Optional[str]): Number of results per page (default: "100")

#### `OtherPhone`

Model for additional phone numbers.

**Fields:**
- `label` (str): Label for the phone number
- `number` (str): The phone number

#### `UpdateContactParams`

Parameters for updating a contact.

**Fields:**
- `id` (int): Unique id of the contact
- `firstname` (str): First name of the contact
- `phone` (str): Phone number of the contact
- `lastname` (Optional[str]): Last name of the contact
- `email` (Optional[str]): Email address associated with the contact
- `company` (Optional[str]): Company associated with the contact
- `notes` (Optional[str]): Custom information associated with the contact
- `other_phones` (Optional[OtherPhone]): Additional phone numbers

#### `CreateContactParams`

Parameters for creating a new contact.

**Fields:**
- `firstname` (str): First name of the contact
- `phone` (str): Phone number of the contact
- `lastname` (Optional[str]): Last name of the contact
- `email` (Optional[str]): Email address of the contact
- `company` (Optional[str]): Company name
- `notes` (Optional[str]): Additional notes
- `acrossteam` (Optional[int]): Create for all team members (1) or owner only (0)
- `agentid` (Optional[int]): Specific agent ID to create contact for

#### `DeleteContactParams`

Parameters for deleting a contact.

**Fields:**
- `id` (int): Unique id of the contact

#### `ContactActionType`

Type of contact action.

**Values:**
- `BLACKLIST`: "0"
- `DND`: "1"
- `DNM`: "2"

#### `ContactActionOperation`

Operation to perform.

**Values:**
- `REMOVE`: "0"
- `ADD`: "1"

#### `ContactActionParams`

Parameters for contact actions (DND, blacklist, etc).

**Fields:**
- `number` (str): Phone number to act on
- `type` (ContactActionType): Type of action (blacklist, DND, DNM)
- `action` (ContactActionOperation): Action to perform (add/remove)
- `acrossteam` (Optional[str]): Apply across team (1) or individual (0) (default: "1")

## Resources

### Campaigns Resources

#### `list(page: Optional[str] = None, per_page: Optional[str] = None) -> Dict[str, Any]`

List all Sales Dialer campaigns.

**Parameters:**
- `page` (Optional[str]): The page number to read
- `per_page` (Optional[str]): The number of results per page (default: 50, max: 100)

**Returns:**
- `Dict[str, Any]`: List of campaigns with status and count

#### `create(name: str, type: str, default_number: Optional[str] = None, country_code: Optional[str] = None) -> Dict[str, Any]`

Create a campaign in Sales Dialer.

**Parameters:**
- `name` (str): The name of the campaign to create
- `type` (str): The type of campaign (autodial, predictive, or dynamic)
- `default_number` (Optional[str]): Default number to dial from for the campaign
- `country_code` (Optional[str]): Country code in ISO-2 format (ISO 3166-1 alpha-2)

**Returns:**
- `Dict[str, Any]`: Response containing campaign_id and status

#### `iter_all(max_items: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]`

Iterate through all campaigns. Automatically handles pagination.

**Parameters:**
- `max_items` (Optional[int]): Maximum number of items to return (None for all)

**Yields:**
- `Dict[str, Any]`: Individual campaign records

### Campaign Calls Resources

#### `list(campaign_id: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, order: Optional[str] = None, page: Optional[str] = None, per_page: Optional[str] = None) -> Dict[str, Any]`

List all calls made from JustCall Sales Dialer.

**Parameters:**
- `campaign_id` (Optional[str]): Campaign ID from which to fetch calls
- `start_date` (Optional[date]): Start date from which to fetch calls
- `end_date` (Optional[date]): End date from which to fetch calls
- `order` (Optional[str]): Order of calls: 0 for ascending, 1 for descending
- `page` (Optional[str]): Page number to retrieve
- `per_page` (Optional[str]): Number of results per page (default: 100, max: 100)

**Returns:**
- `Dict[str, Any]`: List of campaign calls with status, count, and total

**Note:**
- If campaign_id is not provided, all calls from all campaigns will be fetched

#### `iter_all(campaign_id: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, order: Optional[str] = None, max_items: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]`

Iterate through all calls made from JustCall Sales Dialer. Automatically handles pagination.

**Parameters:**
- `campaign_id` (Optional[str]): Campaign ID from which to fetch calls
- `start_date` (Optional[date]): Start date from which to fetch calls
- `end_date` (Optional[date]): End date from which to fetch calls
- `order` (Optional[str]): Order of calls: 0 for ascending, 1 for descending
- `max_items` (Optional[int]): Maximum number of items to return (None for all)

**Yields:**
- `Dict[str, Any]`: Individual call records

**Note:**
- If campaign_id is not provided, all calls from all campaigns will be fetched

### Campaign Contacts Resources

#### `get_custom_fields() -> Dict[str, Any]`

Get custom fields for campaign contacts.

**Returns:**
- `Dict[str, Any]`: List of custom fields with their labels, keys, and types

#### `list(campaign_id: str) -> Dict[str, Any]`

List all contacts in a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID for which to list contacts

**Returns:**
- `Dict[str, Any]`: List of contacts in the campaign

#### `add(campaign_id: str, phone: str, first_name: Optional[str] = None, last_name: Optional[str] = None, custom_props: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

Add a contact to a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID to which the contact will be added
- `phone` (str): Formatted phone number of the contact with country code
- `first_name` (Optional[str]): Contact's first name
- `last_name` (Optional[str]): Contact's last name
- `custom_props` (Optional[Dict[str, Any]]): Custom properties for the contact

**Returns:**
- `Dict[str, Any]`: Added contact details

#### `remove(campaign_id: Optional[str] = None, phone: Optional[str] = None, all: Optional[bool] = None) -> Dict[str, Any]`

Remove a contact from a campaign.

**Parameters:**
- `campaign_id` (Optional[str]): Campaign ID from which to remove the contact
- `phone` (Optional[str]): Phone number of the contact to remove
- `all` (Optional[bool]): If true, removes all contacts from the campaign

**Returns:**
- `Dict[str, Any]`: Response with status and message

**Note:**
- If only phone is provided, the contact will be removed from all campaigns
- If all=True, all contacts will be removed from the specified campaign

#### `iter_all(campaign_id: str, max_items: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]`

Iterate through all contacts in a campaign.

**Parameters:**
- `campaign_id` (str): Campaign ID for which to list contacts
- `max_items` (Optional[int]): Maximum number of items to return (None for all)

**Yields:**
- `Dict[str, Any]`: Individual contact records

### Calls Resources

#### `list(fetch_queue_data: bool = False, fetch_ai_data: bool = False, from_datetime: Optional[datetime] = None, to_datetime: Optional[datetime] = None, contact_number: Optional[str] = None, justcall_number: Optional[str] = None, agent_id: Optional[int] = None, ivr_digit: Optional[int] = None, call_direction: Optional[str] = None, call_type: Optional[str] = None, call_traits: Optional[List[str]] = None, page: Optional[int] = None, per_page: Optional[int] = 20, sort: str = "id", order: str = "desc", last_call_id_fetched: Optional[int] = None) -> Dict[str, Any]`

List all calls with optional filtering parameters. Returns a paginated list of calls based on the provided filters.

**Parameters:**
- `fetch_queue_data` (bool): Fetch queue data like callback time, status, wait duration
- `fetch_ai_data` (bool): Fetch coaching data by Justcall AI
- `from_datetime` (Optional[datetime]): Start datetime
- `to_datetime` (Optional[datetime]): End datetime
- `contact_number` (Optional[str]): Contact number with country code
- `justcall_number` (Optional[str]): JustCall number
- `agent_id` (Optional[int]): ID of the agent
- `ivr_digit` (Optional[int]): IVR digit for call routing filter
- `call_direction` (Optional[str]): Call direction (Incoming/Outgoing - case sensitive)
- `call_type` (Optional[str]): Call type (answered/unanswered/missed/voicemail/abandoned)
- `call_traits` (Optional[List[str]]): Traits associated with calls
- `page` (Optional[int]): Page number
- `per_page` (Optional[int]): Calls per page (min: 20, max: 100)
- `sort` (str): Parameter to sort calls by
- `order` (str): Sort order (asc/desc)
- `last_call_id_fetched` (Optional[int]): ID of last fetched call

**Returns:**
- `Dict[str, Any]`: List of calls with pagination information

#### `get(call_id: int, fetch_queue_data: bool = False, fetch_ai_data: bool = False) -> Dict[str, Any]`

Get details of a specific call by ID.

**Parameters:**
- `call_id` (int): Unique ID of the call generated by JustCall
- `fetch_queue_data` (bool): Set to true to fetch queue data like callback time, status, etc.
- `fetch_ai_data` (bool): Set to true to fetch coaching data by JustCall AI

**Returns:**
- `Dict[str, Any]`: Call details

#### `update(call_id: int, notes: Optional[str] = None, disposition_code: Optional[str] = None, rating: Optional[float] = None) -> Dict[str, Any]`

Update a call's details.

**Parameters:**
- `call_id` (int): Unique ID of the call
- `notes` (Optional[str]): New notes for the call (replaces existing)
- `disposition_code` (Optional[str]): New disposition code
- `rating` (Optional[float]): New rating (0-5, allows .5 increments)

**Returns:**
- `Dict[str, Any]`: Updated call details

#### `get_journey(call_id: int) -> Dict[str, Any]`

Get the journey/timeline of a specific call.

**Parameters:**
- `call_id` (int): Unique ID of the call generated by JustCall

**Returns:**
- `Dict[str, Any]`: Call journey details

#### `get_voice_agent_data(call_id: int) -> Dict[str, Any]`

Get voice agent data for a specific call.

**Parameters:**
- `call_id` (int): Unique ID of the call generated by JustCall

**Returns:**
- `Dict[str, Any]`: Voice agent data for the call

#### `download_recording(call_id: int) -> bytes`

Download the recording for a specific call.

**Parameters:**
- `call_id` (int): Unique ID of the call generated by JustCall

**Returns:**
- `bytes`: The recording file data

**Raises:**
- `JustCallException`: If the recording doesn't exist or other API errors

#### `iter_all(fetch_queue_data: bool = False, fetch_ai_data: bool = False, from_datetime: Optional[datetime] = None, to_datetime: Optional[datetime] = None, contact_number: Optional[str] = None, justcall_number: Optional[str] = None, agent_id: Optional[int] = None, ivr_digit: Optional[int] = None, call_direction: Optional[str] = None, call_type: Optional[str] = None, call_traits: Optional[List[str]] = None, sort: str = "id", order: str = "desc", max_items: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]`

Iterate through all calls matching the filter criteria. Automatically handles pagination.

**Parameters:**
- Same as list() method, except page and per_page are handled internally
- `max_items` (Optional[int]): Maximum number of items to return (None for all)

**Yields:**
- `Dict[str, Any]`: Individual call records

### Contacts Resources

#### `list(page: Optional[str] = "1", per_page: Optional[str] = "50") -> Dict[str, Any]`

List contacts with optional filtering parameters.

**Parameters:**
- `page` (Optional[str]): Page number (v1 API uses string)
- `per_page` (Optional[str]): Results per page (max: 100)

**Returns:**
- `Dict[str, Any]`: List of contacts with pagination information

#### `iter_all(max_items: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]`

Iterate through all contacts. Automatically handles pagination.

**Parameters:**
- `max_items` (Optional[int]): Maximum number of items to return (None for all)

**Yields:**
- `Dict[str, Any]`: Individual contact records

#### `query(id: Optional[int] = None, firstname: Optional[str] = None, lastname: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None, company: Optional[str] = None, notes: Optional[str] = None, page: Optional[str] = "1", per_page: Optional[str] = "100") -> Dict[str, Any]`

Query contacts based on search parameters. At least one search parameter is required.

**Parameters:**
- `id` (Optional[int]): Unique id of the contact
- `firstname` (Optional[str]): First name of the contact
- `lastname` (Optional[str]): Last name of the contact
- `phone` (Optional[str]): Phone number of the contact
- `email` (Optional[str]): Email address associated with the contact
- `company` (Optional[str]): Company associated with the contact
- `notes` (Optional[str]): Custom information associated with the contact
- `page` (Optional[str]): The page number to read
- `per_page` (Optional[str]): Number of results per page (max: 100)

**Returns:**
- `Dict[str, Any]`: Matching contacts

**Raises:**
- `ValueError`: If no search parameters are provided

#### `iter_query(id: Optional[int] = None, firstname: Optional[str] = None, lastname: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None, company: Optional[str] = None, notes: Optional[str] = None, max_items: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]`

Iterate through all contacts matching the query parameters. Automatically handles pagination. At least one search parameter is required.

**Parameters:**
- Same as query() method, except page and per_page are handled internally
- `max_items` (Optional[int]): Maximum number of items to return (None for all)

**Yields:**
- `Dict[str, Any]`: Individual contact records

**Raises:**
- `ValueError`: If no search parameters are provided

#### `update(id: int, firstname: str, phone: str, lastname: Optional[str] = None, email: Optional[str] = None, company: Optional[str] = None, notes: Optional[str] = None, other_phones: Optional[Dict[str, str]] = None) -> Dict[str, Any]`

Update a contact's information.

**Parameters:**
- `id` (int): Unique id of the contact
- `firstname` (str): First name of the contact
- `phone` (str): Phone number of the contact
- `lastname` (Optional[str]): Last name of the contact
- `email` (Optional[str]): Email address associated with the contact
- `company` (Optional[str]): Company associated with the contact
- `notes` (Optional[str]): Custom information to associate with the contact
- `other_phones` (Optional[Dict[str, str]]): Additional phone numbers as {label: number}

**Returns:**
- `Dict[str, Any]`: Updated contact information

**Raises:**
- `ValueError`: If required fields are missing

#### `create(firstname: str, phone: str, lastname: Optional[str] = None, email: Optional[str] = None, company: Optional[str] = None, notes: Optional[str] = None, acrossteam: Optional[int] = None, agentid: Optional[int] = None) -> Dict[str, Any]`

Create a new contact.

**Parameters:**
- `firstname` (str): First name of the contact
- `phone` (str): Phone number of the contact
- `lastname` (Optional[str]): Last name of the contact
- `email` (Optional[str]): Email address associated with the contact
- `company` (Optional[str]): Company associated with the contact
- `notes` (Optional[str]): Custom information to associate with the contact
- `acrossteam` (Optional[int]): 1 to create contact for all team members, 0 or None for account owner only
- `agentid` (Optional[int]): Create contact only for specific agent ID

**Returns:**
- `Dict[str, Any]`: Created contact information

**Raises:**
- `ValueError`: If required fields are missing or invalid

#### `delete(id: int) -> Dict[str, Any]`

Delete a contact.

**Parameters:**
- `id` (int): Unique id of the contact to delete

**Returns:**
- `Dict[str, Any]`: Response indicating success/failure

**Raises:**
- `JustCallException`: If deletion fails or contact doesn't exist

#### `action(number: str, type: Union[str, ContactActionType], action: Union[str, ContactActionOperation], acrossteam: Optional[str] = "1") -> Dict[str, Any]`

Perform actions on a contact number (add/remove to/from DND, blacklist, etc).

**Parameters:**
- `number` (str): Phone number to act on
- `type` (Union[str, ContactActionType]): Type of action:
  - "0" - Blacklist number
  - "1" - Add to DND list
  - "2" - Add to DNM list
- `action` (Union[str, ContactActionOperation]): Action to perform:
  - "0" - Remove from list
  - "1" - Add to list
- `acrossteam` (Optional[str]): Apply across team ("1") or individual ("0"), defaults to "1"

**Returns:**
- `Dict[str, Any]`: Response indicating success/failure

**Raises:**
- `JustCallException`: If the action fails
- `ValueError`: If parameters are invalid