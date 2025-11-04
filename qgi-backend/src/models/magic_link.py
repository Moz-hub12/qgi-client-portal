# src/models/magic_link.py
from datetime import datetime
from src.models.user import db

class MagicLinkToken(db.Model):
    """Model for storing magic link tokens in database"""
    __tablename__ = 'magic_link_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<MagicLinkToken {self.token[:10]}... for {self.email}>'
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.used and datetime.utcnow() < self.expires_at
    
    def mark_as_used(self):
        """Mark token as used"""
        self.used = True
        db.session.commit()
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired tokens from database"""
        expired = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for token in expired:
            db.session.delete(token)
        db.session.commit()
        return len(expired)

