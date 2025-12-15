"""
BKW Email Automation - Main Package

This package handles email processing, data transformation, and delivery
for BKW Excel files received via Rotoforst email.
"""

__version__ = "0.1.0"
__author__ = "BKW Team"

from .config import settings
from .transformers import DataTransformer
from .sharepoint_client import SharePointClient

__all__ = [
    'settings',
    'DataTransformer',
    'SharePointClient',
]
