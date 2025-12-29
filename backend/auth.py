# backend/auth.py

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from app import db
from models import Teacher, TeacherSubjectAllocation, Subject, Admin

# Utility functions used by tests and other modules
def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return check_password_hash(hashed, password)
    except Exception:
        return False


def generate_token(user_id: int, user_type: str, expires_hours: int = 10) -> str:
    payload = {
        "user_id": user_id,
        "user_type": user_type,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")


def verify_token(token: str):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except Exception:
        return None

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# ======================================================
# TOKEN DECORATOR
# ======================================================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            try:
                token = request.headers["Authorization"].split(" ")[1]
            except IndexError:
                return {"error": "Invalid Authorization header"}, 401

        if not token:
            return {"error": "Token missing"}, 401

        try:
            data = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=["HS256"]
            )
            # Support tokens issued for both teachers and admins.
            # Prefer Admin lookup when token indicates ADMIN role to avoid id collisions.
            role = (data.get("role") or data.get("user_type") or "").upper()
            user = None
            if role == "ADMIN":
                user = Admin.query.get(data.get("user_id"))
            else:
                user = Teacher.query.get(data.get("user_id"))

            # If role was ADMIN but admin record not found, fallback to Teacher only if present
            if role == "ADMIN" and user is None:
                user = Teacher.query.get(data.get("user_id"))

            # Debug logging to assist with tracing token/user resolution during development
            try:
                print(f"[auth.token_required] token data={data}, role={role}, resolved_user={user}")
            except Exception:
                pass

            # If teacher lookup failed and role indicates ADMIN, try Admin table
            if user is None and role == "ADMIN":
                user = Admin.query.get(data.get("user_id"))

            if not user or not getattr(user, "active", True):
                return {"error": "Invalid or inactive user"}, 401

        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}, 401
        except Exception:
            return {"error": "Invalid token"}, 401

        # extra-safety: ensure `user` is defined and not None for static checkers
        if user is None:
            return {"error": "Invalid or inactive user"}, 401

        return f(
            user_id=getattr(user, "teacher_id", None) or getattr(user, "admin_id", None),
            user_type=getattr(user, "role", role),
            *args,
            **kwargs
        )

    return decorated


# ======================================================
# LOGIN
# ======================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    userid = data.get("userid")
    password = data.get("password")

    if not userid or not password:
        return {"error": "userid and password required"}, 400

    # Prefer admin login first (admins may share ids/userids with teachers)
    role = None
    user_id = None

    admin = Admin.query.filter_by(username=userid, active=True).first()
    if admin and check_password_hash(admin.password_hash, password):
        role = "ADMIN"
        user_id = admin.admin_id
    else:
        # Try teacher login (teachers use `userid`)
        user = Teacher.query.filter_by(userid=userid, active=True).first()
        if user and check_password_hash(user.password_hash, password):
            role = (user.role or "TEACHER").upper()
            user_id = user.teacher_id

    if not role or not user_id:
        return {"error": "Invalid username or password"}, 401

    token = jwt.encode(
        {
            "user_id": user_id,
            "role": role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=10),
        },
        Config.SECRET_KEY,
        algorithm="HS256",
    )

    return {"token": token, "role": role}, 200



# ======================================================
# CURRENT USER INFO
# ======================================================
@auth_bp.route("/me", methods=["GET"])
@token_required
def me(user_id=None, user_type=None):
    # Return info based on role carried by the token/decorator
    role = (user_type or "TEACHER").upper()

    if role == "ADMIN":
        admin = Admin.query.get(user_id)
        if not admin:
            return {"error": "Admin not found"}, 404
        return jsonify({
            "admin_id": admin.admin_id,
            "username": admin.username,
            "email": admin.email,
            "role": "ADMIN"
        }), 200

    # Default: teacher
    teacher = Teacher.query.get(user_id)
    if not teacher:
        return {"error": "User not found"}, 404

    allocations = TeacherSubjectAllocation.query.filter_by(
        teacher_id=teacher.teacher_id
    ).all()

    allocation_data = []
    for alloc in allocations:
        subject = Subject.query.get(alloc.subject_id)
        if subject:
            allocation_data.append({
                "subject_id": subject.subject_id,
                "subject_code": subject.subject_code,
                "subject_name": subject.subject_name,
                "division": alloc.division
            })

    return jsonify({
        "teacher_id": teacher.teacher_id,
        "name": teacher.name,
        "userid": teacher.userid,
        "role": teacher.role,
        "allocations": allocation_data
    }), 200
