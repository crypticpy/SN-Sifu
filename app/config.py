"""
config.py

This module defines the configuration settings for the KB Article and Ticket Processing System.
It uses environment variables for sensitive information and provides default values where appropriate.

Author: Principal Python Engineer
Date: 2024-07-14
"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    # Cosmos DB settings
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY")
    COSMOS_DATABASE: str = os.getenv("COSMOS_DATABASE", "KBArticlesDB")
    COSMOS_CONTAINER: str = os.getenv("COSMOS_CONTAINER", "ArticlesAndTickets")

    # OpenAI API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # File upload settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", 5 * 1024 * 1024))  # 5 MB default
    ALLOWED_EXTENSIONS: set = {".csv", ".xlsx"}

    # Processing settings
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 100))

    def __post_init__(self):
        """Validate the configuration after initialization."""
        if not self.COSMOS_ENDPOINT or not self.COSMOS_KEY:
            raise ValueError("Cosmos DB endpoint and key must be provided.")
        if not self.OPENAI_API_KEY:
            raise ValueError("OpenAI API key must be provided.")

    @classmethod
    def from_env(cls):
        """Create a Config instance from environment variables."""
        return cls()

# Usage
config = Config.from_env()