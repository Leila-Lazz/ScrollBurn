import os
from flask import Flask, request, jsonify
from flask_login import LoginManager
from dotenv import load_dotenv
from models import db, User

# Load environment variables
# Green IT justification: Using python-dotenv to avoid hardcoding secrets, ensuring security without extra bloat.
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
database_url = os.environ.get('DATABASE_URL', 'sqlite:///../scrollburn.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
# Redirect to login page for unauthorized access (implemented in frontend, but here API returns 401)
login_manager.login_view = None

@login_manager.user_loader
def load_user(user_id):
    # Green IT justification: Querying by ID natively uses an index, ensuring fast O(1) lookup.
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized"}), 401

# Register blueprints (to be created)
from auth import auth_bp
from routes.users import users_bp
from routes.sessions import sessions_bp
from routes.challenges import challenges_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(sessions_bp, url_prefix='/sessions')
app.register_blueprint(challenges_bp, url_prefix='/challenges')

# Carbon Mirror - Public Endpoint
@app.route('/calculator/estimate', methods=['POST'])
def estimate_carbon():
    # Green IT justification: No DB write means zero disk I/O, saving energy for this public endpoint.
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Constants
    multipliers = {
        'TikTok': 2.92, 'YouTube': 1.60, 'Instagram': 1.05,
        'Snapchat': 0.90, 'Twitter/X': 0.70, 'Facebook': 0.79, 'Other': 1.00
    }
    device_mult = {'smartphone': 1.0, 'laptop': 1.4, 'tablet': 1.2}
    
    total_co2 = 0.0
    device = data.get('device', 'smartphone')
    d_mult = device_mult.get(device, 1.0)
    
    for platform, minutes in data.get('platforms', {}).items():
        try:
            minutes = float(minutes)
            p_mult = multipliers.get(platform, 1.00)
            total_co2 += minutes * p_mult * d_mult
        except ValueError:
            pass # ignore invalid minutes

    return jsonify({
        "total_co2_grams": round(total_co2, 2),
        "equivalent_km_car": round(total_co2 / 120, 3),
        "equivalent_emails": round(total_co2 / 0.4, 1),
        "equivalent_minutes_website": round(total_co2 / 0.07, 1)
    })

# Serve static files for frontend (in development)
# Green IT justification: Serving static files directly in dev avoids needing a separate web server process like Nginx.
from flask import send_from_directory
import os

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

@app.route('/')
def index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    if os.path.exists(os.path.join(frontend_dir, path)):
        return send_from_directory(frontend_dir, path)
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    # Initialize DB (run init.sql logic if needed, but usually handled by SQLAlchemy or manual run)
    with app.app_context():
        db.create_all()
<<<<<<< Updated upstream
    app.run(debug=True, port=5000)
# Backend logic refinements
=======
    app.run(debug=True, port=5001)
>>>>>>> Stashed changes
