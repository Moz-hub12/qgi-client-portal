from datetime import datetime
import json
from src.models.user import db

class SupportRequest(db.Model):
    """Support request model for user support tickets"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)  # statement, withdrawal, general, kyc, technical
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    assigned_to = db.Column(db.Integer, nullable=True)  # Admin/support user ID
    resolution_notes = db.Column(db.Text, nullable=True)
    attachments = db.Column(db.Text, nullable=True)  # JSON array of file paths
    extra_data = db.Column(db.Text, nullable=True)  # JSON string for additional data
    
    # Relationship
    user = db.relationship('User', backref=db.backref('support_requests', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'request_type': self.request_type,
            'subject': self.subject,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'assigned_to': self.assigned_to,
            'resolution_notes': self.resolution_notes,
            'attachments': json.loads(self.attachments) if self.attachments else [],
            'metadata': json.loads(self.extra_data) if self.extra_data else {}
        }
    
    def add_attachment(self, file_path):
        """Add attachment to support request"""
        attachments = json.loads(self.attachments) if self.attachments else []
        attachments.append(file_path)
        self.attachments = json.dumps(attachments)
    
    def update_status(self, new_status, resolution_notes=None):
        """Update support request status"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status in ['resolved', 'closed']:
            self.resolved_at = datetime.utcnow()
            if resolution_notes:
                self.resolution_notes = resolution_notes
    
    def update_metadata(self, data):
        """Update metadata with new information"""
        current_data = json.loads(self.extra_data) if self.extra_data else {}
        current_data.update(data)
        self.extra_data = json.dumps(current_data)

class SupportMessage(db.Model):
    """Support message model for conversation threads"""
    id = db.Column(db.Integer, primary_key=True)
    support_request_id = db.Column(db.Integer, db.ForeignKey('support_request.id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)  # User ID (could be customer or support agent)
    sender_type = db.Column(db.String(20), nullable=False)  # user, admin, system
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_internal = db.Column(db.Boolean, default=False)  # Internal notes not visible to user
    attachments = db.Column(db.Text, nullable=True)  # JSON array of file paths
    
    # Relationship
    support_request = db.relationship('SupportRequest', backref=db.backref('messages', lazy=True, order_by='SupportMessage.created_at'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'support_request_id': self.support_request_id,
            'sender_id': self.sender_id,
            'sender_type': self.sender_type,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_internal': self.is_internal,
            'attachments': json.loads(self.attachments) if self.attachments else []
        }

