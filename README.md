# PyJCall

[![PyPI version](https://badge.fury.io/py/pyjcall.svg)](https://badge.fury.io/py/pyjcall)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An asynchronous Python SDK for the [JustCall API](https://developer.justcall.io/docs/overview).

## Features

- Fully asynchronous API client using `aiohttp`
- Comprehensive type hints and Pydantic models
- Automatic rate limiting
- Detailed error handling
- Extensive test coverage

## Installation

```bash
pip install pyjcall
```

## Quick Start

```python
import asyncio
import os
from pyjcall import JustCallClient

async def main():
    # Initialize the client with your API credentials
    async with JustCallClient(
        api_key=os.environ["JUSTCALL_API_KEY"],
        api_secret=os.environ["JUSTCALL_API_SECRET"]
    ) as client:
        # List recent calls
        calls = await client.Calls.list(per_page=10)
        print(f"Retrieved {len(calls['data'])} calls")
        
        # List SMS messages
        messages = await client.Messages.list(per_page=10)
        print(f"Retrieved {len(messages['data'])} messages")

if __name__ == "__main__":
    asyncio.run(main())
```

## Supported Endpoints

* Calls

* Messages (SMS)

* Phone Numbers

* Users

## Error Handling

The SDK provides detailed error handling through the `JustCallException` class:

```python
from pyjcall.utils.exceptions import JustCallException

try:
    call = await client.Calls.get(call_id=999999)
except JustCallException as e:
    print(f"Error {e.status_code}: {e.message}")
```

## Example Script

The repository includes a comprehensive example script (`example.py`) that demonstrates all available endpoints:

```bash
# Set your API credentials in a .env file or environment variables
export JUSTCALL_API_KEY=your_api_key
export JUSTCALL_API_SECRET=your_api_secret

# Run the example script
python example.py
```

## Roadmap

- Support for JustCall Dialer endpoints
- Support for JustCall AI endpoints
- Webhook handling utilities
- Additional convenience methods

## Authentication

This SDK requires JustCall API credentials (API key and API secret). For details on obtaining these credentials and understanding the authentication process, please refer to the [JustCall API documentation](https://developer.justcall.io/docs/overview).

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Disclaimer

This SDK is not affiliated with JustCall. It is a community-driven project.

Generative AI was used to create this SDK and Documentation.