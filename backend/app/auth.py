# Add placeholder blueprint files for now so the app doesn't crash when we first import
# Handles: /api/auth/signup, /api/auth/login, /api/auth/logout, /api/auth/me

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)