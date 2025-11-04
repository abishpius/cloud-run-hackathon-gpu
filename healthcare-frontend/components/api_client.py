"""
API Client for Healthcare Assistant Backend
"""
import requests
from typing import Dict, Any, Optional, Generator
import json
import time
from config.settings import settings


class HealthcareAPIClient:
    """Client for interacting with Healthcare Assistant backend API"""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client

        Args:
            base_url: Base URL for the backend API (defaults to settings)
        """
        self.base_url = (base_url or settings.BACKEND_API_URL).rstrip("/")
        self.timeout = settings.API_TIMEOUT
        self.session = requests.Session()

    def _get_url(self, endpoint: str) -> str:
        """Get full URL for an endpoint"""
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def health_check(self) -> bool:
        """
        Check if backend API is healthy

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self.session.get(
                self._get_url("/health"),
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    def create_session(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new session with the backend

        Args:
            user_id: Optional user ID (auto-generated if not provided)
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            Dict with user_id, session_id, and message

        Raises:
            requests.exceptions.RequestException: If API call fails
        """
        try:
            response = self.session.post(
                self._get_url("/api/v1/session/new"),
                json={
                    "user_id": user_id,
                    "session_id": session_id
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating session: {e}")
            raise

    def send_message(
        self,
        user_id: str,
        session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a message to the healthcare assistant

        Args:
            user_id: User ID
            session_id: Session ID
            message: User message text

        Returns:
            Dict with user_id, session_id, response, and optional metadata

        Raises:
            requests.exceptions.RequestException: If API call fails
        """
        try:
            response = self.session.post(
                self._get_url("/api/v1/chat"),
                json={
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": message
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {
                "user_id": user_id,
                "session_id": session_id,
                "response": "⚠️ The request timed out. The agent may be processing a complex query. Please try again.",
                "error": "timeout"
            }
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
            return {
                "user_id": user_id,
                "session_id": session_id,
                "response": f"❌ Error communicating with the healthcare assistant: {str(e)}",
                "error": str(e)
            }

    def send_message_stream(
        self,
        user_id: str,
        session_id: str,
        message: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Send a message and stream the response events

        Args:
            user_id: User ID
            session_id: Session ID
            message: User message text

        Yields:
            Event dictionaries as they are received

        Raises:
            requests.exceptions.RequestException: If API call fails
        """
        try:
            response = self.session.post(
                self._get_url("/api/v1/chat/stream"),
                json={
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": message
                },
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse SSE stream
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        try:
                            event_data = json.loads(data_str)
                            yield event_data
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.RequestException as e:
            print(f"Error streaming message: {e}")
            yield {
                "type": "error",
                "content": f"Error: {str(e)}",
                "metadata": {"error": str(e)}
            }

    def get_session_state(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a session

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            Dict with session state or None if error

        Raises:
            requests.exceptions.RequestException: If API call fails
        """
        try:
            response = self.session.get(
                self._get_url("/api/v1/session/state"),
                params={
                    "user_id": user_id,
                    "session_id": session_id
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting session state: {e}")
            return None

    def delete_session(
        self,
        user_id: str,
        session_id: str
    ) -> bool:
        """
        Delete a session

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.delete(
                self._get_url("/api/v1/session"),
                params={
                    "user_id": user_id,
                    "session_id": session_id
                },
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting session: {e}")
            return False


# Singleton instance
api_client = HealthcareAPIClient()
