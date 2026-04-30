from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Green IT justification: Using SQLAlchemy models to interact with the database
# prevents manual string concatenation (prevents SQL injection) and allows for
# cleaner parameterized queries natively.
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    device_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('ScrollSession', backref='user', lazy=True, cascade='all, delete-orphan')
    challenges = db.relationship('GreenChallenge', backref='user', lazy=True, cascade='all, delete-orphan')

class ScrollSession(db.Model):
    __tablename__ = 'scroll_sessions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    platform = db.Column(db.String(30), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    device = db.Column(db.String(20))
    co2_grams = db.Column(db.Float)
    session_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GreenChallenge(db.Model):
    __tablename__ = 'green_challenges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(30))
    daily_limit_minutes = db.Column(db.Integer, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')
    co2_saved_grams = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
# Database schema optimizations
