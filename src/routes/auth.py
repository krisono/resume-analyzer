"""
Authentication Routes for Phase 2
- User registration and login endpoints
- Token management and user profile
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any
import logging

# Import services and models
from ..services.auth_service import auth_service
from ..models.database import User, db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
        
        # Validate required fields
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        
        if not all([email, password, first_name, last_name]):
            return jsonify({"error": "Email, password, first_name, and last_name are required"}), 400
        
        # Validate email format
        if "@" not in email or "." not in email:
            return jsonify({"error": "Invalid email format"}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Validate password strength
        password_validation = auth_service.validate_password_strength(password)
        if not password_validation["is_valid"]:
            return jsonify({
                "error": "Password does not meet requirements",
                "password_requirements": password_validation
            }), 400
        
        # Hash password
        hashed_password = auth_service.hash_password(password)
        
        # Create new user
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate tokens
        tokens = auth_service.generate_tokens(new_user.id, new_user.email)
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "created_at": new_user.created_at.isoformat()
            },
            "tokens": tokens
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
        
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify password
        if not auth_service.verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Update last login
        user.update_last_login()
        db.session.commit()
        
        # Generate tokens
        tokens = auth_service.generate_tokens(user.id, user.email)
        
        # Create session record (optional, for tracking)
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        user_agent = request.headers.get('User-Agent', 'unknown')
        session_data = auth_service.create_user_session(user.id, ip_address, user_agent)
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "tokens": tokens,
            "session": session_data
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
        
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            return jsonify({"error": "Refresh token is required"}), 400
        
        # Refresh the token
        new_tokens = auth_service.refresh_access_token(refresh_token)
        if not new_tokens:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        
        return jsonify({
            "message": "Token refreshed successfully",
            "tokens": new_tokens
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({"error": "Token refresh failed"}), 500

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """User logout endpoint"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401
        
        token = auth_service.extract_token_from_header(auth_header)
        if not token:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Verify and revoke token
        if auth_service.revoke_token(token):
            logger.info("User logged out successfully")
            return jsonify({"message": "Logout successful"}), 200
        else:
            return jsonify({"error": "Invalid token"}), 401
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"error": "Logout failed"}), 500

@auth_bp.route("/profile", methods=["GET"])
def get_profile():
    """Get user profile information"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401
        
        token = auth_service.extract_token_from_header(auth_header)
        if not token:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Verify token
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Get user
        user = User.query.get(payload["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        return jsonify({"error": "Failed to fetch profile"}), 500

@auth_bp.route("/profile", methods=["PUT"])
def update_profile():
    """Update user profile information"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401
        
        token = auth_service.extract_token_from_header(auth_header)
        if not token:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Verify token
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Get user
        user = User.query.get(payload["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get update data
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
        
        # Update allowed fields
        if "first_name" in data:
            user.first_name = data["first_name"].strip()
        if "last_name" in data:
            user.last_name = data["last_name"].strip()
        
        # Handle password change
        if "new_password" in data:
            current_password = data.get("current_password")
            if not current_password:
                return jsonify({"error": "Current password required for password change"}), 400
            
            if not auth_service.verify_password(current_password, user.password_hash):
                return jsonify({"error": "Current password is incorrect"}), 401
            
            # Validate new password
            password_validation = auth_service.validate_password_strength(data["new_password"])
            if not password_validation["is_valid"]:
                return jsonify({
                    "error": "New password does not meet requirements",
                    "password_requirements": password_validation
                }), 400
            
            user.password_hash = auth_service.hash_password(data["new_password"])
        
        db.session.commit()
        
        logger.info(f"Profile updated for user: {user.email}")
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to update profile"}), 500

@auth_bp.route("/validate-token", methods=["POST"])
def validate_token():
    """Validate if a token is still valid"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401
        
        token = auth_service.extract_token_from_header(auth_header)
        if not token:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Verify token
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({"valid": False, "error": "Invalid or expired token"}), 401
        
        return jsonify({
            "valid": True,
            "user_id": payload["user_id"],
            "email": payload["email"],
            "expires_at": payload["exp"]
        }), 200
        
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return jsonify({"valid": False, "error": "Token validation failed"}), 500
