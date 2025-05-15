from setuptools import setup, find_packages
import os

# Read version from config.toml
with open("config.toml", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("version"):
            version = line.split("=")[1].strip().strip('"')
            break

setup(
    name="mar-disrupcion",
    version=version,
    description="MAR-DISRUPCION: Sistema Avanzado de Análisis de Seguridad y Finanzas",
    author="Felipe",
    packages=find_packages(exclude=["tests*", "backup_tests*"]),
    python_requires=">=3.9",
    install_requires=[
        # Core AI/ML
        "anthropic>=0.8.0",
        "openai>=1.12.0",
        "torch>=2.2.0",
        "tensorflow>=2.15.0",
        "transformers>=4.36.0",
        "langchain>=0.1.0",
        
        # Data Analysis
        "numpy>=1.26.4",
        "pandas>=2.2.1",
        "scipy>=1.11.0",
        "plotly>=5.19.0",
        
        # Security Tools
        "scapy>=2.5.0",
        "python-nmap>=0.7.1",
        "cryptography>=42.0.4",
        "pyOpenSSL>=23.0.0",
        "pycryptodome>=3.20.0",
        
        # API and Web
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "aiohttp>=3.9.3",
        "requests>=2.31.0",
        "streamlit>=1.32.0",
        
        # Database
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "psycopg2-binary>=2.9.9",
        
        # Utilities
        "python-dotenv>=1.0.0",
        "toml>=0.10.2",
        "pydantic>=2.6.0",
        
        # Monitoring and Logging
        "structlog>=24.1.0",
        "prometheus-client>=0.19.0",
        
        # Caching and Resilience
        "cachetools>=5.3.0",
        "tenacity>=8.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=24.1.0",
            "isort>=5.13.0",
            "mypy>=1.8.0",
            "pylint>=3.0.0"
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-system=AI1:main",
            "ai-webapp=app:main"
        ]
    }
)
