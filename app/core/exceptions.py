from fastapi import HTTPException
from typing import Any, Dict, Optional


class CompetitiveResearchException(Exception):
    """Base exception for the competitive research application"""
    pass


class APIKeyError(CompetitiveResearchException):
    """Raised when there are issues with API keys"""
    pass


class SearchError(CompetitiveResearchException):
    """Raised when search operations fail"""
    pass


class RateLimitError(CompetitiveResearchException):
    """Raised when rate limits are exceeded"""
    pass


class ModelProcessingError(CompetitiveResearchException):
    """Raised when AI model processing fails"""
    pass
