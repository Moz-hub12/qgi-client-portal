from datetime import datetime
import json
from src.models.user import db

class Document(db.Model):
    """Document storage model for investor documents"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # statement, ips, agreement, kyc
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=False)  # Supabase storage path
    file_name = db.Column(db.String(200), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)  # For signed URLs
    is_active = db.Column(db.Boolean, default=True)
    extra_data = db.Column(db.Text, nullable=True)  # JSON string for additional metadata
    
    # Relationship
    user = db.relationship('User', backref=db.backref('documents', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document_type': self.document_type,
            'title': self.title,
            'description': self.description,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active,
            'metadata': json.loads(self.extra_data) if self.extra_data else {}
        }
    
    def update_metadata(self, data):
        """Update metadata with new information"""
        current_data = json.loads(self.extra_data) if self.extra_data else {}
        current_data.update(data)
        self.extra_data = json.dumps(current_data)
    
    def get_metadata(self):
        """Get metadata as dictionary"""
        return json.loads(self.extra_data) if self.extra_data else {}

