"""
Authentication Service for Phase 2
- User registration and login
- JWT token management
- Password hashing and validation
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import current_app
from typing import Dict, Optional, Any, List
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the auth service with Flask app"""
        app.config.setdefault('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    
    def hash_password(self, password: str) -> str:
        """Hash a password for storing in database"""
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def generate_tokens(self, user_id: int, email: str) -> Dict[str, str]:
        """Generate access and refresh tokens for a user"""
        try:
            # Token payload
            payload = {
                'user_id': user_id,
                'email': email,
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            # Access token (shorter expiry)
            access_payload = payload.copy()
            access_payload['exp'] = datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
            access_token = jwt.encode(
                access_payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            # Refresh token (longer expiry)
            refresh_payload = payload.copy()
            refresh_payload['type'] = 'refresh'
            refresh_payload['exp'] = datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
            refresh_token = jwt.encode(
                refresh_payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
            }
            
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            raise Exception("Failed to generate tokens")
    
    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Check token type
            if payload.get('type') != token_type:
                logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
                return None
            
            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                logger.warning("Token has expired")
                return None
            
            return {
                'user_id': payload['user_id'],
                'email': payload['email'],
                'iat': payload['iat'],
                'exp': payload['exp']
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generate new access token using refresh token"""
        # Verify refresh token
        payload = self.verify_token(refresh_token, token_type='refresh')
        if not payload:
            return None
        
        try:
            # Generate new access token
            new_access_payload = {
                'user_id': payload['user_id'],
                'email': payload['email'],
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
                'type': 'access'
            }
            
            new_access_token = jwt.encode(
                new_access_payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            return {
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
            }
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    def extract_token_from_header(self, auth_header: str) -> Optional[str]:
        """Extract token from Authorization header"""
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength and return requirements"""
        requirements = {
            'min_length': len(password) >= 8,
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(c in '!@#$%^&*(),.?":{}|<>' for c in password)
        }
        
        score = sum(requirements.values())
        is_strong = score >= 4 and requirements['min_length']
        
        return {
            'is_valid': is_strong,
            'score': score,
            'max_score': len(requirements),
            'requirements': requirements,
            'suggestions': self._get_password_suggestions(requirements)
        }
    
    def _get_password_suggestions(self, requirements: Dict[str, bool]) -> List[str]:
        """Get password improvement suggestions"""
        suggestions = []
        
        if not requirements['min_length']:
            suggestions.append("Use at least 8 characters")
        if not requirements['has_uppercase']:
            suggestions.append("Include at least one uppercase letter")
        if not requirements['has_lowercase']:
            suggestions.append("Include at least one lowercase letter")
        if not requirements['has_digit']:
            suggestions.append("Include at least one number")
        if not requirements['has_special']:
            suggestions.append("Include at least one special character (!@#$%^&*)")
        
        return suggestions
    
    def create_user_session(self, user_id: int, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Create a user session record"""
        return {
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'login_time': datetime.utcnow(),
            'is_active': True
        }
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token (for logout)"""
        # In a production system, you would maintain a blacklist
        # For now, we'll just verify the token is valid
        payload = self.verify_token(token)
        return payload is not None

# Global instance
auth_service = AuthService()
