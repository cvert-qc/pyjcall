from typing import Dict, Any, Union, AsyncIterator, Optional
import aiohttp
from .resources.calls import Calls
from .utils.exceptions import JustCallException
from .utils.rate_limiter import RateLimiter
from .resources.messages import Messages
from .resources.phone_numbers import PhoneNumbers
from .resources.users import Users
from .resources.contacts import Contacts

class JustCallClient:
    def __init__(self, api_key: str, api_secret: str):
        """Initialize the JustCall API client.
        
        Args:
            api_key (str): Your JustCall API key
            api_secret (str): Your JustCall API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.justcall.io"
        self.session = None
        self.rate_limiter = RateLimiter()
        
        # Initialize resources
        self._calls = Calls(self)
        self._messages = Messages(self)
        self._phone_numbers = PhoneNumbers(self)
        self._users = Users(self)
        self._contacts = Contacts(self)

    async def __aenter__(self):
        """Create aiohttp session when entering context manager."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"{self.api_key}:{self.api_secret}",
                "Accept": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session when exiting context manager."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict = None, 
        json: Dict = None,
        expect_json: bool = True
    ) -> Union[Dict[str, Any], bytes]:
        """Make an HTTP request to the JustCall API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (Dict, optional): Query parameters
            json (Dict, optional): JSON body for POST/PUT requests
            expect_json (bool, optional): Whether to expect JSON response
            
        Returns:
            Union[Dict[str, Any], bytes]: API response
            
        Raises:
            JustCallException: If the API request fails
        """
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"{self.api_key}:{self.api_secret}",
                    "Accept": "application/json"
                }
            )

        # Convert boolean values to integers    
        if params:
            params = {
                k: (1 if v is True else 0 if v is False else v)
                for k, v in params.items()
            }

        await self.rate_limiter.acquire()

        try:
            url = f"{self.base_url}{endpoint}"
            
            async with self.session.request(method, url, params=params, json=json) as response:
                if response.status >= 400:
                    error_data = await response.json()
                    raise JustCallException(
                        status_code=response.status,
                        message=f"API Error: {error_data.get('message', 'Unknown error')}"
                    )
                
                if expect_json:
                    data = await response.json()
                    return data
                else:
                    return await response.read()
                
        except aiohttp.ClientError as e:
            raise JustCallException(
                status_code=500,
                message=f"Request failed: {str(e)}"
            )

    async def _paginate(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json: Dict = None,
        page_key: str = "page",
        per_page_key: str = "per_page",
        items_key: str = "data",
        max_items: int = None,
        start_page: int = 0
    ) -> AsyncIterator[Dict[str, Any]]:
        """Helper method to handle pagination across all resources.
        
        Args:
            method: HTTP method to use
            endpoint: API endpoint
            params: Query parameters (for GET requests)
            json: JSON body (for POST requests)
            page_key: Key used for page number in request
            per_page_key: Key used for items per page in request
            items_key: Key containing items in response
            max_items: Maximum number of items to return (None for all)
            start_page: Starting page number (0 for v2 API, 1 for v1 API)
            
        Yields:
            Individual items from paginated responses
        """
        items_returned = 0
        page = start_page  # Use the provided start page
        
        while True:
            # Update page number in the appropriate request data
            if method.upper() == "GET" and params is not None:
                params[page_key] = str(page)
            elif json is not None:
                json[page_key] = str(page)
            
            # Make the request
            response = await self._make_request(
                method=method,
                endpoint=endpoint,
                params=params,
                json=json
            )
            
            # Get items from response, handling different response structures
            items = []
            if isinstance(response, dict):
                items = response.get(items_key, [])
                if not items and items_key in response:
                    # Handle case where items_key exists but is None/empty
                    break
                elif not items and 'contacts' in response:
                    # Special case for contacts API
                    items = response.get('contacts', [])
            
            if not items:
                break
            
            for item in items:
                if max_items and items_returned >= max_items:
                    return
                yield item
                items_returned += 1
            
            page += 1

    # Resource properties
    @property
    def Calls(self) -> Calls:
        return self._calls

    @property
    def Messages(self) -> Messages:
        return self._messages

    @property
    def PhoneNumbers(self) -> PhoneNumbers:
        return self._phone_numbers

    @property
    def Users(self) -> Users:
        return self._users

    @property
    def Contacts(self) -> Contacts:
        return self._contacts