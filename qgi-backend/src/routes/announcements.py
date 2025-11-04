from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.user import User, db
from ..models.announcement import Announcement

announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('/list', methods=['GET'])
@jwt_required()
def list_announcements():
    """Get all announcements for the current user"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        priority = request.args.get('priority', None)
        
        # Build query
        query = Announcement.query
        
        # Filter by priority if specified
        if priority:
            query = query.filter_by(priority=priority)
        
        # Order by created date (newest first)
        query = query.order_by(Announcement.created_at.desc())
        
        # Paginate results
        announcements = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        announcement_list = []
        for announcement in announcements.items:
            announcement_list.append({
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'priority': announcement.priority,
                'category': announcement.category,
                'created_at': announcement.created_at.isoformat(),
                'updated_at': announcement.updated_at.isoformat() if announcement.updated_at else None,
                'is_read': announcement.is_read,
                'extra_data': announcement.get_extra_data()
            })
        
        return jsonify({
            'announcements': announcement_list,
            'pagination': {
                'page': announcements.page,
                'pages': announcements.pages,
                'per_page': announcements.per_page,
                'total': announcements.total,
                'has_next': announcements.has_next,
                'has_prev': announcements.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching announcements: {str(e)}")
        return jsonify({'error': 'Failed to fetch announcements'}), 500

@announcements_bp.route('/<int:announcement_id>', methods=['GET'])
@jwt_required()
def get_announcement(announcement_id):
    """Get a specific announcement by ID"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        announcement = Announcement.query.get(announcement_id)
        
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        return jsonify({
            'announcement': {
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'priority': announcement.priority,
                'category': announcement.category,
                'created_at': announcement.created_at.isoformat(),
                'updated_at': announcement.updated_at.isoformat() if announcement.updated_at else None,
                'is_read': announcement.is_read,
                'extra_data': announcement.get_extra_data()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching announcement {announcement_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch announcement'}), 500

@announcements_bp.route('/<int:announcement_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_announcement_read(announcement_id):
    """Mark an announcement as read"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        announcement = Announcement.query.get(announcement_id)
        
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Mark as read
        announcement.is_read = True
        announcement.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Announcement marked as read',
            'announcement': {
                'id': announcement.id,
                'is_read': announcement.is_read,
                'updated_at': announcement.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error marking announcement {announcement_id} as read: {str(e)}")
        return jsonify({'error': 'Failed to mark announcement as read'}), 500

@announcements_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_announcement_stats():
    """Get announcement statistics for the current user"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get counts
        total_announcements = Announcement.query.count()
        unread_announcements = Announcement.query.filter_by(is_read=False).count()
        high_priority = Announcement.query.filter_by(priority='high').count()
        
        return jsonify({
            'stats': {
                'total': total_announcements,
                'unread': unread_announcements,
                'high_priority': high_priority,
                'read': total_announcements - unread_announcements
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching announcement stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch announcement stats'}), 500

# Admin routes (for demo purposes - in production, these would be in a separate admin blueprint)
@announcements_bp.route('/create', methods=['POST'])
@jwt_required()
def create_announcement():
    """Create a new announcement (admin function for demo)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create announcement
        announcement = Announcement(
            title=data['title'],
            content=data['content'],
            priority=data.get('priority', 'normal'),
            category=data.get('category', 'general'),
            is_read=False
        )
        
        # Add extra data if provided
        if 'extra_data' in data:
            announcement.set_extra_data(data['extra_data'])
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({
            'message': 'Announcement created successfully',
            'announcement': {
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'priority': announcement.priority,
                'category': announcement.category,
                'created_at': announcement.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating announcement: {str(e)}")
        return jsonify({'error': 'Failed to create announcement'}), 500

