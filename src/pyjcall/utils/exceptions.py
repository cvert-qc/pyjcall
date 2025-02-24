class JustCallException(Exception):
    """Custom exception for JustCall API errors"""
    
    def __init__(self, status_code: int = None, message: str = None):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

