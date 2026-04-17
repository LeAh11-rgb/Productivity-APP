# Handles: /api/auth/signup, /api/auth/login, /api/auth/logout, /api/auth/me

import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from app import models

auth_bp = Blueprint('auth', __name__)


def validate_signup_input(data): 
    errors = []

    if not data.get('email') or '@' not in data['email']:
        errors.append('A valid email address is required.')

    if not data.get('username') or len(data['username'].strip()) < 2:
        errors.append('Username must be at least 2 characters.')

    if not data.get('password') or len(data['password']) < 8:
        errors.append('Password must be at least 8 characters.')

    return errors

 
@auth_bp.route('/signup', methods=['POST'])
def signup(): 
    data = request.get_json()
 
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400
 
    errors = validate_signup_input(data)
    if errors: 
        return jsonify({'error': errors[0], 'errors': errors}), 400
 
    hashed_password = bcrypt.hashpw(
        data['password'].encode('utf-8'),    
        bcrypt.gensalt()                     
    ).decode('utf-8')
 
    user_id = models.create_user(
        email=data['email'],
        username=data['username'],
        hashed_password=hashed_password
    )

    if user_id is None: 
        return jsonify({'error': 'An account with this email already exists.'}), 409
 
    models.seed_default_categories(user_id)
 
    access_token = create_access_token(identity=str(user_id))
 
    user = models.get_user_by_id(user_id)

    return jsonify({
        'message': 'Account created successfully.',
        'user': user,
        'access_token': access_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login(): 
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
 
    user = models.get_user_by_email(email)
 
    invalid_msg = 'Invalid email or password.'

    if not user:
        return jsonify({'error': invalid_msg}), 401
 
    password_matches = bcrypt.checkpw(
        password.encode('utf-8'),
        user['password'].encode('utf-8')
    )

    if not password_matches:
        return jsonify({'error': invalid_msg}), 401
 
    access_token = create_access_token(identity=str(user['id']))
 
    safe_user = {
        'id': user['id'],
        'email': user['email'],
        'username': user['username'],
        'created_at': user['created_at']
    }

    return jsonify({
        'message': f"Welcome back, {user['username']}!",
        'user': safe_user,
        'access_token': access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout(): 
    return jsonify({'message': 'Logged out successfully.'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me(): 
    user_id = int(get_jwt_identity())
    user = models.get_user_by_id(user_id)

    if not user:
        return jsonify({'error': 'User not found.'}), 404

    return jsonify({'user': user}), 200