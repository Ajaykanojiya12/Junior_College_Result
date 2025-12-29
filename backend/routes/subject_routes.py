# routes/subject_routes.py

from flask import Blueprint, jsonify
from models import Subject

subject_bp = Blueprint("subjects", __name__)

@subject_bp.route("/subjects", methods=["GET"])
def list_subjects():
    subjects = Subject.query.filter_by(active=True).all()
    return jsonify([
        {
            "subject_id": s.subject_id,
            "subject_code": s.subject_code,
            "subject_name": s.subject_name
        }
        for s in subjects
    ]), 200
