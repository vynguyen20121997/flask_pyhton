"""Development server runner."""

from app import create_app
from werkzeug.security import generate_password_hash
import os

def create_admin_user(app):
    """Create default admin user if not exists."""
    with app.app_context():
        from models import User
        from app import db
        
        admin = User.query.filter_by(email='admin@courseplatform.com').first()
        if not admin:
            admin_user = User(
                email='admin@courseplatform.com',
                password=generate_password_hash('admin123'),
                full_name='System Administrator',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created: admin@courseplatform.com / admin123")
        else:
            print("ℹ️  Admin user already exists")

if __name__ == '__main__':
    # Create Flask app
    app = create_app()
    
    # Initialize database and create tables
    with app.app_context():
        from app import db
        db.create_all()
        print("✅ Database tables created")
        
        # Create admin user
        create_admin_user(app)
    
    # Run development server
    print("🚀 Starting Flask development server...")
    print("📍 API Base URL: http://localhost:5000/api")
    print("🏥 Health Check: http://localhost:5000/api/health")
    
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        use_reloader=True
    )