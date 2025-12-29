# backend/errors.py
"""
Custom exceptions and error handling for the application.
"""

class ValidationError(Exception):
    """Raised when request validation fails."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication failed", status_code=401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthorizationError(Exception):
    """Raised when user lacks permissions."""
    def __init__(self, message="Access denied", status_code=403):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(Exception):
    """Raised when resource is not found."""
    def __init__(self, message="Resource not found", status_code=404):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseError(Exception):
    """Raised when database operation fails."""
    def __init__(self, message="Database operation failed", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def register_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return {"error": e.message}, e.status_code
    
    @app.errorhandler(AuthenticationError)
    def handle_auth_error(e):
        return {"error": e.message}, e.status_code
    
    @app.errorhandler(AuthorizationError)
    def handle_authz_error(e):
        return {"error": e.message}, e.status_code
    
    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return {"error": e.message}, e.status_code
    
    @app.errorhandler(DatabaseError)
    def handle_db_error(e):
        app.logger.error(f"Database error: {e.message}")
        return {"error": "Database operation failed"}, e.status_code
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        return {"error": "Bad request"}, 400
    
    @app.errorhandler(404)
    def handle_not_found_default(e):
        return {"error": "Endpoint not found"}, 404
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        app.logger.exception("Internal server error")
        return {"error": "Internal server error"}, 500
