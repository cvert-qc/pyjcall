from setuptools import setup, find_packages

setup(
    name="pyjcall",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "black",
            "isort",
            "mypy",
        ],
    },
    python_requires=">=3.8",
    author="Maxime Nicol",
    author_email="nicol.maxime@gmail.com",
    description="Async Python SDK for JustCall API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/maximenicol/pyjcall",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 