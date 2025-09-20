"""Course management routes."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Course, User, Enrollment
from .. import db

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/', methods=['GET'])
def get_courses():
    """Get all courses with filtering and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Max 100 per page
        category = request.args.get('category')
        level = request.args.get('level')
        status = request.args.get('status', 'active')
        search = request.args.get('search', '').strip()
        
        query = Course.query.filter_by(status=status)
        
        if category:
            query = query.filter_by(category=category)
        if level:
            query = query.filter_by(level=level)
        if search:
            query = query.filter(Course.title.contains(search))
        
        courses = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'courses': [course.to_dict() for course in courses.items],
            'pagination': {
                'page': courses.page,
                'pages': courses.pages,
                'per_page': courses.per_page,
                'total': courses.total,
                'has_next': courses.has_next,
                'has_prev': courses.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get a specific course by ID."""
    try:
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify({'course': course.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_course(course_id):
    """Enroll current user in a course."""
    try:
        user_id = get_jwt_identity()
        
        # Check if course exists and is active
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        if course.status != 'active':
            return jsonify({'error': 'Course is not available for enrollment'}), 400
        
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            user_id=user_id, course_id=course_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Already enrolled in this course'}), 400
        
        # Create enrollment
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': 'Enrolled successfully',
            'enrollment': enrollment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    """Get current user's enrolled courses."""
    try:
        user_id = get_jwt_identity()
        
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'enrollments': [enrollment.to_dict() for enrollment in enrollments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all course categories."""
    try:
        categories = db.session.query(Course.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({'categories': category_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/levels', methods=['GET'])
def get_levels():
    """Get all course levels."""
    try:
        levels = ['beginner', 'intermediate', 'advanced']
        return jsonify({'levels': levels}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500