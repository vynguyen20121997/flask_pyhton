"""Order management routes."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Order, OrderItem, Course, Product, User, Enrollment
from .. import db

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        items = data.get('items', [])
        if not items:
            return jsonify({'error': 'Order items are required'}), 400
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=0,
            payment_method=data.get('payment_method', 'card')
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        total_amount = 0
        
        for item_data in items:
            item_type = item_data.get('type')  # 'course' or 'product'
            item_id = item_data.get('id')
            quantity = item_data.get('quantity', 1)
            
            if not item_type or not item_id:
                return jsonify({'error': 'Item type and ID are required'}), 400
            
            if item_type == 'course':
                course = Course.query.get(item_id)
                if not course:
                    return jsonify({'error': f'Course {item_id} not found'}), 404
                
                if course.status != 'active':
                    return jsonify({'error': f'Course {course.title} is not available'}), 400
                
                # Check if already enrolled
                existing_enrollment = Enrollment.query.filter_by(
                    user_id=user_id, course_id=item_id
                ).first()
                
                if existing_enrollment:
                    return jsonify({'error': f'Already enrolled in course {course.title}'}), 400
                
                price = course.price
                
                order_item = OrderItem(
                    order_id=order.id,
                    course_id=item_id,
                    quantity=1,  # Courses are always quantity 1
                    price=price,
                    item_type='course'
                )
                
            elif item_type == 'product':
                product = Product.query.get(item_id)
                if not product:
                    return jsonify({'error': f'Product {item_id} not found'}), 404
                
                if product.status != 'active':
                    return jsonify({'error': f'Product {product.name} is not available'}), 400
                
                if product.stock_quantity < quantity:
                    return jsonify({'error': f'Insufficient stock for {product.name}. Available: {product.stock_quantity}'}), 400
                
                price = product.price * quantity
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_id,
                    quantity=quantity,
                    price=price,
                    item_type='product'
                )
            else:
                return jsonify({'error': 'Invalid item type. Must be "course" or "product"'}), 400
            
            db.session.add(order_item)
            total_amount += price
        
        order.total_amount = total_amount
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/pay', methods=['POST'])
@jwt_required()
def pay_order(order_id):
    """Process payment for an order."""
    try:
        user_id = get_jwt_identity()
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.status != 'pending':
            return jsonify({'error': 'Order is not in pending status'}), 400
        
        # Mock payment processing - in real app, integrate with payment gateway
        payment_data = request.get_json()
        payment_method = payment_data.get('payment_method', order.payment_method)
        
        # Simulate payment validation
        if not payment_method:
            return jsonify({'error': 'Payment method is required'}), 400
        
        # Process payment (mock implementation)
        order.status = 'paid'
        order.payment_status = 'completed'
        order.payment_method = payment_method
        
        # Process order items
        for item in order.order_items:
            if item.item_type == 'course':
                # Create enrollment
                enrollment = Enrollment(
                    user_id=user_id,
                    course_id=item.course_id
                )
                db.session.add(enrollment)
                
            elif item.item_type == 'product':
                # Update stock
                product = Product.query.get(item.product_id)
                if product:
                    product.stock_quantity -= item.quantity
                    if product.stock_quantity <= 0:
                        product.status = 'out_of_stock'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment processed successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """Get current user's orders."""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status')
        
        query = Order.query.filter_by(user_id=user_id)
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

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a specific order."""
    try:
        user_id = get_jwt_identity()
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({'order': order.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order."""
    try:
        user_id = get_jwt_identity()
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.status != 'pending':
            return jsonify({'error': 'Only pending orders can be cancelled'}), 400
        
        order.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500