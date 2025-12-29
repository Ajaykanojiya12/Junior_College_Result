# backend/routes/admin_routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from app import db
from typing import Any, Dict
from auth import generate_token
from models import (
    Teacher,
    Subject,
    Student,
    TeacherSubjectAllocation
)
from schemas import StudentSchema
from auth import token_required
from decorators import admin_required
from services.result_service import generate_results_for_division
from models import Result, Subject, Mark
from flask import send_file
from io import BytesIO
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except Exception:
    letter = None
    canvas = None

from werkzeug.security import generate_password_hash


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

student_schema = StudentSchema()


# ======================================================
# 1️⃣ Add Student
# ======================================================
@admin_bp.route("/students", methods=["POST"])
@token_required
@admin_required
def add_student(user_id=None, user_type=None):
    """
    Add a new student (admin only)
    """
    data: Dict[str, Any] = student_schema.load(request.json or {})

    student = Student(**data)

    try:
        db.session.add(student)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Student already exists"}, 409

    return {"message": "Student added successfully"}, 201


# ======================================================
# 2️⃣ Get Students (by division)
# ======================================================
@admin_bp.route("/students", methods=["GET"])
@token_required
@admin_required
def list_students(user_id=None, user_type=None):
    """
    List students by division (admin only)
    """
    division = request.args.get("division")
    if not division:
        return {"error": "division is required"}, 400

    students = (
        Student.query
        .filter_by(division=division)
        .order_by(Student.roll_no)
        .all()
    )

    return jsonify([
        {
            "roll_no": s.roll_no,
            "name": s.name,
            "division": s.division,
            "optional_subject": s.optional_subject,
            "optional_subject_2": s.optional_subject_2
        }
        for s in students
    ]), 200


# ======================================================
# 3️⃣ Assign Teacher to Subject + Division
# ======================================================
@admin_bp.route("/allocations", methods=["POST"])
@token_required
@admin_required
def allocate_teacher(user_id=None, user_type=None):
    """
    Assign teacher to subject & division (admin only)
    """
    data: Dict[str, Any] = (request.json or {})
    teacher_id = data.get("teacher_id")
    subject_id = data.get("subject_id")
    division = data.get("division")

    if not teacher_id or not subject_id or not division:
        return {"error": "teacher_id, subject_id, division required"}, 400

    allocation = TeacherSubjectAllocation(
        teacher_id=teacher_id,
        subject_id=subject_id,
        division=division
    )

    try:
        db.session.add(allocation)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Allocation already exists"}, 409

    return {"message": "Teacher allocated successfully"}, 201


# ======================================================
# 4️⃣ View Allocations
# ======================================================
@admin_bp.route("/allocations", methods=["GET"])
@token_required
@admin_required
def list_allocations(user_id=None, user_type=None):
    """
    List all teacher-subject allocations (admin only)
    """
    allocations = TeacherSubjectAllocation.query.all()

    return jsonify([
        {
            "teacher_id": a.teacher_id,
            "subject_id": a.subject_id,
            "division": a.division
        }
        for a in allocations
    ]), 200


# ======================================================
# 5️⃣ Generate Results (per division)
# ======================================================
@admin_bp.route("/results/generate", methods=["POST"])
@token_required
@admin_required
def generate_results(user_id=None, user_type=None):
    """
    Generate / update results for a division (admin only)
    """
    division = request.json.get("division")
    if not division:
        return {"error": "division is required"}, 400

    generate_results_for_division(division)

    return {"message": f"Results generated for division {division}"}, 200


# ======================================================
# 6️⃣ Get available divisions (admin)
# ======================================================
@admin_bp.route("/divisions", methods=["GET"])
@token_required
@admin_required
def list_divisions(user_id=None, user_type=None):
    divisions = db.session.query(Student.division).distinct().all()
    divs = [d[0] for d in divisions]
    return jsonify(divs), 200


