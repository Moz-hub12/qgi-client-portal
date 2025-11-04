from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.user import User, db
from ..models.support import SupportRequest

support_bp = Blueprint('support', __name__)

@support_bp.route('/requests', methods=['GET'])
@jwt_required()
def list_support_requests():
    """Get all support requests for the current user"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None)
        request_type = request.args.get('type', None)
        
        # Build query
        query = SupportRequest.query.filter_by(user_id=user.id)
        
        # Filter by status if specified
        if status:
            query = query.filter_by(status=status)
        
        # Filter by request type if specified
        if request_type:
            query = query.filter_by(request_type=request_type)
        
        # Order by created date (newest first)
        query = query.order_by(SupportRequest.created_at.desc())
        
        # Paginate results
        requests = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        request_list = []
        for req in requests.items:
            request_list.append({
                'id': req.id,
                'subject': req.subject,
                'description': req.description,
                'request_type': req.request_type,
                'priority': req.priority,
                'status': req.status,
                'created_at': req.created_at.isoformat(),
                'updated_at': req.updated_at.isoformat() if req.updated_at else None,
                'resolved_at': req.resolved_at.isoformat() if req.resolved_at else None,
                'admin_response': req.admin_response,
                'extra_data': req.get_extra_data()
            })
        
        return jsonify({
            'requests': request_list,
            'pagination': {
                'page': requests.page,
                'pages': requests.pages,
                'per_page': requests.per_page,
                'total': requests.total,
                'has_next': requests.has_next,
                'has_prev': requests.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching support requests: {str(e)}")
        return jsonify({'error': 'Failed to fetch support requests'}), 500

@support_bp.route('/requests/<int:request_id>', methods=['GET'])
@jwt_required()
def get_support_request(request_id):
    """Get a specific support request by ID"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        support_request = SupportRequest.query.filter_by(
            id=request_id, 
            user_id=user.id
        ).first()
        
        if not support_request:
            return jsonify({'error': 'Support request not found'}), 404
        
        return jsonify({
            'request': {
                'id': support_request.id,
                'subject': support_request.subject,
                'description': support_request.description,
                'request_type': support_request.request_type,
                'priority': support_request.priority,
                'status': support_request.status,
                'created_at': support_request.created_at.isoformat(),
                'updated_at': support_request.updated_at.isoformat() if support_request.updated_at else None,
                'resolved_at': support_request.resolved_at.isoformat() if support_request.resolved_at else None,
                'admin_response': support_request.admin_response,
                'extra_data': support_request.get_extra_data()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching support request {request_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch support request'}), 500

@support_bp.route('/requests', methods=['POST'])
@jwt_required()
def create_support_request():
    """Create a new support request"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['subject', 'description', 'request_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate request type
        valid_types = ['statement_request', 'withdraw_roi', 'account_update', 'technical_support', 'general_inquiry']
        if data['request_type'] not in valid_types:
            return jsonify({'error': 'Invalid request type'}), 400
        
        # Create support request
        support_request = SupportRequest(
            user_id=user.id,
            subject=data['subject'],
            description=data['description'],
            request_type=data['request_type'],
            priority=data.get('priority', 'normal'),
            status='open'
        )
        
        # Add extra data if provided
        if 'extra_data' in data:
            support_request.set_extra_data(data['extra_data'])
        
        db.session.add(support_request)
        db.session.commit()
        
        return jsonify({
            'message': 'Support request created successfully',
            'request': {
                'id': support_request.id,
                'subject': support_request.subject,
                'description': support_request.description,
                'request_type': support_request.request_type,
                'priority': support_request.priority,
                'status': support_request.status,
                'created_at': support_request.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating support request: {str(e)}")
        return jsonify({'error': 'Failed to create support request'}), 500

@support_bp.route('/requests/<int:request_id>/update', methods=['PUT'])
@jwt_required()
def update_support_request(request_id):
    """Update a support request (user can only update description)"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        support_request = SupportRequest.query.filter_by(
            id=request_id, 
            user_id=user.id
        ).first()
        
        if not support_request:
            return jsonify({'error': 'Support request not found'}), 404
        
        # Only allow updates if request is still open
        if support_request.status in ['resolved', 'closed']:
            return jsonify({'error': 'Cannot update resolved or closed requests'}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Users can only update description and extra data
        if 'description' in data:
            support_request.description = data['description']
        
        if 'extra_data' in data:
            support_request.set_extra_data(data['extra_data'])
        
        support_request.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Support request updated successfully',
            'request': {
                'id': support_request.id,
                'subject': support_request.subject,
                'description': support_request.description,
                'request_type': support_request.request_type,
                'priority': support_request.priority,
                'status': support_request.status,
                'updated_at': support_request.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating support request {request_id}: {str(e)}")
        return jsonify({'error': 'Failed to update support request'}), 500

@support_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_support_stats():
    """Get support request statistics for the current user"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get counts
        total_requests = SupportRequest.query.filter_by(user_id=user.id).count()
        open_requests = SupportRequest.query.filter_by(user_id=user.id, status='open').count()
        in_progress_requests = SupportRequest.query.filter_by(user_id=user.id, status='in_progress').count()
        resolved_requests = SupportRequest.query.filter_by(user_id=user.id, status='resolved').count()
        
        return jsonify({
            'stats': {
                'total': total_requests,
                'open': open_requests,
                'in_progress': in_progress_requests,
                'resolved': resolved_requests,
                'closed': total_requests - open_requests - in_progress_requests - resolved_requests
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching support stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch support stats'}), 500

@support_bp.route('/types', methods=['GET'])
def get_request_types():
    """Get available support request types"""
    request_types = [
        {
            'value': 'statement_request',
            'label': 'Request Statement',
            'description': 'Request monthly or quarterly statements'
        },
        {
            'value': 'withdraw_roi',
            'label': 'Withdraw ROI',
            'description': 'Request withdrawal of return on investment'
        },
        {
            'value': 'account_update',
            'label': 'Account Update',
            'description': 'Update account information or preferences'
        },
        {
            'value': 'technical_support',
            'label': 'Technical Support',
            'description': 'Report technical issues or get help with the platform'
        },
        {
            'value': 'general_inquiry',
            'label': 'General Inquiry',
            'description': 'General questions or other requests'
        }
    ]
    
    return jsonify({'request_types': request_types}), 200

