"""
ZoomInfo JWT Token Manager

Uses ZoomInfo's official PKI authentication library to generate JWT tokens.
Requires Username + Client ID + Private Key for authentication.

Based on ZoomInfo's official library:
https://github.com/Zoominfo/api-auth-python-client

Usage:
    from src.enrichment.zoominfo_jwt_manager import ZoomInfoJWTManager

    jwt_manager = ZoomInfoJWTManager()
    token = jwt_manager.get_token()  # Returns valid JWT token
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

# Optional dependency - install from: pip install git+https://github.com/Zoominfo/api-auth-python-client.git
try:
    import zi_api_auth_client
    ZOOMINFO_AVAILABLE = True
except ImportError:
    zi_api_auth_client = None
    ZOOMINFO_AVAILABLE = False

logger = logging.getLogger(__name__)


class ZoomInfoJWTManager:
    """Manage JWT token generation and renewal for ZoomInfo API using official client."""

    def __init__(self):
        """Initialize JWT manager with credentials from environment."""
        if not ZOOMINFO_AVAILABLE:
            raise ImportError(
                "ZoomInfo authentication library not installed. "
                "Install with: pip install git+https://github.com/Zoominfo/api-auth-python-client.git"
            )

        self.username = os.getenv('ZOOMINFO_USERNAME')
        self.client_id = os.getenv('ZOOMINFO_CLIENT_ID')
        private_key_file = os.getenv('ZOOMINFO_PRIVATE_KEY_FILE', '.zoominfo_private_key.pem')

        # Token cache
        self.cached_token = None
        self.token_expiry = None

        # Validate credentials
        if not self.username:
            raise ValueError("ZOOMINFO_USERNAME not found in environment")
        if not self.client_id:
            raise ValueError("ZOOMINFO_CLIENT_ID not found in environment")

        # Load private key from file
        try:
            self.private_key = self._load_private_key_from_file(private_key_file)
            logger.info(f"Loaded private key from: {private_key_file}")
            logger.info(f"Initialized ZoomInfo JWT Manager with Username: {self.username}, Client ID: {self.client_id[:8]}...")
        except Exception as e:
            logger.error(f"Failed to load private key: {e}")
            raise

    def _load_private_key_from_file(self, filepath: str) -> str:
        """
        Load private key from PEM file.

        Args:
            filepath: Path to private key PEM file

        Returns:
            Private key as string (PEM format)
        """
        key_path = Path(filepath)

        if not key_path.exists():
            raise FileNotFoundError(f"Private key file not found: {filepath}")

        # Read the key file as string (ZoomInfo library expects string)
        with open(key_path, 'r') as key_file:
            private_key = key_file.read()

        return private_key

    def _generate_token(self) -> str:
        """
        Generate a new JWT token using ZoomInfo's official PKI authentication.

        Token is valid for 1 hour as per ZoomInfo's specification.

        Returns:
            JWT token string
        """
        try:
            # Use ZoomInfo's official PKI authentication
            token = zi_api_auth_client.pki_authentication(
                self.username,
                self.client_id,
                self.private_key
            )

            logger.info(f"Generated new JWT token using ZoomInfo official client")

            return token

        except Exception as e:
            logger.error(f"Failed to generate JWT token: {e}", exc_info=True)
            raise

    def get_token(self) -> str:
        """
        Get valid JWT token (from cache or generate new).

        Returns:
            Valid JWT token string
        """
        # Check if we have a cached token that's still valid
        if self.cached_token and self.token_expiry:
            # Add 5 minute buffer before expiration
            if datetime.utcnow() < (self.token_expiry - timedelta(minutes=5)):
                logger.debug("Using cached JWT token")
                return self.cached_token
            else:
                logger.info("Cached JWT token expired, generating new one")

        # Generate new token
        self.cached_token = self._generate_token()
        self.token_expiry = datetime.utcnow() + timedelta(hours=1)

        return self.cached_token

    def invalidate_token(self):
        """Invalidate cached token (force regeneration on next request)."""
        self.cached_token = None
        self.token_expiry = None
        logger.info("JWT token cache invalidated")