# ======================================================
# 7️⃣ Fetch results by division or roll_no (admin)
# Query params: division OR roll_no (+ optional division)
# ======================================================
@admin_bp.route("/results", methods=["GET"])
@token_required
@admin_required
def fetch_results(user_id=None, user_type=None):
    roll_no = request.args.get("roll_no")
    division = request.args.get("division")

    # If roll_no provided, optionally restrict by division
    if roll_no:
        students = Student.query.filter_by(roll_no=roll_no)
        if division:
            students = students.filter_by(division=division)
        students = students.all()
        if not students:
            return {"error": "Student not found"}, 404

        # Ensure results are generated for involved divisions
        for s in students:
            try:
                generate_results_for_division(s.division)
            except Exception:
                pass

        # Build rows for each matching student (usually one)
        rows = []
        for s in students:
            result = Result.query.filter_by(roll_no=s.roll_no, division=s.division).first()
            # If result is missing, fall back to available Marks so UI can show partial data
            marks = Mark.query.filter_by(roll_no=s.roll_no, division=s.division).all()
            subjects_map = {sub.subject_id: sub.subject_code for sub in Subject.query.all()}
            mark_map = {}
            for m in marks:
                code = subjects_map.get(m.subject_id)
                if code:
                    mark_map[code] = m

            subject_entries = []
            total_avg = 0
            total_grace = 0

            for code, field in {"ENG": "eng", "ECO": "eco", "BK": "bk", "OC": "oc"}.items():
                if result:
                    avg = getattr(result, f"{field}_avg", None)
                    grace = getattr(result, f"{field}_grace", 0) or 0
                else:
                    m = mark_map.get(code)
                    avg = m.annual if m and m.annual is not None else None
                    grace = m.grace if m and m.grace is not None else 0

                final = None
                if avg is not None:
                    final = (avg or 0) + (grace or 0)
                    total_avg += avg or 0
                    total_grace += grace or 0

                # include detailed mark breakdown if available
                m = mark_map.get(code)
                mark_detail = None
                if m:
                    mark_detail = {
                        "mark_id": m.mark_id,
                        "unit1": m.unit1,
                        "unit2": m.unit2,
                        "term": m.term,
                        "annual": m.annual,
                        "tot": m.tot,
                        "sub_avg": m.sub_avg,
                        "grace": m.grace,
                    }

                subject_entries.append({
                    "code": code,
                    "avg": avg,
                    "grace": grace,
                    "final": final,
                    "mark": mark_detail
                })

            # EVS and PE (grade-only) — prefer grades from Result, fall back to marks
            if result and getattr(result, 'evs_grade', None) is not None:
                subject_entries.append({"code": "EVS", "grade": result.evs_grade})
            else:
                m = mark_map.get('EVS')
                if m and m.annual is not None:
                    a = m.annual
                    grade = None
                    if a >= 75:
                        grade = 'A+'
                    elif a >= 60:
                        grade = 'A'
                    elif a >= 50:
                        grade = 'B'
                    elif a >= 35:
                        grade = 'C'
                    else:
                        grade = 'F'
                    subject_entries.append({"code": "EVS", "grade": grade, "mark": {"annual": m.annual, "mark_id": m.mark_id, "unit1": m.unit1, "unit2": m.unit2, "term": m.term, "tot": m.tot, "sub_avg": m.sub_avg, "grace": m.grace}})

            if result and getattr(result, 'pe_grade', None) is not None:
                subject_entries.append({"code": "PE", "grade": result.pe_grade})
            else:
                m = mark_map.get('PE')
                if m and m.annual is not None:
                    a = m.annual
                    grade = None
                    if a >= 75:
                        grade = 'A+'
                    elif a >= 60:
                        grade = 'A'
                    elif a >= 50:
                        grade = 'B'
                    elif a >= 35:
                        grade = 'C'
                    else:
                        grade = 'F'
                    subject_entries.append({"code": "PE", "grade": grade, "mark": {"annual": m.annual, "mark_id": m.mark_id, "unit1": m.unit1, "unit2": m.unit2, "term": m.term, "tot": m.tot, "sub_avg": m.sub_avg, "grace": m.grace}})

            for code, field in {"HINDI": "hindi", "IT": "it", "MATHS": "maths", "SP": "sp"}.items():
                include = False
                if code in ("HINDI", "IT") and s.optional_subject == code:
                    include = True
                if code in ("MATHS", "SP") and s.optional_subject_2 == code:
                    include = True
                if include:
                    avg = getattr(result, f"{field}_avg", None) if result else None
                    grace = getattr(result, f"{field}_grace", 0) if result else 0
                    final = None
                    if avg is not None:
                        final = (avg or 0) + (grace or 0)
                        total_avg += avg or 0
                        total_grace += grace or 0

                    # include detailed mark breakdown if available
                    m = mark_map.get(code)
                    mark_detail = None
                    if m:
                        mark_detail = {
                            "mark_id": m.mark_id,
                            "unit1": m.unit1,
                            "unit2": m.unit2,
                            "term": m.term,
                            "annual": m.annual,
                            "tot": m.tot,
                            "sub_avg": m.sub_avg,
                            "grace": m.grace,
                        }

                    subject_entries.append({
                        "code": code,
                        "avg": avg,
                        "grace": grace,
                        "final": final,
                        "mark": mark_detail
                    })

            final_total = None
            if subject_entries:
                # Only show final_total if percentage exists (i.e., result fully computed)
                perc = getattr(result, "percentage", None) if result else None
                if perc is not None:
                    final_total = total_avg + total_grace

            rows.append({
                "roll_no": s.roll_no,
                "name": s.name,
                "division": s.division,
                "subjects": subject_entries,
                "total_avg": round(total_avg, 2),
                "total_grace": round(total_grace, 2),
                "final_total": round(final_total, 2) if final_total is not None else None,
                "percentage": getattr(result, "percentage", None) if result else None,
            })

        # If caller requested a single roll_no, return single object
        if len(rows) == 1:
            return jsonify(rows[0]), 200
        return jsonify(rows), 200

    # Else, require division
    if not division:
        return {"error": "division or roll_no is required"}, 400

    # regenerate results for the division
    try:
        generate_results_for_division(division)
    except Exception:
        pass

    # Build rows for entire division
    students = Student.query.filter_by(division=division).order_by(Student.roll_no).all()
    rows = []
    for idx, s in enumerate(students, start=1):
        result = Result.query.filter_by(roll_no=s.roll_no, division=s.division).first()
        # Prepare mark map to allow partial display when Result row missing
        marks = Mark.query.filter_by(roll_no=s.roll_no, division=s.division).all()
        subjects_map = {sub.subject_id: sub.subject_code for sub in Subject.query.all()}
        mark_map = {}
        for m in marks:
            code = subjects_map.get(m.subject_id)
            if code:
                mark_map[code] = m

        subject_entries = []
        total_avg = 0
        total_grace = 0

        for code, field in {"ENG": "eng", "ECO": "eco", "BK": "bk", "OC": "oc"}.items():
            if result:
                avg = getattr(result, f"{field}_avg", None)
                grace = getattr(result, f"{field}_grace", 0) or 0
            else:
                m = mark_map.get(code)
                avg = m.annual if m and m.annual is not None else None
                grace = m.grace if m and m.grace is not None else 0

            final = None
            if avg is not None:
                final = (avg or 0) + (grace or 0)
                total_avg += avg or 0
                total_grace += grace or 0

            # include mark detail when present
            m = mark_map.get(code)
            mark_detail = None
            if m:
                mark_detail = {
                    "mark_id": m.mark_id,
                    "unit1": m.unit1,
                    "unit2": m.unit2,
                    "term": m.term,
                    "annual": m.annual,
                    "tot": m.tot,
                    "sub_avg": m.sub_avg,
                    "grace": m.grace,
                }

            subject_entries.append({"code": code, "avg": avg, "grace": grace, "final": final, "mark": mark_detail})

        for code, field in {"HINDI": "hindi", "IT": "it", "MATHS": "maths", "SP": "sp"}.items():
            include = False
            if code in ("HINDI", "IT") and s.optional_subject == code:
                include = True
            if code in ("MATHS", "SP") and s.optional_subject_2 == code:
                include = True

            if include:
                if result:
                    avg = getattr(result, f"{field}_avg", None)
                    grace = getattr(result, f"{field}_grace", 0) or 0
                else:
                    m = mark_map.get(code)
                    avg = m.annual if m and m.annual is not None else None
                    grace = m.grace if m and m.grace is not None else 0
                final = None
                if avg is not None:
                    final = (avg or 0) + (grace or 0)
                    total_avg += avg or 0
                    total_grace += grace or 0

                subject_entries.append({"code": code, "avg": avg, "grace": grace, "final": final})
        # EVS and PE (grade-only) — append once after optional subjects
        if result and getattr(result, 'evs_grade', None) is not None:
            subject_entries.append({"code": "EVS", "grade": result.evs_grade})
        else:
            m = mark_map.get('EVS')
            if m and m.annual is not None:
                a = m.annual
                grade = None
                if a >= 75:
                    grade = 'A+'
                elif a >= 60:
                    grade = 'A'
                elif a >= 50:
                    grade = 'B'
                elif a >= 35:
                    grade = 'C'
                else:
                    grade = 'F'
                subject_entries.append({"code": "EVS", "grade": grade, "mark": {"annual": m.annual, "mark_id": m.mark_id, "unit1": m.unit1, "unit2": m.unit2, "term": m.term, "tot": m.tot, "sub_avg": m.sub_avg, "grace": m.grace}})

        if result and getattr(result, 'pe_grade', None) is not None:
            subject_entries.append({"code": "PE", "grade": result.pe_grade})
        else:
            m = mark_map.get('PE')
            if m and m.annual is not None:
                a = m.annual
                grade = None
                if a >= 75:
                    grade = 'A+'
                elif a >= 60:
                    grade = 'A'
                elif a >= 50:
                    grade = 'B'
                elif a >= 35:
                    grade = 'C'
                else:
                    grade = 'F'
                subject_entries.append({"code": "PE", "grade": grade, "mark": {"annual": m.annual, "mark_id": m.mark_id, "unit1": m.unit1, "unit2": m.unit2, "term": m.term, "tot": m.tot, "sub_avg": m.sub_avg, "grace": m.grace}})

        final_total = None
        if subject_entries:
            perc = getattr(result, "percentage", None) if result else None
            if perc is not None:
                final_total = total_avg + total_grace

        rows.append({
            "seq": idx,
            "roll_no": s.roll_no,
            "name": s.name,
            "subjects": subject_entries,
            "total_avg": round(total_avg, 2),
            "total_grace": round(total_grace, 2),
            "final_total": round(final_total, 2) if final_total is not None else None,
            "percentage": getattr(result, "percentage", None) if result else None,
        })

    return jsonify(rows), 200


