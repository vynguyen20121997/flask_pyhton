"""User management routes."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from .. import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user profile."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'full_name' in data and data['full_name'].strip():
            user.full_name = data['full_name'].strip()
        if 'phone' in data:
            user.phone = data['phone'].strip() if data['phone'] else None
        if 'address' in data:
            user.address = data['address'].strip() if data['address'] else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_current_user():
    """Delete current user account."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin account'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Account deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/me/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get current user statistics."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        from ..models import Enrollment, Order
        
        stats = {
            'total_enrollments': len(user.enrollments),
            'active_enrollments': len([e for e in user.enrollments if e.status == 'active']),
            'completed_enrollments': len([e for e in user.enrollments if e.status == 'completed']),
            'total_orders': len(user.orders),
            'paid_orders': len([o for o in user.orders if o.status == 'paid']),
            'total_spent': sum([o.total_amount for o in user.orders if o.status == 'paid'])
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500