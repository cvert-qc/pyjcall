from typing import Dict, Any, Union, Iterator, Optional, Tuple
import requests
import time
import threading
import logging
from datetime import date, datetime
from .resources.calls import Calls
from .utils.exceptions import JustCallException
from .utils.rate_limiter import RateLimiter, RateLimitStrategy, RateLimitConfig
from .utils.retry import RetryHandler, RetryConfig
from .utils.datetime import to_api_date, to_api_datetime
from .resources.messages import Messages
from .resources.phone_numbers import PhoneNumbers
from .resources.users import Users
from .resources.contacts import Contacts
from .resources.campaigns import Campaigns
from .resources.campaign_contacts import CampaignContacts
from .resources.campaign_calls import CampaignCalls

logger = logging.getLogger(__name__)

# Constants for rate limiting and retry configuration
DEFAULT_RATE = 1.0  # 1 request per second (3600 per hour)
DEFAULT_MAX_TOKENS = 60  # Match the burst limit of 60 requests
DEFAULT_WINDOW_SIZE = 60.0  # 60-second window for window-based strategies
DEFAULT_BACKOFF_FACTOR = 1.5  # Exponential backoff multiplier
DEFAULT_MAX_RETRIES = 5  # Maximum number of retries
DEFAULT_RETRY_DELAY = 2.0  # Initial retry delay in seconds

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
            rate=DEFAULT_RATE,
            max_tokens=DEFAULT_MAX_TOKENS,
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            window_size=DEFAULT_WINDOW_SIZE,
        )
        
        # Initialize retry handler for handling rate limit errors and transient failures
        self.retry_handler = RetryHandler(
            max_retries=DEFAULT_MAX_RETRIES,
            retry_delay=DEFAULT_RETRY_DELAY,
            backoff_factor=DEFAULT_BACKOFF_FACTOR
        )
        
        # Track API rate limit info
        self.rate_limit_info = {
            "burst_limit": DEFAULT_MAX_TOKENS,
            "burst_remaining": DEFAULT_MAX_TOKENS,
            "burst_reset": 0,
            "limit": 3600,
            "remaining": 3600,
            "reset": 0
        }
        
        # Initialize resources
        self._calls = Calls(self)
        self._messages = Messages(self)
        self._phone_numbers = PhoneNumbers(self)
        self._users = Users(self)
        self._contacts = Contacts(self)
        self._campaigns = Campaigns(self)
        self._campaign_contacts = CampaignContacts(self)
        self._campaign_calls = CampaignCalls(self)
        
        logger.info(f"Initialized JustCallClient with rate limiting and retry mechanisms")

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
            JustCallException: If the API request fails after all retries are exhausted
        """
        # Define the actual request function to be used with retry mechanism
        def _do_request() -> Union[Dict[str, Any], bytes]:
            if not self.session:
                self.session = requests.Session()
                self.session.headers.update({
                    "Authorization": f"{self.api_key}:{self.api_secret}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                })

            # Convert parameter values to appropriate string formats
            request_params = self._prepare_request_params(params) if params else None

            # Use the endpoint for rate limiting
            self.rate_limiter.acquire(endpoint)
            
            try:
                url = f"{self.base_url}{endpoint}"
                logger.debug(f"Making {method} request to {url}")
                
                response = self.session.request(method, url, params=request_params, json=json)
                
                # Always update rate limit info from headers if available
                self._update_rate_limits_from_headers(response.headers)
                
                if response.status_code >= 400:
                    # Try to parse error response as JSON
                    try:
                        error_data = response.json()
                        error_message = error_data.get('message', 'Unknown error')
                    except Exception:
                        # If JSON parsing fails, use the text or status
                        error_message = response.text or f"HTTP {response.status_code}"
                    
                    # Check if it's a rate limit error
                    if 'rate limit' in error_message.lower() or response.status_code == 429:
                        # Extract and log rate limit headers
                        rate_limit_headers = {
                            k: v for k, v in response.headers.items() 
                            if 'rate' in k.lower() or 'limit' in k.lower() or 'remaining' in k.lower()
                        }
                        
                        # Log headers to help with debugging
                        headers_str = '\n'.join([f"{k}: {v}" for k, v in rate_limit_headers.items()])
                        logger.warning(f"Rate limit exceeded. Headers:\n{headers_str}")
                        
                        # Adjust rate limiter based on headers
                        self._adjust_rate_limiter_from_headers(rate_limit_headers)
                        
                        # Include headers in the exception message
                        error_message = f"{error_message} Headers: {rate_limit_headers}"
                    
                    exception = JustCallException(
                        status_code=response.status_code,
                        message=f"API Error: {error_message}"
                    )
                    
                    # Add the response headers to the exception for retry logic
                    exception.headers = dict(response.headers)
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
        
        # Use the retry handler to execute the request with retry logic
        try:
            return self.retry_handler.execute_with_retry(_do_request)
        except JustCallException as e:
            # Re-raise JustCallException directly
            raise
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
        
    def _update_rate_limits_from_headers(self, headers: Dict[str, str]) -> None:
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
                
            # Log rate limit information at debug level
            logger.debug(f"Rate limit info updated: burst_remaining={self.rate_limit_info['burst_remaining']}, "
                         f"remaining={self.rate_limit_info['remaining']}")
        except (ValueError, KeyError) as e:
            logger.warning(f"Error parsing rate limit headers: {e}")
    
    def _adjust_rate_limiter_from_headers(self, headers: Dict[str, str]) -> None:
        """Adjust rate limiter settings based on rate limit headers.
        
        Args:
            headers: Rate limit headers from API response
        """
        # Constants for rate limiting adjustments
        MIN_RATE = 1.0 / 60.0  # Minimum rate: 1 request per minute
        BUFFER_FACTOR = 1.2    # Safety buffer factor for rate limiting
        SHORT_WAIT_FACTOR = 0.25  # Factor for short wait calculation
        MAX_SHORT_WAIT = 5.0  # Maximum short wait time in seconds
        
        try:
            # If we're hitting burst limits, slow down dramatically
            if 'x-rate-limit-burst-remaining' in headers:
                burst_remaining = int(headers['x-rate-limit-burst-remaining'])
                burst_reset = int(headers.get('x-rate-limit-burst-reset', 60))
                
                # Calculate how much to slow down based on remaining burst capacity
                if burst_remaining == 0:
                    logger.warning(f"Burst limit reached. Slowing down for {burst_reset} seconds.")
                    
                    # Create a new rate limit configuration
                    new_rate = max(MIN_RATE, 1.0 / (burst_reset * BUFFER_FACTOR))
                    new_max_tokens = 1  # No bursting when we've hit limits
                    
                    # Update the rate limiter configuration
                    self.rate_limiter.rate = new_rate
                    self.rate_limiter.max_tokens = new_max_tokens
                    
                    logger.info(f"Rate limiter adjusted: rate={new_rate:.6f}/s, max_tokens={new_max_tokens}")
                    
                    # Add a short sleep to give immediate relief but not block the job
                    short_wait = min(MAX_SHORT_WAIT, burst_reset * SHORT_WAIT_FACTOR)
                    logger.info(f"Short wait of {short_wait:.1f} seconds to relieve pressure...")
                    time.sleep(short_wait)
                    
                    # Update retry handler configuration
                    new_retry_config = RetryConfig(
                        max_retries=self.retry_handler.config.max_retries,
                        retry_delay=max(self.retry_handler.config.retry_delay, burst_reset / 2),
                        backoff_factor=2.0,  # More aggressive backoff
                        retry_codes=self.retry_handler.config.retry_codes
                    )
                    self.retry_handler.update_config(new_retry_config)
                    
                elif burst_remaining < 10:  # Getting close to limits
                    # Gradually slow down as we approach limits
                    slowdown_factor = max(0.2, burst_remaining / 10.0)
                    new_rate = self.rate_limiter.rate * slowdown_factor
                    
                    logger.info(f"Approaching burst limit ({burst_remaining} remaining). "
                               f"Reducing rate to {new_rate:.6f}/s")
                    
                    self.rate_limiter.rate = new_rate
            
            # Also check general rate limits
            if 'x-rate-limit-remaining' in headers and 'x-rate-limit-limit' in headers:
                remaining = int(headers['x-rate-limit-remaining'])
                limit = int(headers['x-rate-limit-limit'])
                reset = int(headers.get('x-rate-limit-reset', 3600))
                
                # If we're below 10% of our limit, slow down
                if remaining < limit * 0.1 and remaining > 0:
                    new_rate = max(MIN_RATE, remaining / reset)
                    logger.info(f"General rate limit low ({remaining}/{limit} remaining). "
                               f"Adjusting rate to {new_rate:.6f}/s")
                    self.rate_limiter.rate = new_rate
                    
        except Exception as e:
            logger.error(f"Error adjusting rate limiter: {e}")
            # Don't let rate limiter adjustment failures break the client
            # Just continue with current settings
    
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