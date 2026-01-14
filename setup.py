"""Setup script for CollectiveBrain."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="collective-brain",
    version="1.0.0",
    author="CollectiveBrain Contributors",
    description="Decentralized multi-agent collective brain system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mega-Therion/CollectiveBrain_V1",
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    py_modules=[
        "collective_brain",
        "orchestrator",
        "worker_pool",
        "memory_layer",
        "consensus_engine",
        "supervisor",
        "api",
        "config",
        "logger",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dateutil>=2.8.2",
        "requests>=2.31.0",
        "httpx>=0.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=24.1.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "isort>=5.13.2",
        ],
        "full": [
            "redis>=5.0.1",
            "pymilvus>=2.3.4",
            "neo4j>=5.16.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "collective-brain=collective_brain:main",
            "collective-brain-api=api:main",
        ],
    },
)
