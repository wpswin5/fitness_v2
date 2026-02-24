"""
Auth0 JWT Validation and Token Handling
"""
import json
import logging
from functools import lru_cache
from typing import Optional

import requests
from jose import JWTError, jwt
from jose.exceptions import JWTClaimsError
from datetime import datetime, timedelta

from src.config import settings
from src.auth.models import TokenPayload, JWKS

logger = logging.getLogger(__name__)


class Auth0Manager:
    """Manages Auth0 JWT validation and token operations"""
    
    def __init__(self):
        self.domain = settings.AUTH0_DOMAIN
        self.audience = settings.AUTH0_API_AUDIENCE or f"https://{self.domain}/api/v2/"
        self.issuer = f"https://{self.domain}/"
        self.jwks_client = None
    
    @lru_cache(maxsize=1)
    def get_jwks(self) -> JWKS:
        """Fetch and cache Auth0 JWKS (public keys) for token validation"""
        try:
            response = requests.get(f"{self.issuer}.well-known/jwks.json", timeout=5)
            response.raise_for_status()
            jwks_data = response.json()
            return JWKS(**jwks_data)
        except Exception as e:
            logger.error(f"Failed to fetch Auth0 JWKS: {str(e)}")
            raise
    
    def get_public_key(self, token: str) -> str:
        """Extract the public key from JWKS for the given token"""
        try:
            # Decode without verification to get the header
            unverified_header = jwt.get_unverified_header(token)
        except JWTError as e:
            logger.error(f"Failed to decode JWT header: {str(e)}")
            raise
        
        # Get JWKS and find matching key by kid
        jwks = self.get_jwks()
        kid = unverified_header.get("kid")
        
        if not kid:
            raise JWTError("Token does not contain 'kid' in header")
        
        for key in jwks.keys:
            if key.kid == kid:
                # Convert JWK to PEM format for verification
                return self._jwk_to_pem(key)
        
        raise JWTError(f"Unable to find matching key with kid: {kid}")
    
    @staticmethod
    def _jwk_to_pem(jwk) -> str:
        """Convert JWK to PEM format for PyJWT validation"""
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        import base64
        
        # Decode base64url encoded values
        def _decode_base64_url(data: str) -> bytes:
            # Add padding if necessary
            padding = 4 - len(data) % 4
            if padding != 4:
                data += '=' * padding
            return base64.urlsafe_b64decode(data)
        
        # Extract components
        n_bytes = _decode_base64_url(jwk.n)
        e_bytes = _decode_base64_url(jwk.e)
        
        # Convert to integers
        n = int.from_bytes(n_bytes, byteorder='big')
        e = int.from_bytes(e_bytes, byteorder='big')
        
        # Create RSA public key
        public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
        
        # Convert to PEM format
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    def verify_token(self, token: str) -> TokenPayload:
        """
        Verify Auth0 JWT token and extract claims
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            TokenPayload with verified claims
            
        Raises:
            JWTError: If token is invalid or verification fails
            JWTClaimsError: If token claims are invalid
        """
        try:
            # Get public key for this token
            public_key = self.get_public_key(token)
            
            # Decode without verification first to log claims for debugging
            unverified_payload = jwt.get_unverified_claims(token)
            logger.debug(f"Token claims (unverified): aud={unverified_payload.get('aud')}, iss={unverified_payload.get('iss')}, sub={unverified_payload.get('sub')}")
            logger.debug(f"Expected audience: {self.audience}, Expected issuer: {self.issuer}")
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
            
            # Extract and validate claims
            token_payload = TokenPayload(**payload)
            
            logger.info(f"Token verified for user: {token_payload.sub}")
            return token_payload
            
        except JWTClaimsError as e:
            logger.error(f"Token claims validation failed: {str(e)}")
            logger.error(f"Expected audience: {self.audience}, Expected issuer: {self.issuer}")
            raise
        except JWTError as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {str(e)}")
            raise
    
    def get_management_token(self) -> str:
        """
        Get Management API access token for Auth0 API calls
        (For user operations, etc.)
        """
        try:
            response = requests.post(
                f"{self.issuer}oauth/token",
                json={
                    "client_id": settings.AUTH0_CLIENT_ID_WEB,
                    "client_secret": settings.AUTH0_CLIENT_SECRET_WEB,
                    "audience": f"{self.issuer}api/v2/",
                    "grant_type": "client_credentials",
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            logger.error(f"Failed to get management token: {str(e)}")
            raise


# Singleton instance
auth0_manager = Auth0Manager()
