from typing import Dict, Any, Union, AsyncIterator
import aiohttp
from .resources.calls import Calls
from .utils.exceptions import JustCallException
from .utils.rate_limiter import RateLimiter
from .resources.messages import Messages
from .resources.phone_numbers import PhoneNumbers
from .resources.users import Users

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
            print(f"Making request to: {url}")  # Debug info
            if params:
                print(f"With params: {params}")  # Debug info
            
            async with self.session.request(method, url, params=params, json=json) as response:
                if response.status >= 400:
                    error_data = await response.json()
                    raise JustCallException(
                        status_code=response.status,
                        message=f"API Error: {error_data.get('message', 'Unknown error')}. URL: {url}, Params: {params}"
                    )
                
                if expect_json:
                    return await response.json()
                else:
                    return await response.read()
                
        except aiohttp.ClientError as e:
            raise JustCallException(
                status_code=500,
                message=f"Request failed: {str(e)}. URL: {url}, Params: {params}"
            )

    async def _paginate(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        page_key: str = "page",
        per_page_key: str = "per_page",
        items_key: str = "data",
        max_items: int = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Helper method to handle pagination across all resources.
        
        Args:
            method: HTTP method to use
            endpoint: API endpoint
            params: Query parameters
            page_key: Key used for page number in params
            per_page_key: Key used for items per page in params
            items_key: Key containing items in response
            max_items: Maximum number of items to return (None for all)
            
        Yields:
            Individual items from paginated responses
        """
        params = params or {}
        items_returned = 0
        page = params.get(page_key, 0)
        
        while True:
            params[page_key] = page
            response = await self._make_request(method, endpoint, params=params)
            
            items = response.get(items_key, [])
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