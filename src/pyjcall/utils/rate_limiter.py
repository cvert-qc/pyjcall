import asyncio
import time
from typing import Optional

class RateLimiter:
    """Token bucket rate limiter implementation.
    
    Default settings:
    - 60 requests per minute (1 request per second)
    - Burst of up to 5 requests
    """
    
    def __init__(
        self,
        rate: float = 1,  # tokens per second
        max_tokens: int = 5,  # maximum burst size
    ):
        self.rate = rate
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
        
    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            while self.tokens <= 0:
                # Calculate how long to wait for at least 1 token
                now = time.monotonic()
                time_passed = now - self.last_update
                self.tokens = min(
                    self.max_tokens,
                    self.tokens + time_passed * self.rate
                )
                self.last_update = now
                
                if self.tokens <= 0:
                    # Wait for approximately 1 token to be available
                    wait_time = 1.0 / self.rate
                    await asyncio.sleep(wait_time)
            
            self.tokens -= 1
