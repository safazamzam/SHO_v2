from flask_sqlalchemy import SQLAlchemy
from models.models import db
from datetime import datetime, timedelta

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    reset_token = db.Column(db.String(255), nullable=False, unique=True)
    new_password_hash = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    
    def __init__(self, username, email, reset_token, expires_at=None):
        self.username = username
        self.email = email
        self.reset_token = reset_token
        self.expires_at = expires_at or (datetime.utcnow() + timedelta(hours=24))
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def mark_as_used(self):
        self.is_used = True
        db.session.commit()