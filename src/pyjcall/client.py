from typing import Dict, Any, Union, Iterator, Optional, Tuple
import requests
import time
import threading
import logging
from datetime import date, datetime
from limits import RateLimitItemPerSecond
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter
from .resources.calls import Calls
from .utils.exceptions import JustCallException
from .utils.datetime import to_api_date, to_api_datetime
from .resources.messages import Messages
from .resources.phone_numbers import PhoneNumbers
from .resources.users import Users
from .resources.contacts import Contacts
from .resources.campaigns import Campaigns
from .resources.campaign_contacts import CampaignContacts
from .resources.campaign_calls import CampaignCalls

logger = logging.getLogger(__name__)

# Rate limiting constants
DEFAULT_RATE_LIMIT = 60  # requests per minute
RATE_LIMIT_NAMESPACE = "justcall_api"

class JustCallClient:
    def __init__(self, api_key: str, api_secret: str, rate_limit: int = DEFAULT_RATE_LIMIT):
        """Initialize the JustCall API client.
        
        Args:
            api_key (str): Your JustCall API key
            api_secret (str): Your JustCall API secret
            rate_limit (int, optional): Maximum number of requests per minute. Defaults to 60.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.justcall.io"
        self.session = None
        
        # Initialize rate limiter with moving window strategy
        self.rate_limit = rate_limit
        self.storage = MemoryStorage()
        self.rate_limiter = MovingWindowRateLimiter(self.storage)
        self.rate = RateLimitItemPerSecond(rate_limit, 60)
        
        # Initialize resources
        self._calls = Calls(self)
        self._messages = Messages(self)
        self._phone_numbers = PhoneNumbers(self)
        self._users = Users(self)
        self._contacts = Contacts(self)
        self._campaigns = Campaigns(self)
        self._campaign_contacts = CampaignContacts(self)
        self._campaign_calls = CampaignCalls(self)
        
        logger.info(f"Initialized JustCallClient with rate limit of {rate_limit} requests per minute")

    def __enter__(self):
        """Create requests session when entering context manager."""
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"{self.api_key}:{self.api_secret}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close requests session when exiting context manager."""
        if self.session:
            self.session.close()
            self.session = None

    def _make_request(
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
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"{self.api_key}:{self.api_secret}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            })

        # Convert parameter values to appropriate string formats
        request_params = self._prepare_request_params(params) if params else None
        
        try:
            url = f"{self.base_url}{endpoint}"
            logger.debug(f"Making {method} request to {url}")
            
            # Apply rate limiting
            if not self.rate_limiter.test(self.rate, RATE_LIMIT_NAMESPACE, "api"):
                # If we've hit the rate limit, calculate sleep time
                # Wait for a short time before retrying
                sleep_time = 5.0  # Default to 1 second
                logger.warning(f"Rate limit reached for justcall api, sleeping for {sleep_time:.2f} seconds")

                count = 0
                while not self.rate_limiter.test(self.rate, RATE_LIMIT_NAMESPACE, "api") and count < 120:
                    time.sleep(1)
                    count += 1
                
                # Try again after waiting
                if not self.rate_limiter.test(self.rate, RATE_LIMIT_NAMESPACE, "api"):
                    raise JustCallException(
                        status_code=429,
                        message="Rate limit exceeded and could not recover"
                    )
            
            # If we passed the test, actually consume the quota
            self.rate_limiter.hit(self.rate, RATE_LIMIT_NAMESPACE, "api")
            
            response = self.session.request(method, url, params=request_params, json=json)
            
            if response.status_code >= 400:
                # Try to parse error response as JSON
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Unknown error')
                except Exception:
                    # If JSON parsing fails, use the text or status
                    error_message = response.text or f"HTTP {response.status_code}"
                
                exception = JustCallException(
                    status_code=response.status_code,
                    message=f"API Error: {error_message}"
                )
                raise exception
                
            if expect_json:
                try:
                    return response.json()
                except ValueError:
                    # Handle case where response is not JSON despite expect_json=True
                    content = response.content
                    logger.warning(f"Expected JSON response but got non-JSON content: {content[:100]}...")
                    raise JustCallException(
                        status_code=response.status_code,
                        message="Invalid JSON response from API"
                    )
            else:
                return response.content
            
        except requests.RequestException as e:
            logger.error(f"HTTP client error: {str(e)}")
            raise JustCallException(
                status_code=500,
                message=f"Request failed: {str(e)}"
            )
        except Exception as e:
            # Wrap other exceptions in JustCallException
            logger.error(f"Unexpected error during API request: {str(e)}")
            raise JustCallException(
                status_code=500,
                message=f"Unexpected error: {str(e)}"
            )

    def _paginate(
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
    ) -> Iterator[Dict[str, Any]]:
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
            response = self._make_request(
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