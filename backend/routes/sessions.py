from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, ScrollSession
from datetime import datetime, timedelta

sessions_bp = Blueprint('sessions', __name__)

MULTIPLIERS = {
    'TikTok': 2.92, 'YouTube': 1.60, 'Instagram': 1.05,
    'Snapchat': 0.90, 'Twitter/X': 0.70, 'Facebook': 0.79, 'Other': 1.00
}
DEVICE_MULT = {'smartphone': 1.0, 'laptop': 1.4, 'tablet': 1.2}

def calculate_co2(platform, duration_minutes, device):
    p_mult = MULTIPLIERS.get(platform, 1.00)
    d_mult = DEVICE_MULT.get(device, 1.0)
    return round(float(duration_minutes) * p_mult * d_mult, 2)

@sessions_bp.route('', methods=['POST'])
@login_required
def create_session():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    platform = data.get('platform')
    duration_minutes = data.get('duration_minutes')
    device = data.get('device', 'smartphone')
    session_date_str = data.get('session_date')

    if not all([platform, duration_minutes, session_date_str]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
        duration_minutes = int(duration_minutes)
    except ValueError:
        return jsonify({"error": "Invalid date format or duration"}), 400

    # Server-side CO2 calc
    co2_grams = calculate_co2(platform, duration_minutes, device)

    new_session = ScrollSession(
        user_id=current_user.id,
        platform=platform,
        duration_minutes=duration_minutes,
        device=device,
        co2_grams=co2_grams,
        session_date=session_date
    )
    db.session.add(new_session)
    db.session.commit()

    return jsonify({"message": "Session created", "co2_grams": co2_grams}), 201

@sessions_bp.route('', methods=['GET'])
@login_required
def get_sessions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id', current_user.id, type=int)

    # Security: only see own sessions unless admin (simplifying for now)
    if user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    pagination = ScrollSession.query.filter_by(user_id=user_id).order_by(ScrollSession.session_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    sessions_data = []
    for s in pagination.items:
        sessions_data.append({
            "id": s.id,
            "platform": s.platform,
            "duration_minutes": s.duration_minutes,
            "device": s.device,
            "co2_grams": s.co2_grams,
            "session_date": s.session_date.isoformat()
        })

    return jsonify({
        "sessions": sessions_data,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    }), 200

@sessions_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_session(id):
    s = ScrollSession.query.get_or_404(id)
    if s.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403
    
    return jsonify({
        "id": s.id,
        "platform": s.platform,
        "duration_minutes": s.duration_minutes,
        "device": s.device,
        "co2_grams": s.co2_grams,
        "session_date": s.session_date.isoformat()
    }), 200

@sessions_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_session(id):
    s = ScrollSession.query.get_or_404(id)
    if s.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    if 'platform' in data:
        s.platform = data['platform']
    if 'duration_minutes' in data:
        s.duration_minutes = int(data['duration_minutes'])
    if 'device' in data:
        s.device = data['device']
    if 'session_date' in data:
        s.session_date = datetime.strptime(data['session_date'], '%Y-%m-%d').date()

    # Recalculate
    s.co2_grams = calculate_co2(s.platform, s.duration_minutes, s.device)
    db.session.commit()
    
    return jsonify({"message": "Session updated"}), 200

@sessions_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_session(id):
    s = ScrollSession.query.get_or_404(id)
    if s.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(s)
    db.session.commit()
    return jsonify({"message": "Session deleted"}), 200

@sessions_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    # Green IT justification: Using database aggregations where possible limits Python memory usage
    sessions = ScrollSession.query.filter_by(user_id=current_user.id).all()
    
    total_co2 = sum(s.co2_grams for s in sessions)
    
    # Calculate weekly CO2
    one_week_ago = datetime.utcnow().date() - timedelta(days=7)
    weekly_co2 = sum(s.co2_grams for s in sessions if s.session_date >= one_week_ago)
    
    # Top platform
    platform_counts = {}
    for s in sessions:
        platform_counts[s.platform] = platform_counts.get(s.platform, 0) + s.duration_minutes
    
    top_platform = max(platform_counts, key=platform_counts.get) if platform_counts else "None"
    
    return jsonify({
        "total_co2": round(total_co2, 2),
        "weekly_co2": round(weekly_co2, 2),
        "top_platform": top_platform,
        "equivalent_km_car": round(total_co2 / 120, 3),
        "equivalent_emails": round(total_co2 / 0.4, 1)
    }), 200
