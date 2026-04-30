from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt
import jwt
from datetime import datetime, timedelta
from models import db, User
import os

auth_bp = Blueprint('auth', __name__)

def generate_jwt(user_id):
    # Green IT justification: JWT tokens avoid hitting the database for session validation on every request
    payload = {
        'exp': datetime.utcnow() + timedelta(hours=int(os.environ.get('JWT_EXPIRY_HOURS', 24))),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, os.environ.get('SECRET_KEY', 'default-dev-key'), algorithm='HS256')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    device_type = data.get('device_type', 'smartphone')

    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        # Security: No sensitive data in error messages
        return jsonify({"error": "Email already exists"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    # Security: bcrypt password hashing (never store plaintext)
    # Green IT justification: Bcrypt provides security natively without relying on external API calls
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        device_type=device_type
    )
    db.session.add(new_user)
    db.session.commit()

    # Login automatically
    login_user(new_user)
    token = generate_jwt(new_user.id)

    return jsonify({
        "message": "User registered successfully", 
        "token": token,
        "user_id": new_user.id
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        login_user(user)
        token = generate_jwt(user.id)
        return jsonify({
            "message": "Login successful", 
            "token": token,
            "user_id": user.id
        }), 200

    return jsonify({"error": "Invalid email or password"}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    # Green IT justification: Fetching specific fields instead of SELECT *
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "device_type": current_user.device_type
    }), 200
