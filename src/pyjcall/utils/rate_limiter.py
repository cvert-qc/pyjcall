import time
import threading
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Callable, Any, Deque, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Enum for different rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"


# Constants for rate limiting
DEFAULT_RATE = 1.0  # Default requests per second
DEFAULT_MAX_TOKENS = 5  # Default maximum burst size
DEFAULT_WINDOW_SIZE = 60.0  # Default window size in seconds
MIN_WAIT_TIME = 0.1  # Minimum wait time in seconds
DEFAULT_PRESSURE_RELIEF_WAIT = 0.5  # Default wait time to relieve pressure
DEFAULT_JITTER_FACTOR = 0.1  # Default jitter factor (10%)

# Rate limit header constants
HEADER_BURST_LIMIT = "x-rate-limit-burst-limit"
HEADER_BURST_REMAINING = "x-rate-limit-burst-remaining"
HEADER_BURST_RESET = "x-rate-limit-burst-reset"
HEADER_LIMIT = "x-rate-limit-limit"
HEADER_REMAINING = "x-rate-limit-remaining"
HEADER_RESET = "x-rate-limit-reset"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    rate: float = DEFAULT_RATE
    max_tokens: int = DEFAULT_MAX_TOKENS
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    window_size: float = DEFAULT_WINDOW_SIZE
    endpoint_limits: Dict[str, float] = field(default_factory=dict)
    pressure_relief_wait: float = DEFAULT_PRESSURE_RELIEF_WAIT
    jitter_factor: float = DEFAULT_JITTER_FACTOR
    adaptive: bool = True  # Whether to adapt to API rate limit headers

