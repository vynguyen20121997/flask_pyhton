"""Database models for the course platform."""

from datetime import datetime
from . import db

class User(db.Model):
    """User model for authentication and profile management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role = db.Column(db.String(20), default='student', nullable=False)  # student, admin
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive, banned
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.email}>'

class Course(db.Model):
    """Course model for educational content."""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    duration_hours = db.Column(db.Integer)
    level = db.Column(db.String(20))  # beginner, intermediate, advanced
    category = db.Column(db.String(50))
    thumbnail_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive, draft
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='course', lazy=True)

    def to_dict(self):
        """Convert course object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'duration_hours': self.duration_hours,
            'level': self.level,
            'category': self.category,
            'thumbnail_url': self.thumbnail_url,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'enrollment_count': len(self.enrollments)
        }

    def __repr__(self):
        return f'<Course {self.title}>'

class Product(db.Model):
    """Product model for educational tools and materials."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    image_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive, out_of_stock
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def to_dict(self):
        """Convert product object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    """Order model for purchase transactions."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, paid, cancelled, refunded
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert order object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'items': [item.to_dict() for item in self.order_items]
        }

    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    """Order item model for individual items in an order."""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Float, nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # course, product

    def to_dict(self):
        """Convert order item object to dictionary."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'course_id': self.course_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'item_type': self.item_type,
            'course': self.course.to_dict() if self.course else None,
            'product': self.product.to_dict() if self.product else None
        }

    def __repr__(self):
        return f'<OrderItem {self.id}>'

class Enrollment(db.Model):
    """Enrollment model for course registrations."""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    progress = db.Column(db.Float, default=0.0, nullable=False)  # 0-100 percentage
    status = db.Column(db.String(20), default='active', nullable=False)  # active, completed, dropped
    completion_date = db.Column(db.DateTime)

    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)

    def to_dict(self):
        """Convert enrollment object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrolled_at': self.enrolled_at.isoformat(),
            'progress': self.progress,
            'status': self.status,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'course': self.course.to_dict(),
            'user': self.user.to_dict()
        }

    def __repr__(self):
        return f'<Enrollment {self.user_id}-{self.course_id}>'

class Event(db.Model):
    """Event model for scheduled activities."""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), default='upcoming', nullable=False)  # upcoming, ongoing, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert event object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'location': self.location,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Event {self.title}>'

class Post(db.Model):
    """Post model for blog/news content."""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='published', nullable=False)  # draft, published, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert post object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'category': self.category,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author': self.author.to_dict()
        }

    def __repr__(self):
        return f'<Post {self.title}>'

class Message(db.Model):
    """Message model for user communications."""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unread', nullable=False)  # unread, read, replied
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert message object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'content': self.content,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict()
        }

    def __repr__(self):
        return f'<Message {self.subject}>'