# ======================================================
# Download student marksheet PDF (admin only)
# ======================================================
@admin_bp.route('/students/<string:roll_no>/pdf', methods=['GET'])
@token_required
@admin_required
def student_marksheet_pdf(roll_no, user_id=None, user_type=None):
    division = request.args.get('division')
    if not division:
        return {"error": "division is required"}, 400

    # ensure results are up-to-date
    try:
        generate_results_for_division(division)
    except Exception:
        pass

    res = Result.query.filter_by(roll_no=roll_no, division=division).first()
    if not res:
        return {"error": "Result not found"}, 404

    if canvas is None:
        return {"error": "reportlab not installed on server. Install reportlab in requirements."}, 501

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Header
    c.setFont('Helvetica-Bold', 16)
    c.drawString(40, height - 50, 'Official Marksheet')
    c.setFont('Helvetica', 12)
    c.drawString(40, height - 70, f'Name: {res.name}  |  Roll: {res.roll_no}  |  Division: {res.division}')

    # Table header
    y = height - 110
    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, 'Subject')
    c.drawString(260, y, 'Annual')
    c.drawString(360, y, 'Grace')
    c.drawString(460, y, 'Final')
    c.setFont('Helvetica', 11)
    y -= 18

    # iterate known subjects and map to result fields
    mapping = [
        ('ENG', 'eng_avg', 'eng_grace'),
        ('ECO', 'eco_avg', 'eco_grace'),
        ('BK', 'bk_avg', 'bk_grace'),
        ('OC', 'oc_avg', 'oc_grace'),
        ('HINDI', 'hindi_avg', 'hindi_grace'),
        ('IT', 'it_avg', 'it_grace'),
        ('MATHS', 'maths_avg', 'maths_grace'),
        ('SP', 'sp_avg', 'sp_grace')
    ]

    total = 0
    for code, avg_field, grace_field in mapping:
        avg = getattr(res, avg_field, None)
        grace = getattr(res, grace_field, 0) or 0
        if avg is None:
            continue
        final = (avg or 0) + (grace or 0)
        c.drawString(40, y, code)
        c.drawRightString(320, y, f'{round(avg,2)}')
        c.drawRightString(420, y, f'{round(grace,2)}')
        c.drawRightString(520, y, f'{round(final,2)}')
        total += final
        y -= 16

    y -= 8
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, f'Total: {round(res.percentage * (len(mapping) / len(mapping)),2) if res.percentage is not None else "-"}')
    c.drawRightString(520, y, f'Percentage: {res.percentage or "-"}')

    c.showPage()
    c.save()
    buf.seek(0)

    return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=f'{roll_no}_marksheet.pdf')



