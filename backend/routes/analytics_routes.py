# routes/analytics_routes.py

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app import db
from models import Student, Result
from auth import token_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


# ======================================================
# 1️⃣ Health Check
# ======================================================
@analytics_bp.route("/health", methods=["GET"])
def health_check():
    return {"status": "ok"}, 200


# ======================================================
# 2️⃣ Division Summary
# ======================================================
@analytics_bp.route("/division-summary", methods=["GET"])
@token_required
def division_summary(user_id=None, user_type=None):
    """
    Summary statistics for a division
    """
    division = request.args.get("division")
    if not division:
        return {"error": "division is required"}, 400

    total_students = Student.query.filter_by(division=division).count()
    results_published = Result.query.filter_by(
        division=division,
        is_published=True
    ).count()

    avg_percentage = db.session.query(
        func.avg(Result.percentage)
    ).filter_by(division=division).scalar()

    return jsonify({
        "division": division,
        "total_students": total_students,
        "results_published": results_published,
        "average_percentage": round(avg_percentage, 2) if avg_percentage else 0
    }), 200


# ======================================================
# 3️⃣ Top Performers (Division-wise)
# ======================================================
@analytics_bp.route("/topper", methods=["GET"])
@token_required
def division_topper(user_id=None, user_type=None):
    """
    Get top N students of a division
    """
    division = request.args.get("division")
    limit = int(request.args.get("limit", 5))

    if not division:
        return {"error": "division is required"}, 400

    toppers = Result.query.filter_by(
        division=division,
        is_published=True
    ).order_by(Result.percentage.desc()).limit(limit).all()

    return jsonify([
        {
            "roll_no": r.roll_no,
            "name": r.name,
            "percentage": r.percentage
        }
        for r in toppers
    ]), 200
