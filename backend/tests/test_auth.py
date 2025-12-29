# backend/tests/test_auth.py
"""Unit tests for authentication module"""
import unittest
from auth import hash_password, verify_password, generate_token, verify_token
import config

class TestAuthentication(unittest.TestCase):
    """Test password and token functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Check that hashed password is different from original
        self.assertNotEqual(hashed, password)
        
        # Check that hash can be verified
        self.assertTrue(verify_password(password, hashed))
    
    def test_verify_password_fails(self):
        """Test that wrong password fails verification"""
        password = "correct_password"
        hashed = hash_password(password)
        
        self.assertFalse(verify_password("wrong_password", hashed))
    
    def test_generate_token(self):
        """Test JWT token generation"""
        user_id = 1
        user_type = "admin"
        
        token = generate_token(user_id, user_type)
        
        # Check token is a string
        self.assertIsInstance(token, str)
        
        # Check token can be verified
        payload = verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["user_id"], user_id)
        self.assertEqual(payload["user_type"], user_type)
    
    def test_verify_invalid_token(self):
        """Test that invalid token fails verification"""
        payload = verify_token("invalid_token")
        self.assertIsNone(payload)
    
    def test_token_expiration(self):
        """Test that expired tokens fail verification"""
        user_id = 1
        user_type = "admin"
        
        # Generate token that expires in -1 second (already expired)
        import jwt
        from datetime import datetime, timedelta
        
        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() - timedelta(seconds=1)
        }
        
        token = jwt.encode(payload, config.SECRET_KEY, algorithm='HS256')
        result = verify_token(token)
        
        # Expired token should return None
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
