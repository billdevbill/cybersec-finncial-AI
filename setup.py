from setuptools import setup, find_packages

setup(
    name="ai_system",
    version="0.1.0",
    description="Advanced AI System for Security and Financial Analysis",
    author="Felipe",
    packages=find_packages(exclude=["tests*", "backup_tests*"]),
    python_requires=">=3.9",
    install_requires=[
        "anthropic>=0.8.0",
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.31.0",
        "numpy>=1.24.0",
        "torch>=2.2.0",
        "scapy>=2.5.0",
        "python-nmap>=0.7.1",
        "plotly>=5.18.0",
        "pandas>=2.2.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.6.0",
        "cryptography>=42.0.0"
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
