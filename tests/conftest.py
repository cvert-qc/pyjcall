import dotenv
import pytest
import os
from pyjcall import JustCallClient
from aioresponses import aioresponses

p = os.path.join(os.path.dirname(__file__), '../../')
dotenv.load_dotenv(p)
# print root directory
print("root env", p);
# print the env variables
print(os.environ)

# Set this to True to run integration tests
RUN_INTEGRATION_TESTS = os.environ.get("RUN_INTEGRATION_TESTS", "").lower() == "true"

@pytest.fixture
async def client(request):
    """Return a test client for unit tests, or a real client for integration tests."""
    if request.node.get_closest_marker('integration'):
        if not RUN_INTEGRATION_TESTS:
            pytest.skip("Integration tests are disabled. Set RUN_INTEGRATION_TESTS=true to enable.")
        
        api_key = os.getenv("JUSTCALL_API_KEY")
        api_secret = os.getenv("JUSTCALL_API_SECRET")
        if not api_key or not api_secret:
            pytest.skip("API credentials not found in environment")
        
        return JustCallClient(api_key=api_key, api_secret=api_secret)
    else:
        # Use test credentials for unit tests
        return JustCallClient(api_key="test_key", api_secret="test_secret")

@pytest.fixture
def mock_api():
    with aioresponses() as m:
        yield m
