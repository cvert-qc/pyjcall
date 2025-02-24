#!/bin/bash

# Create main directory structure
mkdir -p src/pyjcall/{models,resources,utils}
mkdir -p tests
mkdir -p docs
mkdir -p examples

# Move existing Python files to their new locations
mv client.py src/pyjcall/
mv models/*.py src/pyjcall/models/
mv resources/*.py src/pyjcall/resources/
mv utils/*.py src/pyjcall/utils/

# Move test file
mv test_calls.py tests/

# Create necessary __init__.py files
touch src/pyjcall/__init__.py
touch src/pyjcall/models/__init__.py
touch src/pyjcall/resources/__init__.py
touch src/pyjcall/utils/__init__.py
touch tests/__init__.py

# Create documentation files
echo "# PyJCall" > README.md
echo "# PyJCall Documentation" > docs/README.md
echo "# API Reference" > docs/API.md

# Create example file
cat > examples/basic_usage.py << 'EOF'
import asyncio
import os
from pyjcall import JustCallClient

async def main():
    async with JustCallClient(
        api_key=os.getenv("JUSTCALL_API_KEY"),
        api_secret=os.getenv("JUSTCALL_API_SECRET")
    ) as client:
        # List calls
        calls = await client.Calls.list(per_page=20)
        print(f"Retrieved {len(calls.get('data', []))} calls")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Create test configuration
cat > tests/conftest.py << 'EOF'
import pytest
import os
from pyjcall import JustCallClient

@pytest.fixture
async def client():
    api_key = os.getenv("JUSTCALL_API_KEY")
    api_secret = os.getenv("JUSTCALL_API_SECRET")
    async with JustCallClient(api_key=api_key, api_secret=api_secret) as client:
        yield client
EOF

# Create requirements files
cat > requirements-dev.txt << 'EOF'
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
EOF

# Create LICENSE file (MIT License)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Make the script executable
chmod +x setup_project.sh

echo "Project structure created successfully!" 