from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from core.exceptions import SearchError, RateLimitError
from core.config import settings


class GoogleSearchTool:
    """
    A tool for performing Google searches using the Custom Search JSON API.
    """

    def __init__(self):
        """Initializes the Google Search tool."""
        try:
            self.service = build(
                "customsearch",
                "v1",
                developerKey=settings.GOOGLE_API_KEY
            )
            # Verify credentials with a test query
            self.service.cse().list(
                q="test",
                cx=settings.GOOGLE_CSE_ID.strip(),
                num=1
            ).execute()
        except Exception as e:
            raise SearchError(f"Failed to initialize Google Search: {str(e)}")

        self.last_request_time = datetime.now(timezone.utc).timestamp()
        self.requests_this_minute = 0
        self.daily_requests = 0

    async def _rate_limit(self):
        """Handles rate limiting for the Google Custom Search API."""
        current_time = datetime.now(timezone.utc).timestamp()

        # Reset daily counter at midnight UTC
        if datetime.now(timezone.utc).date() > datetime.fromtimestamp(
            self.last_request_time, timezone.utc
        ).date():
            self.daily_requests = 0

        # Per-minute rate limiting
        if current_time - self.last_request_time >= 60:
            self.requests_this_minute = 0
            self.last_request_time = current_time

        if self.requests_this_minute >= settings.RATE_LIMIT_PER_MIN:
            await asyncio.sleep(2)  # Pause for 2 seconds if rate limit is hit
            self.requests_this_minute = 0

        if self.daily_requests >= settings.GOOGLE_SEARCH_QUOTA_PER_DAY:
            raise RateLimitError("Daily search quota exceeded")

        self.requests_this_minute += 1
        self.daily_requests += 1

    async def search(self, query: str, time_range: Optional[str] = None) -> List[Dict]:
        """
        Performs a Google search.

        Args:
            query: The search query.
            time_range: Optional time restriction for the search (e.g., 'd1', 'w1', 'm1').

        Returns:
            A list of dictionaries, each containing the title, link, snippet, and date of a search result.

        Raises:
            SearchError: If there is an error during the search.
            RateLimitError: If the daily search quota is exceeded.
        """
        try:
            await self._rate_limit()

            # Execute the search
            result = self.service.cse().list(
                q=query,
                cx=settings.GOOGLE_CSE_ID,
                dateRestrict=time_range,
                num=10  # Number of results to retrieve
            ).execute()

            # Format the results
            formatted_results = []
            for item in result.get('items', []):
                formatted_results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'date': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time')
                    # Use current time if date is not found
                    or datetime.now(timezone.utc).isoformat()
                })

            return formatted_results

        except HttpError as e:
            raise SearchError(f"Google Search API error: {str(e)}")
        except Exception as e:
            raise SearchError(f"Unexpected error: {str(e)}")