class RateLimiter:
    """Advanced rate limiter implementation with multiple strategies.
    
    Default settings:
    - 60 requests per minute (1 request per second)
    - Burst of up to 5 requests
    
    Supports different rate limiting strategies:
    - TOKEN_BUCKET: Classic token bucket algorithm (default)
    - FIXED_WINDOW: Fixed time window counting
    - SLIDING_WINDOW: Sliding time window counting
    """
    
    def __init__(
        self,
        rate: float = DEFAULT_RATE,  # tokens/requests per second
        max_tokens: int = DEFAULT_MAX_TOKENS,  # maximum burst size
        strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET,
        window_size: float = DEFAULT_WINDOW_SIZE,  # window size in seconds (for window-based strategies)
        endpoint_limits: Optional[Dict[str, float]] = None,  # endpoint-specific rate limits
        pressure_relief_wait: float = DEFAULT_PRESSURE_RELIEF_WAIT,  # wait time to relieve pressure
        jitter_factor: float = DEFAULT_JITTER_FACTOR,  # jitter factor for distributed environments
        adaptive: bool = True,  # whether to adapt to API rate limit headers
    ):
        self.config = RateLimitConfig(
            rate=rate,
            max_tokens=max_tokens,
            strategy=strategy,
            window_size=window_size,
            endpoint_limits=endpoint_limits or {},
            pressure_relief_wait=pressure_relief_wait,
            jitter_factor=jitter_factor,
            adaptive=adaptive
        )
        
        # Token bucket state
        self.tokens = max_tokens
        self.last_update = time.monotonic()
        
        # Window-based state - using deque for more efficient operations
        self.request_timestamps: Dict[str, Deque[float]] = {}  # endpoint -> deque of timestamps
        
        # Concurrency control
        self._lock = threading.Lock()
        
        # Request tracking
        self.request_count = 0
        self.endpoint_counts: Dict[str, int] = {}
        
        # Rate limit state from API headers
        self.burst_limit = max_tokens
        self.burst_remaining = max_tokens
        self.burst_reset = 0
        self.global_limit = int(rate * window_size)
        self.global_remaining = self.global_limit
        self.global_reset = 0
        self.last_header_update = 0
        
        logger.info(f"Initialized RateLimiter with strategy: {strategy.value}, rate: {rate}/s, adaptive: {adaptive}")
    
    @property
    def rate(self) -> float:
        return self.config.rate
    
    @rate.setter
    def rate(self, value: float) -> None:
        self.config.rate = value
        logger.debug(f"Rate updated to: {value}/s")
    
    @property
    def max_tokens(self) -> int:
        return self.config.max_tokens
    
    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        self.config.max_tokens = value
        logger.debug(f"Max tokens updated to: {value}")
    
    @property
    def strategy(self) -> RateLimitStrategy:
        return self.config.strategy
    
    @strategy.setter
    def strategy(self, value: RateLimitStrategy) -> None:
        self.config.strategy = value
        logger.info(f"Strategy updated to: {value.value}")
    
    @property
    def window_size(self) -> float:
        return self.config.window_size
    
    @window_size.setter
    def window_size(self, value: float) -> None:
        self.config.window_size = value
        logger.debug(f"Window size updated to: {value}s")
    
    @property
    def endpoint_limits(self) -> Dict[str, float]:
        return self.config.endpoint_limits
    
    @endpoint_limits.setter
    def endpoint_limits(self, value: Dict[str, float]) -> None:
        self.config.endpoint_limits = value
        logger.debug(f"Endpoint limits updated: {value}")
        
    def acquire(self, endpoint: Optional[str] = None) -> None:
        """Acquire permission to make a request, waiting if necessary.
        
        Args:
            endpoint: Optional API endpoint being accessed, for endpoint-specific rate limiting
        """
        with self._lock:
            try:
                if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
                    self._acquire_token_bucket(endpoint)
                elif self.strategy == RateLimitStrategy.FIXED_WINDOW:
                    self._acquire_fixed_window(endpoint)
                elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
                    self._acquire_sliding_window(endpoint)
                else:
                    logger.warning(f"Unknown rate limiting strategy: {self.strategy}. Using token bucket.")
                    self._acquire_token_bucket(endpoint)
                
                # Track request for metrics
                self.request_count += 1
                if endpoint:
                    self.endpoint_counts[endpoint] = self.endpoint_counts.get(endpoint, 0) + 1
            except Exception as e:
                logger.error(f"Error during rate limiting: {e}")
                # Still allow the request to proceed in case of internal rate limiter errors
                # This prevents the rate limiter from blocking legitimate requests due to bugs
                if endpoint:
                    self.endpoint_counts[endpoint] = self.endpoint_counts.get(endpoint, 0) + 1
    
    def _acquire_token_bucket(self, endpoint: Optional[str] = None) -> None:
        """Token bucket algorithm implementation with adaptive rate limiting based on API headers."""
        # Get endpoint-specific rate if available
        rate = self.endpoint_limits.get(endpoint, self.rate) if endpoint else self.rate
        
        # Check if we should use adaptive rate limiting based on headers
        if self.config.adaptive and self.burst_remaining == 0 and self.burst_reset > 0:
            # We've hit the burst limit according to API headers
            wait_time = self.burst_reset + self._add_jitter(self.burst_reset)
            logger.warning(f"Burst limit reached. Slowing down for {wait_time} seconds.")
            time.sleep(wait_time)
            
            # After waiting for the burst reset, adjust our rate to be more conservative
            adjusted_rate = rate * 0.8  # 20% more conservative
            adjusted_tokens = max(1, int(self.max_tokens * 0.5))  # 50% of max tokens
            logger.info(f"Rate limiter adjusted: rate={adjusted_rate}/s, max_tokens={adjusted_tokens}")
            
            # Apply a short wait to relieve pressure
            relief_wait = self.config.pressure_relief_wait + self._add_jitter(self.config.pressure_relief_wait)
            logger.info(f"Short wait of {relief_wait} seconds to relieve pressure...")
            time.sleep(relief_wait)
            
            # Reset tokens to allow one request
            self.tokens = 1
            self.last_update = time.monotonic()
            return
        
        # Standard token bucket algorithm
        while self.tokens <= 0:
            # Calculate how long to wait for at least 1 token
            now = time.monotonic()
            time_passed = now - self.last_update
            self.tokens = min(
                self.max_tokens,
                self.tokens + time_passed * rate
            )
            self.last_update = now
            
            if self.tokens <= 0:
                # Wait for approximately 1 token to be available
                wait_time = max(MIN_WAIT_TIME, 1.0 / rate)
                wait_time += self._add_jitter(wait_time)  # Add jitter to prevent thundering herd
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s for token")
                time.sleep(wait_time)
        
        self.tokens -= 1
        self.last_update = time.monotonic()
    
    def _acquire_fixed_window(self, endpoint: Optional[str] = None) -> None:
        """Fixed window rate limiting implementation."""
        now = time.monotonic()
        window_start = now - self.window_size
        key = endpoint or "global"
        
        # Initialize or clean up old timestamps
        if key not in self.request_timestamps:
            self.request_timestamps[key] = deque()
        
        # Remove timestamps outside the current window
        while self.request_timestamps[key] and self.request_timestamps[key][0] <= window_start:
            self.request_timestamps[key].popleft()
        
        # Get endpoint-specific rate if available
        rate = self.endpoint_limits.get(endpoint, self.rate) if endpoint else self.rate
        max_requests = int(rate * self.window_size)
        
        # Check if we've exceeded the rate limit
        while len(self.request_timestamps[key]) >= max_requests:
            # Calculate time until a slot opens up in the next window
            wait_time = max(MIN_WAIT_TIME, self.window_size - (now - window_start))
            logger.debug(f"Fixed window rate limit reached for {key}, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            
            # Update time references
            now = time.monotonic()
            window_start = now - self.window_size
            
            # Clean up timestamps again
            while self.request_timestamps[key] and self.request_timestamps[key][0] <= window_start:
                self.request_timestamps[key].popleft()
        
        # Record this request
        self.request_timestamps[key].append(now)
    
    def _acquire_sliding_window(self, endpoint: Optional[str] = None) -> None:
        """Sliding window rate limiting implementation."""
        now = time.monotonic()
        key = endpoint or "global"
        
        # Initialize or clean up old timestamps
        if key not in self.request_timestamps:
            self.request_timestamps[key] = deque()
        
        # Remove timestamps outside the current window
        window_start = now - self.window_size
        while self.request_timestamps[key] and self.request_timestamps[key][0] <= window_start:
            self.request_timestamps[key].popleft()
        
        # Get endpoint-specific rate if available
        rate = self.endpoint_limits.get(endpoint, self.rate) if endpoint else self.rate
        max_requests = int(rate * self.window_size)
        
        # Check if we've exceeded the rate limit
        while len(self.request_timestamps[key]) >= max_requests:
            if not self.request_timestamps[key]:
                break
                
            # Calculate time until oldest request expires from window
            oldest = self.request_timestamps[key][0]  # First item in deque is the oldest
            wait_time = max(MIN_WAIT_TIME, oldest + self.window_size - now)
            logger.debug(f"Sliding window rate limit reached for {key}, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            
            # Update time and clean up expired timestamps
            now = time.monotonic()
            window_start = now - self.window_size
            while self.request_timestamps[key] and self.request_timestamps[key][0] <= window_start:
                self.request_timestamps[key].popleft()
        
        # Record this request
        self.request_timestamps[key].append(now)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get rate limiting metrics for monitoring."""
        metrics = {
            "strategy": self.strategy.value,
            "rate": self.rate,
            "max_tokens": self.max_tokens,
            "window_size": self.window_size,
            "total_requests": self.request_count,
            "endpoint_counts": self.endpoint_counts.copy(),
        }
        
        # Add strategy-specific metrics
        if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            metrics["current_tokens"] = self.tokens
        elif self.strategy in (RateLimitStrategy.FIXED_WINDOW, RateLimitStrategy.SLIDING_WINDOW):
            window_stats = {}
            for key, timestamps in self.request_timestamps.items():
                window_stats[key] = len(timestamps)
            metrics["window_stats"] = window_stats
            
        return metrics
    
    def with_rate_limit(self, func: Callable, endpoint: Optional[str] = None, *args, **kwargs) -> Any:
        """Decorator-like method to execute a function with rate limiting.
        
        Args:
            func: Function to execute
            endpoint: Optional endpoint identifier for endpoint-specific rate limiting
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The result of the function call
        """
        self.acquire(endpoint)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing rate-limited function: {e}")
            raise
            
    def update_configuration(self, config: RateLimitConfig) -> None:
        """Update the rate limiter configuration.
        
        Args:
            config: New configuration to apply
        """
        self.config = config
        logger.info(f"Rate limiter configuration updated: strategy={config.strategy.value}, "
                   f"rate={config.rate}/s, max_tokens={config.max_tokens}")
                   
    def update_from_headers(self, headers: Dict[str, str]) -> None:
        """Update rate limiter state based on API response headers.
        
        Args:
            headers: API response headers containing rate limit information
        """
        if not self.config.adaptive or not headers:
            return
            
        try:
            # Parse burst limit headers
            if HEADER_BURST_LIMIT in headers and HEADER_BURST_REMAINING in headers and HEADER_BURST_RESET in headers:
                self.burst_limit = int(headers[HEADER_BURST_LIMIT])
                self.burst_remaining = int(headers[HEADER_BURST_REMAINING])
                self.burst_reset = int(headers[HEADER_BURST_RESET])
                
                # Log warning if burst limit is reached
                if self.burst_remaining == 0:
                    logger.warning(f"Rate limit exceeded. Headers:\n{self._format_headers(headers)}")
            
            # Parse global limit headers
            if HEADER_LIMIT in headers and HEADER_REMAINING in headers:
                self.global_limit = int(headers[HEADER_LIMIT])
                self.global_remaining = int(headers[HEADER_REMAINING])
                if HEADER_RESET in headers:
                    self.global_reset = int(headers[HEADER_RESET])
                
            # Update timestamp
            self.last_header_update = time.monotonic()
            
            # Adjust rate and tokens based on headers if burst limit is reached
            if self.burst_remaining == 0 and self.burst_reset > 0:
                # Calculate a more conservative rate based on remaining global limit
                if self.global_limit > 0 and self.global_remaining > 0:
                    # Use remaining capacity as a percentage of total
                    remaining_ratio = self.global_remaining / self.global_limit
                    # Adjust rate to be more conservative when approaching limits
                    new_rate = self.rate * max(0.1, remaining_ratio)
                    new_max_tokens = max(1, int(self.max_tokens * remaining_ratio))
                    
                    logger.info(f"Rate limiter adjusted: rate={new_rate:.6f}/s, max_tokens={new_max_tokens}")
                    
                    # Update configuration with new values
                    self.rate = new_rate
                    self.max_tokens = new_max_tokens
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing rate limit headers: {e}")
    
    def _format_headers(self, headers: Dict[str, str]) -> str:
        """Format headers for logging.
        
        Args:
            headers: Headers dictionary
            
        Returns:
            Formatted string of headers
        """
        return '\n'.join([f"{k}: {v}" for k, v in headers.items() 
                          if k.startswith('x-rate-limit')])
    
    def _add_jitter(self, value: float) -> float:
        """Add jitter to a value to prevent thundering herd problems.
        
        Args:
            value: Base value to add jitter to
            
        Returns:
            Value with jitter added
        """
        if self.config.jitter_factor <= 0:
            return 0
        
        jitter_amount = value * self.config.jitter_factor
        return random.uniform(0, jitter_amount)
