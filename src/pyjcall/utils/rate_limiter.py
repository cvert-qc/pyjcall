import asyncio
import time
from typing import Optional, Dict, List, Callable, Awaitable
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Enum for different rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"

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
        rate: float = 1.6,  # tokens/requests per second
        max_tokens: int = 5,  # maximum burst size
        strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET,
        window_size: float = 60.0,  # window size in seconds (for window-based strategies)
        endpoint_limits: Optional[Dict[str, float]] = None,  # endpoint-specific rate limits
    ):
        self.rate = rate
        self.max_tokens = max_tokens
        self.strategy = strategy
        self.window_size = window_size
        self.endpoint_limits = endpoint_limits or {}
        
        # Token bucket state
        self.tokens = max_tokens
        self.last_update = time.monotonic()
        
        # Window-based state
        self.request_timestamps: Dict[str, List[float]] = {}  # endpoint -> list of timestamps
        
        # Concurrency control
        self._lock = asyncio.Lock()
        
        # Request tracking
        self.request_count = 0
        self.endpoint_counts: Dict[str, int] = {}
        
        logger.info(f"Initialized RateLimiter with strategy: {strategy.value}, rate: {rate}/s")
        
    async def acquire(self, endpoint: Optional[str] = None) -> None:
        """Acquire permission to make a request, waiting if necessary.
        
        Args:
            endpoint: Optional API endpoint being accessed, for endpoint-specific rate limiting
        """
        async with self._lock:
            if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
                await self._acquire_token_bucket(endpoint)
            elif self.strategy == RateLimitStrategy.FIXED_WINDOW:
                await self._acquire_fixed_window(endpoint)
            elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
                await self._acquire_sliding_window(endpoint)
            
            # Track request for metrics
            self.request_count += 1
            if endpoint:
                self.endpoint_counts[endpoint] = self.endpoint_counts.get(endpoint, 0) + 1
    
    async def _acquire_token_bucket(self, endpoint: Optional[str] = None) -> None:
        """Token bucket algorithm implementation."""
        # Get endpoint-specific rate if available
        rate = self.endpoint_limits.get(endpoint, self.rate) if endpoint else self.rate
        
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
                wait_time = 1.0 / rate
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s for token")
                await asyncio.sleep(wait_time)
        
        self.tokens -= 1
        self.last_update = time.monotonic()
    
    async def _acquire_fixed_window(self, endpoint: Optional[str] = None) -> None:
        """Fixed window rate limiting implementation."""
        now = time.monotonic()
        window_start = now - self.window_size
        key = endpoint or "global"
        
        # Initialize or clean up old timestamps
        if key not in self.request_timestamps:
            self.request_timestamps[key] = []
        
        # Remove timestamps outside the current window
        self.request_timestamps[key] = [ts for ts in self.request_timestamps[key] if ts > window_start]
        
        # Get endpoint-specific rate if available
        rate = self.endpoint_limits.get(endpoint, self.rate) if endpoint else self.rate
        max_requests = int(rate * self.window_size)
        
        # Check if we've exceeded the rate limit
        while len(self.request_timestamps[key]) >= max_requests:
            # Calculate time until a slot opens up in the next window
            wait_time = self.window_size - (now - window_start)
            logger.debug(f"Fixed window rate limit reached for {key}, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            
            # Update time references
            now = time.monotonic()
            window_start = now - self.window_size
            
            # Clean up timestamps again
            self.request_timestamps[key] = [ts for ts in self.request_timestamps[key] if ts > window_start]
        
        # Record this request
        self.request_timestamps[key].append(now)
    
    async def _acquire_sliding_window(self, endpoint: Optional[str] = None) -> None:
        """Sliding window rate limiting implementation."""
        now = time.monotonic()
        key = endpoint or "global"
        
        # Initialize or clean up old timestamps
        if key not in self.request_timestamps:
            self.request_timestamps[key] = []
        
        # Remove timestamps outside the current window
        window_start = now - self.window_size
        self.request_timestamps[key] = [ts for ts in self.request_timestamps[key] if ts > window_start]
        
        # Get endpoint-specific rate if available
        rate = self.endpoint_limits.get(endpoint, self.rate) if endpoint else self.rate
        max_requests = int(rate * self.window_size)
        
        # Check if we've exceeded the rate limit
        while len(self.request_timestamps[key]) >= max_requests:
            if not self.request_timestamps[key]:
                break
                
            # Calculate time until oldest request expires from window
            oldest = min(self.request_timestamps[key])
            wait_time = max(0.1, oldest + self.window_size - now)
            logger.debug(f"Sliding window rate limit reached for {key}, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            
            # Update time and clean up expired timestamps
            now = time.monotonic()
            window_start = now - self.window_size
            self.request_timestamps[key] = [ts for ts in self.request_timestamps[key] if ts > window_start]
        
        # Record this request
        self.request_timestamps[key].append(now)
    
    def get_metrics(self) -> Dict[str, any]:
        """Get rate limiting metrics for monitoring."""
        return {
            "strategy": self.strategy.value,
            "rate": self.rate,
            "total_requests": self.request_count,
            "endpoint_counts": self.endpoint_counts.copy(),
        }
    
    async def with_rate_limit(self, func: Callable[..., Awaitable], endpoint: Optional[str] = None, *args, **kwargs):
        """Decorator-like method to execute a function with rate limiting.
        
        Args:
            func: Async function to execute
            endpoint: Optional endpoint identifier for endpoint-specific rate limiting
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The result of the function call
        """
        await self.acquire(endpoint)
        return await func(*args, **kwargs)
