# backend/decorators.py
"""
Utility decorators for Flask routes.
"""

from functools import wraps
from typing import Any, Dict, cast
from flask import request, current_app
from schemas import PaginationSchema
from marshmallow import ValidationError
from errors import ValidationError as AppValidationError

pagination_schema = PaginationSchema()

# ======================================================
# PAGINATION DECORATOR (UNCHANGED)
# ======================================================
def paginated(f):
    """Decorator to add pagination to list endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Normalize query args to single (flat) values for marshmallow
            raw = request.args.to_dict(flat=False)
            args_map = {k: (v[0] if isinstance(v, list) and v else v) for k, v in raw.items()}
            pagination_data = cast(Dict[str, Any], pagination_schema.load(args_map))
            kwargs["page"] = pagination_data.get("page", 1)
            kwargs["limit"] = pagination_data.get("limit", 10)
            kwargs["search"] = pagination_data.get("search")
            return f(*args, **kwargs)
        except ValidationError as err:
            raise AppValidationError(
                f"Invalid pagination parameters: {err.messages}"
            )
    return decorated_function


# ======================================================
# LOGGING DECORATOR (UNCHANGED)
# ======================================================
def log_endpoint(action_name):
    """Decorator to log endpoint access and actions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            method = request.method
            endpoint = request.endpoint
            current_app.logger.info(f"{action_name} - {method} {endpoint}")
            try:
                result = f(*args, **kwargs)
                current_app.logger.info(f"{action_name} - Success")
                return result
            except Exception as e:
                current_app.logger.error(f"{action_name} - Error: {str(e)}")
                raise
        return decorated_function
    return decorator


# ======================================================
# ADMIN REQUIRED DECORATOR (NEW - REQUIRED)
# ======================================================
def admin_required(f):
    """
    Allows access ONLY to users with role = ADMIN.
    Must be used AFTER @token_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_type = kwargs.get("user_type")

        # Accept case-insensitive admin role values (e.g., 'ADMIN' or 'admin')
        try:
            is_admin = isinstance(user_type, str) and user_type.upper() == "ADMIN"
        except Exception:
            is_admin = False

        if not is_admin:
            return {"error": "Admin access required"}, 403

        return f(*args, **kwargs)

    return decorated_function
