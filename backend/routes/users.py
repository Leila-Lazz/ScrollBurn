from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, User

users_bp = Blueprint('users', __name__)

# Green IT justification: Pagination limits DB queries and JSON payload size
@users_bp.route('', methods=['GET'])
@login_required
def get_users():
    # Admin only check could go here, for simplicity assuming auth is enough or add admin flag
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Enforce max 20 per page
    if per_page > 20:
        per_page = 20

    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Green IT justification: specific columns selected by mapping
    users_data = []
    for user in pagination.items:
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "device_type": user.device_type,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })

    return jsonify({
        "users": users_data,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    }), 200

@users_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "device_type": user.device_type,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }), 200

@users_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'device_type' in data:
        user.device_type = data['device_type']
        
    db.session.commit()
    
    return jsonify({
        "message": "User updated",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "device_type": user.device_type
        }
    }), 200

@users_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200
