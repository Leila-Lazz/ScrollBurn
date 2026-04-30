from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, GreenChallenge
from datetime import datetime

challenges_bp = Blueprint('challenges', __name__)

@challenges_bp.route('', methods=['POST'])
@login_required
def create_challenge():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    title = data.get('title')
    platform = data.get('platform')
    daily_limit_minutes = data.get('daily_limit_minutes')
    duration_days = data.get('duration_days')

    if not all([title, daily_limit_minutes, duration_days]):
        return jsonify({"error": "Missing required fields"}), 400

    new_challenge = GreenChallenge(
        user_id=current_user.id,
        title=title,
        platform=platform,
        daily_limit_minutes=int(daily_limit_minutes),
        duration_days=int(duration_days),
        start_date=datetime.utcnow().date(),
        status='active'
    )
    db.session.add(new_challenge)
    db.session.commit()

    return jsonify({"message": "Challenge created"}), 201

@challenges_bp.route('', methods=['GET'])
@login_required
def get_challenges():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = GreenChallenge.query.filter_by(user_id=current_user.id).order_by(GreenChallenge.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    challenges_data = []
    for c in pagination.items:
        challenges_data.append({
            "id": c.id,
            "title": c.title,
            "platform": c.platform,
            "daily_limit_minutes": c.daily_limit_minutes,
            "duration_days": c.duration_days,
            "status": c.status,
            "co2_saved_grams": c.co2_saved_grams,
            "start_date": c.start_date.isoformat()
        })

    return jsonify({
        "challenges": challenges_data,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    }), 200

@challenges_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_challenge(id):
    c = GreenChallenge.query.get_or_404(id)
    if c.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403
    
    return jsonify({
        "id": c.id,
        "title": c.title,
        "platform": c.platform,
        "daily_limit_minutes": c.daily_limit_minutes,
        "duration_days": c.duration_days,
        "status": c.status,
        "co2_saved_grams": c.co2_saved_grams,
        "start_date": c.start_date.isoformat()
    }), 200

@challenges_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_challenge(id):
    c = GreenChallenge.query.get_or_404(id)
    if c.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    if 'title' in data:
        c.title = data['title']
    if 'daily_limit_minutes' in data:
        c.daily_limit_minutes = int(data['daily_limit_minutes'])
    if 'status' in data:
        c.status = data['status']
    if 'co2_saved_grams' in data:
        c.co2_saved_grams = float(data['co2_saved_grams'])

    db.session.commit()
    return jsonify({"message": "Challenge updated"}), 200

@challenges_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_challenge(id):
    c = GreenChallenge.query.get_or_404(id)
    if c.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Challenge deleted"}), 200
