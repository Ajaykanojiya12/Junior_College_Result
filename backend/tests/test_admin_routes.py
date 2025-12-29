# backend/tests/test_admin_routes.py
"""Unit tests for admin routes"""
import unittest
import json
from app import create_app, db
from models import Admin, Teacher
from auth import hash_password

class AdminRoutesTestCase(unittest.TestCase):
    """Test admin route endpoints"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test admin
            admin = Admin(
                username="testadmin",
                password_hash=hash_password("testpass123"),
                email="admin@test.com",
                active=True
            )
            db.session.add(admin)
            db.session.commit()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = self.client.post(
            "/admin/login",
            data=json.dumps({"userid": "testadmin", "password": "testpass123"}),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)
        self.assertEqual(data["role"], "admin")
    
    def test_admin_login_invalid_credentials(self):
        """Test admin login with invalid credentials"""
        response = self.client.post(
            "/admin/login",
            data=json.dumps({"userid": "testadmin", "password": "wrongpass"}),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    def test_admin_login_missing_fields(self):
        """Test admin login with missing fields"""
        response = self.client.post(
            "/admin/login",
            data=json.dumps({"userid": "testadmin"}),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