# ======================================================
# ADMIN – TEACHERS CRUD
# ======================================================

@admin_bp.route("/teachers", methods=["GET"])
@token_required
def list_teachers(user_id=None, user_type=None):
    if user_type != "ADMIN":
        return {"error": "Unauthorized"}, 403

    teachers = Teacher.query.all()
    return jsonify([
        {
            "teacher_id": t.teacher_id,
            "name": t.name,
            "userid": t.userid,
            "email": t.email,
            "active": t.active,
            "role": t.role
        }
        for t in teachers
    ]), 200


@admin_bp.route("/teachers", methods=["POST"])
@token_required
def add_teacher(user_id=None, user_type=None):
    if user_type != "ADMIN":
        return {"error": "Unauthorized"}, 403

    data = request.json
    required = ["name", "userid", "password"]
    if not all(k in data for k in required):
        return {"error": "Missing required fields"}, 400

    if Teacher.query.filter_by(userid=data["userid"]).first():
        return {"error": "UserID already exists"}, 409

    teacher = Teacher(
        name=data["name"],
        userid=data["userid"],
        email=data.get("email"),
        role=data.get("role", "TEACHER"),
        active=True,
        password_hash=generate_password_hash(data["password"])
    )

    db.session.add(teacher)
    db.session.commit()

    return {"message": "Teacher added"}, 201


