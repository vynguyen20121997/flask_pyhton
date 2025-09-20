"""Enrollment management routes."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Enrollment, Course, User
from .. import db
from datetime import datetime

enrollments_bp = Blueprint('enrollments', __name__)

@enrollments_bp.route('/my-enrollments', methods=['GET'])
@jwt_required()
def get_my_enrollments():
    """Get current user's enrollments."""
    try:
        user_id = get_jwt_identity()
        status = request.args.get('status')
        
        query = Enrollment.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        
        enrollments = query.order_by(Enrollment.enrolled_at.desc()).all()
        
        return jsonify({
            'enrollments': [enrollment.to_dict() for enrollment in enrollments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enrollments_bp.route('/<int:enrollment_id>/progress', methods=['PUT'])
@jwt_required()
def update_progress(enrollment_id):
    """Update enrollment progress."""
    try:
        user_id = get_jwt_identity()
        enrollment = Enrollment.query.filter_by(
            id=enrollment_id, user_id=user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        data = request.get_json()
        progress = data.get('progress', 0)
        
        if not isinstance(progress, (int, float)) or not 0 <= progress <= 100:
            return jsonify({'error': 'Progress must be a number between 0 and 100'}), 400
        
        enrollment.progress = float(progress)
        
        # Mark as completed if progress is 100%
        if progress == 100 and enrollment.status != 'completed':
            enrollment.status = 'completed'
            enrollment.completion_date = datetime.utcnow()
        elif progress < 100 and enrollment.status == 'completed':
            # Revert completion if progress goes below 100%
            enrollment.status = 'active'
            enrollment.completion_date = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated successfully',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enrollments_bp.route('/<int:enrollment_id>/complete', methods=['POST'])
@jwt_required()
def complete_course(enrollment_id):
    """Mark course as completed."""
    try:
        user_id = get_jwt_identity()
        enrollment = Enrollment.query.filter_by(
            id=enrollment_id, user_id=user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        if enrollment.status == 'completed':
            return jsonify({'error': 'Course is already completed'}), 400
        
        enrollment.status = 'completed'
        enrollment.progress = 100.0
        enrollment.completion_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Course completed successfully',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enrollments_bp.route('/<int:enrollment_id>/drop', methods=['POST'])
@jwt_required()
def drop_course(enrollment_id):
    """Drop a course."""
    try:
        user_id = get_jwt_identity()
        enrollment = Enrollment.query.filter_by(
            id=enrollment_id, user_id=user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        if enrollment.status == 'dropped':
            return jsonify({'error': 'Course is already dropped'}), 400
        
        enrollment.status = 'dropped'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Course dropped successfully',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enrollments_bp.route('/<int:enrollment_id>/reactivate', methods=['POST'])
@jwt_required()
def reactivate_enrollment(enrollment_id):
    """Reactivate a dropped enrollment."""
    try:
        user_id = get_jwt_identity()
        enrollment = Enrollment.query.filter_by(
            id=enrollment_id, user_id=user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        if enrollment.status != 'dropped':
            return jsonify({'error': 'Only dropped enrollments can be reactivated'}), 400
        
        enrollment.status = 'active'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Enrollment reactivated successfully',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enrollments_bp.route('/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def get_enrollment(enrollment_id):
    """Get specific enrollment details."""
    try:
        user_id = get_jwt_identity()
        enrollment = Enrollment.query.filter_by(
            id=enrollment_id, user_id=user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        return jsonify({'enrollment': enrollment.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500