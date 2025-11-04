from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.user import User, db
from ..models.document import Document

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/list', methods=['GET'])
@jwt_required()
def list_documents():
    """Get all documents for the current user"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', None)
        
        # Build query
        query = Document.query.filter_by(user_id=user.id)
        
        # Filter by category if specified
        if category:
            query = query.filter_by(category=category)
        
        # Order by created date (newest first)
        query = query.order_by(Document.created_at.desc())
        
        # Paginate results
        documents = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        document_list = []
        for doc in documents.items:
            document_list.append({
                'id': doc.id,
                'filename': doc.filename,
                'original_filename': doc.original_filename,
                'file_size': doc.file_size,
                'mime_type': doc.mime_type,
                'category': doc.category,
                'description': doc.description,
                'file_path': doc.file_path,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
                'extra_data': doc.get_extra_data()
            })
        
        return jsonify({
            'documents': document_list,
            'pagination': {
                'page': documents.page,
                'pages': documents.pages,
                'per_page': documents.per_page,
                'total': documents.total,
                'has_next': documents.has_next,
                'has_prev': documents.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching documents: {str(e)}")
        return jsonify({'error': 'Failed to fetch documents'}), 500

@documents_bp.route('/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get a specific document by ID"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(
            id=document_id, 
            user_id=user.id
        ).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Generate a demo signed URL for the document
        signed_url = f"https://demo-storage.qgi.com/documents/{document.file_path}?expires=3600"
        
        return jsonify({
            'document': {
                'id': document.id,
                'filename': document.filename,
                'original_filename': document.original_filename,
                'file_size': document.file_size,
                'mime_type': document.mime_type,
                'category': document.category,
                'description': document.description,
                'file_path': document.file_path,
                'created_at': document.created_at.isoformat(),
                'updated_at': document.updated_at.isoformat() if document.updated_at else None,
                'extra_data': document.get_extra_data(),
                'signed_url': signed_url
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching document {document_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch document'}), 500

@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a new document (demo mode)"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # In demo mode, simulate file upload
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({'error': 'No file data provided'}), 400
        
        # Create document record
        document = Document(
            user_id=user.id,
            filename=f"demo_{data['filename']}",
            original_filename=data['filename'],
            file_size=data.get('file_size', 1024),
            mime_type=data.get('mime_type', 'application/pdf'),
            category=data.get('category', 'general'),
            description=data.get('description', ''),
            file_path=f"demo/documents/{user.id}/{data['filename']}"
        )
        
        # Add extra data if provided
        if 'extra_data' in data:
            document.set_extra_data(data['extra_data'])
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'message': 'Document uploaded successfully (demo mode)',
            'document': {
                'id': document.id,
                'filename': document.filename,
                'original_filename': document.original_filename,
                'file_size': document.file_size,
                'mime_type': document.mime_type,
                'category': document.category,
                'description': document.description,
                'file_path': document.file_path,
                'created_at': document.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': 'Failed to upload document'}), 500

@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete a document"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(
            id=document_id, 
            user_id=user.id
        ).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # In demo mode, just delete the database record
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'message': 'Document deleted successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete document'}), 500

@documents_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_document_stats():
    """Get document statistics for the current user"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get counts
        total_documents = Document.query.filter_by(user_id=user.id).count()
        statements = Document.query.filter_by(user_id=user.id, category='statement').count()
        agreements = Document.query.filter_by(user_id=user.id, category='agreement').count()
        reports = Document.query.filter_by(user_id=user.id, category='report').count()
        
        return jsonify({
            'stats': {
                'total': total_documents,
                'statements': statements,
                'agreements': agreements,
                'reports': reports,
                'other': total_documents - statements - agreements - reports
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching document stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch document stats'}), 500

