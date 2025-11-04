from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
from ..models.user import User, db
from ..models.document import Document
from ..services.supabase_service import supabase_service

documents_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/list', methods=['GET'])
@jwt_required()
def list_documents():
    """Get list of documents for the current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get documents for the user
        documents = Document.query.filter_by(user_id=user.id).order_by(Document.created_at.desc()).all()
        
        document_list = []
        for doc in documents:
            # Generate signed URL for document access
            signed_url = None
            if doc.file_path:
                try:
                    signed_url = supabase_service.get_signed_url("documents", doc.file_path, expires_in=3600)  # 1 hour
                except Exception as e:
                    current_app.logger.error(f"Failed to generate signed URL for {doc.file_path}: {str(e)}")
            
            document_list.append({
                'id': doc.id,
                'title': doc.title,
                'description': doc.description,
                'category': doc.category,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
                'signed_url': signed_url,
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat() if signed_url else None
            })
        
        return jsonify({
            'documents': document_list,
            'total_count': len(document_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': 'Failed to retrieve documents'}), 500

@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a new document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File size too large (max 16MB)'}), 400
        
        # Get form data
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')
        category = request.form.get('category', 'general')
        
        # Upload to Supabase Storage
        try:
            upload_result = supabase_service.upload_file(
                file=file,
                bucket="documents", 
                folder="documents",
                user_id=user.id
            )
            file_path = upload_result['file_path']
        except Exception as e:
            current_app.logger.error(f"Supabase upload error: {str(e)}")
            return jsonify({'error': 'Storage service unavailable'}), 503
        
        # Create document record
        document = Document(
            user_id=user.id,
            title=title,
            description=description,
            category=category,
            file_path=file_path,
            file_type=upload_result.get('original_filename', '').rsplit('.', 1)[-1].lower() if '.' in upload_result.get('original_filename', '') else '',
            file_size=upload_result.get('file_size', file_size),
            original_filename=upload_result.get('original_filename', file.filename)
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': {
                'id': document.id,
                'title': document.title,
                'description': document.description,
                'category': document.category,
                'file_type': document.file_type,
                'file_size': document.file_size,
                'created_at': document.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': 'Failed to upload document'}), 500

@documents_bp.route('/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get a specific document with signed URL"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get document (ensure it belongs to the user)
        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Generate signed URL
        signed_url = None
        if document.file_path:
            try:
                signed_url = supabase_service.get_signed_url("documents", document.file_path, expires_in=3600)
            except Exception as e:
                current_app.logger.error(f"Failed to generate signed URL: {str(e)}")
                return jsonify({'error': 'Failed to generate access URL'}), 500
        
        return jsonify({
            'document': {
                'id': document.id,
                'title': document.title,
                'description': document.description,
                'category': document.category,
                'file_type': document.file_type,
                'file_size': document.file_size,
                'created_at': document.created_at.isoformat(),
                'signed_url': signed_url,
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat() if signed_url else None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving document: {str(e)}")
        return jsonify({'error': 'Failed to retrieve document'}), 500

@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete a document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get document (ensure it belongs to the user)
        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete from Supabase Storage
        if document.file_path:
            try:
                supabase_service.delete_file("documents", document.file_path)
            except Exception as e:
                current_app.logger.warning(f"Failed to delete file from storage: {str(e)}")
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting document: {str(e)}")
        return jsonify({'error': 'Failed to delete document'}), 500

@documents_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get available document categories"""
    categories = [
        {'id': 'statements', 'name': 'Monthly Statements', 'description': 'Monthly portfolio statements'},
        {'id': 'agreements', 'name': 'Investment Agreements', 'description': 'Legal agreements and contracts'},
        {'id': 'reports', 'name': 'Performance Reports', 'description': 'Quarterly and annual reports'},
        {'id': 'tax', 'name': 'Tax Documents', 'description': 'Tax-related documents and forms'},
        {'id': 'kyc', 'name': 'KYC Documents', 'description': 'Know Your Customer documentation'},
        {'id': 'general', 'name': 'General', 'description': 'Other documents'}
    ]
    
    return jsonify({'categories': categories}), 200

@documents_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_document_stats():
    """Get document statistics for the user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get document counts by category
        from sqlalchemy import func
        
        category_stats = db.session.query(
            Document.category,
            func.count(Document.id).label('count'),
            func.sum(Document.file_size).label('total_size')
        ).filter_by(user_id=user.id).group_by(Document.category).all()
        
        stats = {
            'total_documents': Document.query.filter_by(user_id=user.id).count(),
            'total_size': db.session.query(func.sum(Document.file_size)).filter_by(user_id=user.id).scalar() or 0,
            'categories': [
                {
                    'category': stat.category,
                    'count': stat.count,
                    'total_size': stat.total_size or 0
                } for stat in category_stats
            ]
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting document stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