@admin_bp.route("/teachers/<int:teacher_id>", methods=["PUT"])
@token_required
def update_teacher(teacher_id, user_id=None, user_type=None):
    if user_type != "ADMIN":
        return {"error": "Unauthorized"}, 403

    teacher = Teacher.query.get_or_404(teacher_id)
    data = request.json

    teacher.name = data.get("name", teacher.name)
    teacher.userid = data.get("userid", teacher.userid)
    teacher.email = data.get("email", teacher.email)
    teacher.active = data.get("active", teacher.active)

    if data.get("password"):
        teacher.password_hash = generate_password_hash(data["password"])

    db.session.commit()
    return {"message": "Teacher updated"}, 200


@admin_bp.route("/teachers/<int:teacher_id>", methods=["DELETE"])
@token_required
def delete_teacher(teacher_id, user_id=None, user_type=None):
    if user_type != "ADMIN":
        return {"error": "Unauthorized"}, 403

    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()

    return {"message": "Teacher deleted"}, 200


# ======================================================
# ADMIN LOGIN (tests expect /admin/login)
# ======================================================
@admin_bp.route("/login", methods=["POST"])
def admin_login():
    data = request.json or {}
    userid = data.get("userid")
    password = data.get("password")

    if not userid or not password:
        return {"error": "userid and password required"}, 400

    admin = None
    from models import Admin
    admin = Admin.query.filter_by(username=userid, active=True).first()
    if not admin:
        return {"error": "Invalid credentials"}, 401

    # Admin passwords are hashed with werkzeug.generate_password_hash
    from werkzeug.security import check_password_hash
    if not check_password_hash(admin.password_hash, password):
        return {"error": "Invalid credentials"}, 401

    token = generate_token(admin.admin_id, "ADMIN")
    # Return role in lowercase for consistency with client/tests
    return {"token": token, "role": "admin"}, 200


# ======================================================
# ADMIN IMPERSONATE TEACHER (open teacher panel without logging out)
# ======================================================
@admin_bp.route('/teachers/<int:teacher_id>/impersonate', methods=['POST'])
@token_required
@admin_required
def impersonate_teacher(teacher_id, user_id=None, user_type=None):
    """
    Generate a short-lived token for a teacher so an admin can open
    the teacher panel without logging out (impersonation).
    """
    teacher = Teacher.query.get(teacher_id)
    if not teacher or not teacher.active:
        return {"error": "Teacher not found or inactive"}, 404

    # Issue token with TEACHER role
    token = generate_token(teacher.teacher_id, "TEACHER", expires_hours=2)

    return {
        "token": token,
        "teacher": {
            "teacher_id": teacher.teacher_id,
            "name": teacher.name,
            "userid": teacher.userid,
            "email": teacher.email,
        }
    }, 200
