"""Admin management routes."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Course, Product, Order, Enrollment, Event, Post, Message
from .. import db
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if user is admin."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Course management
@admin_bp.route('/courses', methods=['POST'])
@admin_required
def create_course():
    """Create a new course."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        course = Course(
            title=data['title'],
            description=data.get('description'),
            price=float(data['price']),
            duration_hours=data.get('duration_hours'),
            level=data.get('level'),
            category=data.get('category'),
            thumbnail_url=data.get('thumbnail_url'),
            status=data.get('status', 'active')
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Course created successfully',
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
@admin_required
def update_course(course_id):
    """Update a course."""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        for field in ['title', 'description', 'price', 'duration_hours', 'level', 'category', 'thumbnail_url', 'status']:
            if field in data:
                if field == 'price':
                    setattr(course, field, float(data[field]))
                else:
                    setattr(course, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Course updated successfully',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@admin_required
def delete_course(course_id):
    """Delete a course."""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if course has enrollments
        if course.enrollments:
            return jsonify({'error': 'Cannot delete course with existing enrollments'}), 400
        
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({'message': 'Course deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Product management
@admin_bp.route('/products', methods=['POST'])
@admin_required
def create_product():
    """Create a new product."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=float(data['price']),
            category=data.get('category'),
            stock_quantity=int(data.get('stock_quantity', 0)),
            image_url=data.get('image_url'),
            status=data.get('status', 'active')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update a product."""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        for field in ['name', 'description', 'price', 'category', 'stock_quantity', 'image_url', 'status']:
            if field in data:
                if field == 'price':
                    setattr(product, field, float(data[field]))
                elif field == 'stock_quantity':
                    setattr(product, field, int(data[field]))
                else:
                    setattr(product, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete a product."""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        role = request.args.get('role')
        status = request.args.get('status')
        
        query = User.query
        if role:
            query = query.filter_by(role=role)
        if status:
            query = query.filter_by(status=status)
        
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update a user."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        for field in ['full_name', 'phone', 'address', 'role', 'status']:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin user'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Orders management
@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """Get all orders with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status')
        
        query = Order.query
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'pagination': {
                'page': orders.page,
                'pages': orders.pages,
                'per_page': orders.per_page,
                'total': orders.total,
                'has_next': orders.has_next,
                'has_prev': orders.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """Update order status."""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'paid', 'cancelled', 'refunded']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Dashboard statistics
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """Get dashboard statistics."""
    try:
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(status='active').count(),
            'total_courses': Course.query.count(),
            'active_courses': Course.query.filter_by(status='active').count(),
            'total_products': Product.query.count(),
            'active_products': Product.query.filter_by(status='active').count(),
            'total_orders': Order.query.count(),
            'paid_orders': Order.query.filter_by(status='paid').count(),
            'pending_orders': Order.query.filter_by(status='pending').count(),
            'total_enrollments': Enrollment.query.count(),
            'active_enrollments': Enrollment.query.filter_by(status='active').count(),
            'completed_enrollments': Enrollment.query.filter_by(status='completed').count(),
            'total_revenue': db.session.query(db.func.sum(Order.total_amount)).filter_by(status='paid').scalar() or 0
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enrollments management
@admin_bp.route('/enrollments', methods=['GET'])
@admin_required
def get_all_enrollments():
    """Get all enrollments with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status')
        course_id = request.args.get('course_id', type=int)
        
        query = Enrollment.query
        if status:
            query = query.filter_by(status=status)
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        enrollments = query.order_by(Enrollment.enrolled_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'enrollments': [enrollment.to_dict() for enrollment in enrollments.items],
            'pagination': {
                'page': enrollments.page,
                'pages': enrollments.pages,
                'per_page': enrollments.per_page,
                'total': enrollments.total,
                'has_next': enrollments.has_next,
                'has_prev': enrollments.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500