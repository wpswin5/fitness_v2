"""
Auth0 Token and User Context Models
"""
from pydantic import BaseModel
from typing import Optional, Any, Dict


class TokenPayload(BaseModel):
    """Claims extracted from Auth0 ID token or Access token"""
    sub: str  # Auth0 user ID
    aud: Optional[str] = None  # Audience (API identifier)
    iss: Optional[str] = None  # Issuer (Auth0 domain)
    exp: Optional[int] = None  # Expiration timestamp
    iat: Optional[int] = None  # Issued at timestamp
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    nickname: Optional[str] = None
    name: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional claims from Auth0


class UserContext(BaseModel):
    """User context extracted from authenticated request"""
    auth0_sub: str  # The 'sub' claim from Auth0 token
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    
    class Config:
        from_attributes = True


class JWKSPublicKey(BaseModel):
    """JWKS public key from Auth0"""
    kid: str
    kty: str
    use: Optional[str] = None
    n: str
    e: str
    alg: Optional[str] = None
    
    class Config:
        extra = "allow"


class JWKS(BaseModel):
    """JWKS response from Auth0"""
    keys: list[JWKSPublicKey]
