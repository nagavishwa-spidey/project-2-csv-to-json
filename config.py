"""
Configuration management for Cloud CSV to JSON Converter.
Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    PORT = int(os.environ.get('PORT', 5000))

    # File upload settings
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 5242880))  # 5MB default
    ALLOWED_EXTENSIONS = {'csv', 'tsv', 'txt'}

    # CSV defaults
    DEFAULT_DELIMITER = os.environ.get('DEFAULT_DELIMITER', ',')

    # Supported output formats
    SUPPORTED_FORMATS = {'array_of_objects', 'array_of_arrays', 'nested_json'}

    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
