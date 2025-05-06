"""
Retry mechanism for handling API rate limits and transient errors.
"""
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, TypeVar, Set

logger = logging.getLogger(__name__)

# Type variable for generic return type
T = TypeVar('T')

# Constants for retry configuration
DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_DELAY = 2.0
DEFAULT_BACKOFF_FACTOR = 1.5
DEFAULT_RETRY_CODES = {429, 500, 502, 503, 504}
MAX_BACKOFF_TIME = 60.0  # Maximum backoff time in seconds


@dataclass
class RetryConfig:
    """Configuration for retry mechanism."""
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay: float = DEFAULT_RETRY_DELAY
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    retry_codes: Set[int] = field(default_factory=lambda: DEFAULT_RETRY_CODES.copy())


class RetryHandler:
    """Handles retrying operations with exponential backoff."""

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        retry_codes: Optional[set] = None
    ):
        """Initialize the retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            backoff_factor: Multiplier for exponential backoff
            retry_codes: HTTP status codes that should trigger a retry
        """
        self.config = RetryConfig(
            max_retries=max_retries,
            retry_delay=retry_delay,
            backoff_factor=backoff_factor,
            retry_codes=retry_codes or DEFAULT_RETRY_CODES
        )
        self.current_retry = 0
        
        logger.debug(
            f"Initialized RetryHandler with max_retries={max_retries}, "
            f"retry_delay={retry_delay}s, backoff_factor={backoff_factor}"
        )
    
    def reset(self) -> None:
        """Reset the retry counter."""
        self.current_retry = 0
    
    def should_retry(self, status_code: int, retry_count: int) -> bool:
        """Determine if a retry should be attempted based on status code and retry count.
        
        Args:
            status_code: HTTP status code from the response
            retry_count: Current retry attempt count
            
        Returns:
            True if a retry should be attempted, False otherwise
        """
        return status_code in self.config.retry_codes and retry_count < self.config.max_retries
    
    def wait_before_retry(self, retry_count: int) -> None:
        """Wait with exponential backoff before the next retry attempt.
        
        Args:
            retry_count: Current retry attempt count
        """
        if retry_count <= 0:
            return
            
        backoff_time = self.config.retry_delay * (self.config.backoff_factor ** (retry_count - 1))
        # Cap the backoff time to avoid excessive waits
        backoff_time = min(backoff_time, MAX_BACKOFF_TIME)
        
        logger.info(f"Retry attempt {retry_count}/{self.config.max_retries}: "
                   f"Waiting {backoff_time:.2f} seconds before retrying...")
        
        time.sleep(backoff_time)
    
    def execute_with_retry(
        self,
        func: Callable[..., T],
        *args: Any,
        rate_limiter=None,
        **kwargs: Any
    ) -> T:
        """Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            rate_limiter: Optional rate limiter instance to update from response headers
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call
            
        Raises:
            The last exception encountered after all retries are exhausted
        """
        retry_count = 0
        last_exception = None
        
        while retry_count <= self.config.max_retries:
            try:
                if retry_count > 0:
                    self.wait_before_retry(retry_count)
                
                result = func(*args, **kwargs)
                
                # If we have a rate limiter and the result has headers, update the rate limiter
                if rate_limiter and hasattr(result, 'headers'):
                    rate_limiter.update_from_headers(result.headers)
                    # Mark the request as successful to reset consecutive error counter
                    rate_limiter.mark_request_success()
                    
                return result
                
            except Exception as e:
                last_exception = e
                retry_count += 1
                
                # Check if we should retry based on the exception
                should_retry = False
                
                # Extract status code if it's an HTTP error
                status_code = getattr(e, 'status_code', None)
                if status_code is not None:
                    should_retry = self.should_retry(status_code, retry_count)
                
                # Check for rate limit headers in the exception
                headers = getattr(e, 'headers', None)
                if headers and rate_limiter:
                    # Update rate limiter with headers from the exception
                    rate_limiter.update_from_headers(headers)
                    
                    # If it's a rate limit error, we should always retry
                    if status_code == 429:
                        should_retry = retry_count <= self.config.max_retries
                
                if not should_retry:
                    logger.warning(f"Not retrying: {str(e)}")
                    raise
                
                # Extract and log rate limit headers if present in the exception
                if headers and any(k.startswith('x-rate-limit') for k in headers.keys()):
                    header_info = '\n'.join([f"{k}: {v}" for k, v in headers.items() 
                                           if k.startswith('x-rate-limit')])
                    logger.warning(f"Retrying due to error: {str(e)}. Headers: {{{header_info}}}")
                else:
                    logger.warning(f"Retrying due to error: {str(e)}")
        
        # If we've exhausted all retries, raise the last exception
        if last_exception:
            logger.error(f"All retry attempts failed. Last error: {str(last_exception)}")
            raise last_exception
        
        # This should never happen, but just in case
        raise RuntimeError("Unexpected error in retry logic")
    
    def update_config(self, config: RetryConfig) -> None:
        """Update the retry configuration.
        
        Args:
            config: New configuration to apply
        """
        self.config = config
        logger.info(f"Retry configuration updated: max_retries={config.max_retries}, "
                   f"retry_delay={config.retry_delay}s, backoff_factor={config.backoff_factor}")
