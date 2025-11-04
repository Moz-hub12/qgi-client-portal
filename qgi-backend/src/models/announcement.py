from datetime import datetime
import json
from src.models.user import db

class Announcement(db.Model):
    """Announcement model for manager-to-investor communication"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    target_users = db.Column(db.Text, nullable=True)  # JSON array of user IDs, null = all users
    created_by = db.Column(db.Integer, nullable=True)  # Admin/manager user ID
    expires_at = db.Column(db.DateTime, nullable=True)  # Optional expiration date
    extra_data = db.Column(db.Text, nullable=True)  # JSON string for additional data
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'target_users': json.loads(self.target_users) if self.target_users else None,
            'created_by': self.created_by,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'metadata': json.loads(self.extra_data) if self.extra_data else {}
        }
    
    def is_visible_to_user(self, user_id):
        """Check if announcement is visible to specific user"""
        if not self.is_active:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        if self.target_users:
            target_list = json.loads(self.target_users)
            return user_id in target_list
        
        return True  # Visible to all users if no target_users specified
    
    def update_metadata(self, data):
        """Update metadata with new information"""
        current_data = json.loads(self.extra_data) if self.extra_data else {}
        current_data.update(data)
        self.extra_data = json.dumps(current_data)

