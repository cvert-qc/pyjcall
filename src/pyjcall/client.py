from typing import Dict, Any, Union, AsyncIterator, Optional
import aiohttp
from datetime import date, datetime
from .resources.calls import Calls
from .utils.exceptions import JustCallException
from .utils.rate_limiter import RateLimiter, RateLimitStrategy
from .utils.datetime import to_api_date, to_api_datetime
from .resources.messages import Messages
from .resources.phone_numbers import PhoneNumbers
from .resources.users import Users
from .resources.contacts import Contacts
from .resources.campaigns import Campaigns
from .resources.campaign_contacts import CampaignContacts
from .resources.campaign_calls import CampaignCalls

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
        
        # Initialize rate limiter with settings matching JustCall API limits
        # JustCall API has a dual rate limiting system:
        # 1. Burst limit: 60 requests in a short period
        # 2. General limit: 3600 requests per hour (1 per second)
        self.rate_limiter = RateLimiter(
            rate=1.0,  # 1 request per second (3600 per hour)
            max_tokens=60,  # Match the burst limit of 60 requests
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            window_size=60.0,  # 60-second window for window-based strategies
        )
        
        # Track API rate limit info
        self.rate_limit_info = {
            "burst_limit": 60,
            "burst_remaining": 60,
            "burst_reset": 0,
            "limit": 3600,
            "remaining": 3600,
            "reset": 0
        }
        
        # Rate limit backoff settings
        self.backoff_factor = 1.5  # Exponential backoff multiplier
        self.max_retries = 5      # Maximum number of retries
        self.retry_delay = 2.0    # Initial retry delay in seconds
        self.current_retry = 0    # Current retry count
        
        # Initialize resources
        self._calls = Calls(self)
        self._messages = Messages(self)
        self._phone_numbers = PhoneNumbers(self)
        self._users = Users(self)
        self._contacts = Contacts(self)
        self._campaigns = Campaigns(self)
        self._campaign_contacts = CampaignContacts(self)
        self._campaign_calls = CampaignCalls(self)

    async def __aenter__(self):
        """Create aiohttp session when entering context manager."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"{self.api_key}:{self.api_secret}",
                "Accept": "application/json",
                "Content-Type": "application/json"
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
        expect_json: bool = True,
        retry_count: int = 0
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
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )

        # Convert parameter values to appropriate string formats
        if params:
            params = self._prepare_request_params(params)

        # Use the endpoint for rate limiting
        await self.rate_limiter.acquire(endpoint)
        
        # If we're retrying, add exponential backoff delay
        if retry_count > 0:
            backoff_time = self.retry_delay * (self.backoff_factor ** (retry_count - 1))
            print(f"Retry attempt {retry_count}/{self.max_retries}: Waiting {backoff_time:.2f} seconds before retrying...")
            await asyncio.sleep(backoff_time)

        try:
            url = f"{self.base_url}{endpoint}"
            
            async with self.session.request(method, url, params=params, json=json) as response:
                # Always update rate limit info from headers if available
                self._update_rate_limits_from_headers(response.headers)
                
                if response.status >= 400:
                    error_data = await response.json()
                    error_message = error_data.get('message', 'Unknown error')
                    
                    # Check if it's a rate limit error
                    if 'rate limit' in error_message.lower() or response.status == 429:
                        # Extract and log rate limit headers
                        rate_limit_headers = {
                            k: v for k, v in response.headers.items() 
                            if 'rate' in k.lower() or 'limit' in k.lower() or 'remaining' in k.lower()
                        }
                        
                        # Print headers to help with debugging
                        headers_str = '\n'.join([f"{k}: {v}" for k, v in rate_limit_headers.items()])
                        print(f"\nRate limit exceeded. Headers:\n{headers_str}\n")
                        
                        # Adjust rate limiter based on headers
                        await self._adjust_rate_limiter_from_headers(rate_limit_headers)
                        
                        # Try to retry the request if we haven't exceeded max retries
                        if retry_count < self.max_retries:
                            print(f"Retrying request to {endpoint} (attempt {retry_count+1}/{self.max_retries})")
                            return await self._make_request(
                                method=method,
                                endpoint=endpoint,
                                params=params,
                                json=json,
                                expect_json=expect_json,
                                retry_count=retry_count + 1
                            )
                        
                        # Include headers in the exception message
                        error_message = f"{error_message} Headers: {rate_limit_headers}"
                    
                    raise JustCallException(
                        status_code=response.status,
                        message=f"API Error: {error_message}"
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
                # Also convert any datetime objects in JSON body
                json = self._prepare_request_params(json)
            
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

    @property
    def Campaigns(self) -> Campaigns:
        return self._campaigns

    @property
    def CampaignContacts(self) -> CampaignContacts:
        return self._campaign_contacts

    @property
    def CampaignCalls(self) -> CampaignCalls:
        return self._campaign_calls
        
    def _update_rate_limits_from_headers(self, headers):
        """Update internal rate limit tracking based on response headers.
        
        Args:
            headers: Response headers from API call
        """
        # Extract rate limit headers
        try:
            # Burst limits
            if 'x-rate-limit-burst-limit' in headers:
                self.rate_limit_info['burst_limit'] = int(headers['x-rate-limit-burst-limit'])
            if 'x-rate-limit-burst-remaining' in headers:
                self.rate_limit_info['burst_remaining'] = int(headers['x-rate-limit-burst-remaining'])
            if 'x-rate-limit-burst-reset' in headers:
                self.rate_limit_info['burst_reset'] = int(headers['x-rate-limit-burst-reset'])
                
            # General limits
            if 'x-rate-limit-limit' in headers:
                self.rate_limit_info['limit'] = int(headers['x-rate-limit-limit'])
            if 'x-rate-limit-remaining' in headers:
                self.rate_limit_info['remaining'] = int(headers['x-rate-limit-remaining'])
            if 'x-rate-limit-reset' in headers:
                self.rate_limit_info['reset'] = int(headers['x-rate-limit-reset'])
        except (ValueError, KeyError) as e:
            print(f"Error parsing rate limit headers: {e}")
    
    async def _adjust_rate_limiter_from_headers(self, headers):
        """Adjust rate limiter settings based on rate limit headers.
        
        Args:
            headers: Rate limit headers from API response
        """
        try:
            # If we're hitting burst limits, slow down dramatically
            if 'x-rate-limit-burst-remaining' in headers and int(headers['x-rate-limit-burst-remaining']) == 0:
                burst_reset = int(headers.get('x-rate-limit-burst-reset', 60))
                print(f"Adjusting rate limiter: Burst limit reached. Slowing down for {burst_reset} seconds.")
                
                # Slow down the rate limiter significantly
                self.rate_limiter.rate = 1.0 / (burst_reset + 10)  # Add larger buffer
                
                # Reduce the max tokens to prevent bursts
                self.rate_limiter.max_tokens = max(1, self.rate_limiter.max_tokens // 2)
                
                # If we have a reset time, wait that long plus a buffer
                if burst_reset > 0:
                    # Add more buffer time for higher reset values
                    buffer = min(30, burst_reset // 2 + 5)  # More buffer for longer reset times
                    wait_time = burst_reset + buffer
                    print(f"Waiting for {wait_time} seconds before continuing...")
                    import asyncio
                    await asyncio.sleep(wait_time)  # Wait for reset plus buffer
        except Exception as e:
            print(f"Error adjusting rate limiter: {e}")
    
    def _prepare_request_params(self, params: Dict) -> Dict:
        """Convert parameter values to appropriate string formats for API requests.
        
        Handles:
        - Boolean values to integers (True -> 1, False -> 0)
        - datetime objects to string format
        - date objects to string format
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            Dictionary with values converted to appropriate string formats
        """
        if not params:
            return params
            
        result = {}
        for k, v in params.items():
            if v is True:
                result[k] = 1
            elif v is False:
                result[k] = 0
            elif isinstance(v, datetime):
                result[k] = to_api_datetime(v)
            elif isinstance(v, date):
                result[k] = to_api_date(v)
            elif isinstance(v, dict):
                result[k] = self._prepare_request_params(v)
            elif isinstance(v, list):
                result[k] = [self._prepare_request_params(item) if isinstance(item, dict) 
                             else to_api_datetime(item) if isinstance(item, datetime)
                             else to_api_date(item) if isinstance(item, date)
                             else item 
                             for item in v]
            else:
                result[k] = v
                
        return result